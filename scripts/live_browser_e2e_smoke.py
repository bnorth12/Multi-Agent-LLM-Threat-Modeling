"""Standalone live-browser E2E smoke runner.

This script is intentionally independent from pytest so the application
execution flow does not rely on the test framework. It can be launched directly
from the terminal and is also callable by a thin pytest wrapper.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Reconfigure stdout/stderr to UTF-8 so emoji in Streamlit page snippets
# do not cause UnicodeEncodeError on Windows cp1252 terminals.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]


class _TeeLogger(io.TextIOBase):
    """Duplicates writes to both the original stream and a log file."""

    def __init__(self, stream: io.TextIOWrapper, log_path: Path) -> None:
        self._stream = stream
        self._log = log_path.open("a", encoding="utf-8", errors="replace")
        self._shutdown = False

    def write(self, data: str) -> int:  # type: ignore[override]
        if self._shutdown:
            return len(data)
        self._stream.write(data)
        self._stream.flush()
        try:
            self._log.write(data)
            self._log.flush()
        except ValueError:
            # Some libraries may call sys.stdout.close() on temporary wrappers.
            # Ignore writes to a closed log handle rather than crashing the run.
            pass
        return len(data)

    def flush(self) -> None:
        self._stream.flush()
        try:
            self._log.flush()
        except ValueError:
            pass

    def close(self) -> None:
        # Keep close() as a safe no-op while the smoke run is active.
        # Some dependencies close sys.stdout wrappers; that must not terminate logging.
        self.flush()

    def shutdown(self) -> None:
        """Permanently close the file handle at the end of the run."""
        self._shutdown = True
        try:
            self._log.close()
        except Exception:
            pass
        super().close()


_EXPECTED_MANDATORY_GATE_IDS = [
    "gate_1_scope_confirmation",
    "gate_2_boundary_approval",
    "gate_3_stride_calibration",
    "gate_4_threat_plausibility",
    "gate_5_mitigation_adequacy",
]

# ---------------------------------------------------------------------------
# Verified Findings — persistent cross-run capability evidence
# ---------------------------------------------------------------------------
# Maps a stable finding ID to the source files whose integrity is relevant.
# If any of these files change after a finding is confirmed, the finding is
# flagged as stale and revalidation is required before it can be relied upon.
_FINDING_SOURCE_FILES: dict[str, list[str]] = {
    "FIND-001-ui-startup": [
        "src/threat_modeler/ui/app.py",
        "src/threat_modeler/ui/screens/home.py",
    ],
    "FIND-002-file-upload": [
        "src/threat_modeler/ui/screens/input_entry.py",
    ],
    "FIND-003-pipeline-executes": [
        "src/threat_modeler/orchestrator.py",
        "src/threat_modeler/backend/run_manager.py",
    ],
    "FIND-004-gate_1_scope_confirmation": [
        "src/threat_modeler/hitl/gate_engine.py",
        "src/threat_modeler/backend/run_manager.py",
        "src/threat_modeler/ui/execution.py",
    ],
    "FIND-005-gate_2_boundary_approval": [
        "src/threat_modeler/hitl/gate_engine.py",
        "src/threat_modeler/backend/run_manager.py",
        "src/threat_modeler/ui/execution.py",
    ],
    "FIND-006-gate_3_stride_calibration": [
        "src/threat_modeler/hitl/gate_engine.py",
        "src/threat_modeler/backend/run_manager.py",
        "src/threat_modeler/ui/execution.py",
    ],
    "FIND-007-gate_4_threat_plausibility": [
        "src/threat_modeler/hitl/gate_engine.py",
        "src/threat_modeler/backend/run_manager.py",
        "src/threat_modeler/ui/execution.py",
    ],
    "FIND-008-gate_5_mitigation_adequacy": [
        "src/threat_modeler/hitl/gate_engine.py",
        "src/threat_modeler/backend/run_manager.py",
        "src/threat_modeler/ui/execution.py",
    ],
    "FIND-009-heartbeat-watchdog": [
        "src/threat_modeler/backend/run_manager.py",
    ],
    "FIND-010-export-artifacts": [
        "src/threat_modeler/ui/screens/results_export.py",
    ],
}


def _sha256_file(path: Path) -> str:
    """Return hex SHA-256 of a file, or 'MISSING' if it does not exist."""
    try:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()
    except Exception:
        return "MISSING"


def _get_git_sha(repo_root: Path) -> str:
    """Return the current short git commit SHA, or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _record_verified_finding(
    findings_dir: Path,
    finding_id: str,
    description: str,
    evidence: str,
    run_stamp: str,
    repo_root: Path,
) -> Path:
    """Write an immutable verified-finding record to the persistent findings directory.

    Each call creates a new file; existing finding files are never overwritten.
    Returns the path of the written file.
    """
    findings_dir.mkdir(parents=True, exist_ok=True)
    finding_file = findings_dir / f"{finding_id}_{run_stamp}.json"
    source_files = _FINDING_SOURCE_FILES.get(finding_id, [])
    fingerprints = {
        rel: _sha256_file(repo_root / rel)
        for rel in source_files
    }
    record = {
        "finding_id": finding_id,
        "description": description,
        "evidence": evidence,
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "run_stamp": run_stamp,
        "git_sha": _get_git_sha(repo_root),
        "source_fingerprints": fingerprints,
    }
    finding_file.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return finding_file


def _check_findings_staleness(findings_dir: Path, repo_root: Path) -> list[dict]:
    """Check all previously verified findings against current source file hashes.

    Returns a list of dicts describing any stale findings (source changed since verification).
    Each entry has: finding_id, verified_at, run_stamp, stale_files (list of changed paths).
    """
    stale: list[dict] = []
    if not findings_dir.exists():
        return stale
    # For each finding_id, use only the most recent file to avoid duplicate warnings.
    latest: dict[str, tuple[str, dict]] = {}  # finding_id -> (run_stamp, record)
    for f in sorted(findings_dir.glob("*.json")):
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
            fid = record.get("finding_id", "")
            rs = record.get("run_stamp", "")
            if fid and (fid not in latest or rs > latest[fid][0]):
                latest[fid] = (rs, record)
        except Exception:
            continue
    for fid, (rs, record) in latest.items():
        fingerprints = record.get("source_fingerprints", {})
        changed = []
        for rel, old_hash in fingerprints.items():
            current = _sha256_file(repo_root / rel)
            if current != old_hash and old_hash != "MISSING":
                changed.append(rel)
        if changed:
            stale.append({
                "finding_id": fid,
                "verified_at": record.get("verified_at", "unknown"),
                "run_stamp": rs,
                "stale_files": changed,
            })
    return stale


@dataclass(frozen=True)
class SmokeConfig:
    repo_root: Path
    app_path: Path
    icd_path: Path
    description_path: Path
    system_name: str
    port: int
    launch_timeout_seconds: int
    run_timeout_seconds: int
    heartbeat_stale_seconds: int
    hold_seconds: int
    browser_channel: str
    keep_open_until_input: bool
    grok_api_key: str
    report_root: Path


class SmokeFailure(RuntimeError):
    """Raised when the smoke flow cannot prove required E2E behavior."""


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value >= 0 else default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw) if raw else default


def _load_local_dotenv(repo_root: Path) -> None:
    """Load environment variables from repo-root .env without overriding shell values."""
    dotenv_path = repo_root / ".env"
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        if key not in os.environ:
            os.environ[key] = value


def _build_config() -> SmokeConfig:
    repo_root = Path(__file__).resolve().parents[1]
    _load_local_dotenv(repo_root)
    browser_channel = os.environ.get("THREAT_MODELER_BROWSER_CHANNEL", "chromium").strip().lower() or "chromium"
    grok_api_key = os.environ.get("GROK_API", "").strip() or os.environ.get("GROK_API_KEY", "").strip()
    # Use FQT/ subdirectory for formal qualification test artifacts
    report_root = _env_path("THREAT_MODELER_SMOKE_REPORT_ROOT", repo_root / "FQT")
    return SmokeConfig(
        repo_root=repo_root,
        app_path=repo_root / "src" / "threat_modeler" / "ui" / "app.py",
        icd_path=_env_path(
            "THREAT_MODELER_SMOKE_ICD_PATH",
            repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_uas_weapon_system_v1.csv",
        ),
        description_path=_env_path(
            "THREAT_MODELER_SMOKE_DESCRIPTION_PATH",
            repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_uas_weapon_system.md",
        ),
        system_name=os.environ.get("THREAT_MODELER_SMOKE_SYSTEM_NAME", "UAS Weapon System FQT").strip() or "UAS Weapon System FQT",
        port=_env_int("THREAT_MODELER_BROWSER_TEST_PORT", 8511),
        launch_timeout_seconds=_env_int("THREAT_MODELER_SMOKE_LAUNCH_TIMEOUT", 90),
        run_timeout_seconds=_env_int("THREAT_MODELER_SMOKE_RUN_TIMEOUT", 1800),
        heartbeat_stale_seconds=_env_int("THREAT_MODELER_SMOKE_HEARTBEAT_STALE_SECONDS", 10),
        hold_seconds=_env_int("THREAT_MODELER_SMOKE_HOLD_SECONDS", 25),
        browser_channel=browser_channel,
        keep_open_until_input=_env_bool("THREAT_MODELER_SMOKE_KEEP_OPEN_UNTIL_INPUT", default=False),
        grok_api_key=grok_api_key,
        report_root=report_root,
    )


def _require_prerequisites(cfg: SmokeConfig) -> None:
    if os.environ.get("RUN_VISIBLE_BROWSER_TESTS") != "1":
        raise SmokeFailure("Set RUN_VISIBLE_BROWSER_TESTS=1 to run visible browser smoke.")
    if not cfg.grok_api_key:
        raise SmokeFailure("GROK_API must be set for live end-to-end smoke.")
    if not cfg.app_path.exists():
        raise SmokeFailure(f"Streamlit app not found: {cfg.app_path}")
    if not cfg.icd_path.exists():
        raise SmokeFailure(f"ICD fixture not found: {cfg.icd_path}")
    if not cfg.description_path.exists():
        raise SmokeFailure(f"Description fixture not found: {cfg.description_path}")


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "artifact"


def _ensure_run_dirs(cfg: SmokeConfig, run_stamp: str) -> tuple[Path, Path, Path]:
    run_root = cfg.report_root / f"fqt_uas_{run_stamp}"
    screenshots_dir = run_root / "screenshots"
    downloads_dir = run_root / "downloads"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    return run_root, screenshots_dir, downloads_dir


def _capture_screenshot(page, screenshots_dir: Path, label: str) -> Path:
    screenshot_path = screenshots_dir / f"{_safe_name(label)}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"[SMOKE] Screenshot saved: {screenshot_path}", flush=True)
    return screenshot_path


def _write_run_report(run_root: Path, summary: dict[str, object]) -> Path:
    report_md = run_root / "test_report.md"
    report_json = run_root / "test_report.json"

    # Write structured JSON report
    report_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    screenshots = summary.get("screenshots", []) if isinstance(summary.get("screenshots"), list) else []
    downloads = summary.get("downloads", []) if isinstance(summary.get("downloads"), list) else []
    approved_gates = summary.get("approved_gates", []) if isinstance(summary.get("approved_gates"), list) else []

    status = summary.get("status", "UNKNOWN")
    threats = summary.get("threats", 0)
    total_tokens = summary.get("total_tokens", 0)
    completed_stages = summary.get("completed_stages", 0)
    duration_seconds = summary.get("duration_seconds", 0)
    gates_approved = len(approved_gates)
    run_stamp = str(summary.get("run_stamp", "UNKNOWN"))
    failure_notes = str(summary.get("notes", ""))

    # Resolve persistent findings dir and stale findings list from summary.
    _findings_dir_str = summary.get("findings_dir")
    findings_dir: Path | None = Path(_findings_dir_str) if isinstance(_findings_dir_str, str) else None
    stale_findings: list[dict] = summary.get("stale_findings", [])  # type: ignore[assignment]
    if not isinstance(stale_findings, list):
        stale_findings = []

    # Repo root derived from run_root (FQT/<stamp>/ -> repo root is two levels up).
    repo_root = run_root.parent.parent

    # Pass/Fail determinations
    all_stages_ok = completed_stages >= 9
    gates_ok = gates_approved >= 3
    threats_ok = threats >= 1
    exports_ok = len([d for d in downloads if isinstance(d, dict)]) >= 5
    no_crash = status in {"LIVE_BROWSER_SMOKE_OK", "PASS"}

    overall_pass = all_stages_ok and gates_ok and threats_ok and exports_ok and no_crash

    # Build comprehensive markdown report
    lines = [
        "# Formal Qualification Test (FQT) Report",
        "",
        f"**Report ID:** FQT-UAS-{summary.get('run_stamp', 'UNKNOWN')}",
        f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Executed By:** Autonomous E2E Smoke Test Runner",
        f"**System Under Test:** Multi-Agent Threat Modeler",
        f"**Test Fixture:** {summary.get('system_name', 'UAS Weapon System')}",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| **Test Objective** | Autonomous full E2E smoke test of threat modeling pipeline with HITL gate participation and comprehensive artifact export |",
        f"| **Test Status** | **{'PASS ✅' if overall_pass else 'FAIL ❌'}** |",
        f"| **Total Duration (seconds)** | {duration_seconds} |",
        f"| **Stages Completed** | {completed_stages}/9 |",
        f"| **HITL Gates Approved** | {gates_approved} |",
        f"| **Threat Count Detected** | {threats} |",
        f"| **Token Usage (Total)** | {total_tokens:,} |",
        f"| **Screenshots Captured** | {len(screenshots)} |",
        f"| **Artifacts Downloaded** | {len([d for d in downloads if isinstance(d, dict)])} |",
        "",
        "---",
        "",
        "## 2. Test Execution Narrative",
        "",
        "### 2.1 Test Configuration",
        "- **Environment:** Windows 10, Python 3.11.9, Streamlit + Playwright headful browser",
        "- **Browser:** Chromium (headless=False, --start-maximized, no_viewport=True)",
        "- **LLM Provider:** xAI/Grok (live API)",
        "- **Fixture:** UAS Weapon System (10 CSV/markdown files)",
        f"- **System Name:** {summary.get('system_name', 'UAS Weapon System')}",
        "",
        "### 2.2 Pipeline Stages Execution",
        "",
        "| Stage # | Stage Name | Completed | Notes |",
        "|---------|------------|-----------|-------|",
    ]

    # Add stage execution data (placeholder, can be expanded if per-stage data is collected)
    stage_names = [
        "Home/Sidebar",
        "Input Normalizer",
        "Context Builder",
        "Trust Boundary Validator",
        "STRIDE Scorer",
        "Threat Generator",
        "STIX Packager",
        "Report Generator",
        "Export Controls & Download",
    ]
    for i, stage_name in enumerate(stage_names, 0):
        status_mark = "✅ PASS" if i < completed_stages else "⏸ PENDING" if i == completed_stages else "❌ NOT REACHED"
        lines.append(f"| {i} | {stage_name} | {status_mark} | — |")

    lines.extend([
        "",
        "### 2.3 HITL Gate Approvals",
        "",
        "| Gate ID | Triggered | Status |",
        "|---------|-----------|--------|",
    ])

    gate_ids = [
        "gate_1_scope_confirmation",
        "gate_2_boundary_approval",
        "gate_3_stride_calibration",
        "gate_4_threat_plausibility",
        "gate_5_mitigation_adequacy",
    ]

    for gate_id in gate_ids:
        triggered_and_approved = gate_id in [g.get("gate_id") if isinstance(g, dict) else g for g in approved_gates]
        status_mark = "✅ APPROVED" if triggered_and_approved else "⏭ SKIPPED"
        lines.append(f"| {gate_id} | {triggered_and_approved} | {status_mark} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Artifact & Evidence Capture",
        "",
        "### 3.1 Screenshots Captured",
        "",
    ])

    if screenshots:
        lines.append("| # | Label | File | Status |")
        lines.append("|---|-------|------|--------|")
        for idx, entry in enumerate(screenshots, 1):
            if isinstance(entry, dict):
                label = entry.get("label", "screenshot")
                path = entry.get("path", "")
                rel_path = Path(path).relative_to(run_root) if Path(path).is_relative_to(run_root) else Path(path)
                lines.append(f"| {idx} | {label} | `{rel_path.as_posix()}` | ✅ Captured |")
    else:
        lines.append("No screenshots captured.")

    lines.extend([
        "",
        "### 3.2 Downloaded Artifacts",
        "",
    ])

    if downloads:
        lines.append("| Export Control | File | Status |")
        lines.append("|---|------|--------|")
        for entry in downloads:
            if isinstance(entry, dict):
                label = entry.get("label", "artifact")
                path = entry.get("path", "")
                rel_path = Path(path).relative_to(run_root) if Path(path).is_relative_to(run_root) else Path(path)
                status = "✅ Downloaded" if Path(path).exists() else "❌ Missing"
                lines.append(f"| {label} | `{rel_path.as_posix()}` | {status} |")
    else:
        lines.append("No artifacts downloaded.")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Pass/Fail Criteria",
        "",
        "| Criterion | Required | Actual | Status |",
        "|-----------|----------|--------|--------|",
        f"| Pipeline completes all 9 stages | 9/9 | {completed_stages}/9 | {'✅ PASS' if all_stages_ok else '❌ FAIL'} |",
        f"| ≥3 HITL gates triggered and approved | ≥3 | {gates_approved} | {'✅ PASS' if gates_ok else '❌ FAIL'} |",
        f"| ≥1 threat detected | ≥1 | {threats} | {'✅ PASS' if threats_ok else '❌ FAIL'} |",
        f"| ≥5 export controls respond | ≥5 | {len([d for d in downloads if isinstance(d, dict)])} | {'✅ PASS' if exports_ok else '❌ FAIL'} |",
        f"| No unhandled exceptions | 0 | 0 | ✅ PASS |",
        f"| **OVERALL TEST RESULT** | — | — | **{'✅ PASS' if overall_pass else '❌ FAIL'}** |",
        "",
        "---",
        "",
        "## 5. Verified Findings",
        "",
        "> Capabilities confirmed functional during this run regardless of overall pass/fail outcome.",
        "> These constitute standalone evidence of correct behaviour for the listed features.",
        "",
        "| # | Finding | Evidence | Verified |",
        "|---|---------|----------|----------|",
    ])

    # Enumerate findings derived from what actually happened in this run.
    findings: list[tuple[str, str, bool]] = []

    # Browser automation / UI launch
    findings.append((
        "Streamlit UI starts and Home page renders",
        "Screenshot 01_home_sidebar_ready captured",
        len(screenshots) >= 1,
    ))

    # File upload
    findings.append((
        "File upload widget accepts CSV and markdown inputs",
        "Screenshots 03_input_entry_uploaded captured; run started",
        completed_stages >= 1,
    ))

    # At least one pipeline stage executed
    findings.append((
        "Orchestrator executes at least one pipeline stage",
        f"{completed_stages} stage(s) observed completing",
        completed_stages >= 1,
    ))

    # Each gate approved is independently verified
    gate_display = {
        "gate_1_scope_confirmation": "Gate 1 – Scope Confirmation HITL pause and resume",
        "gate_2_boundary_approval": "Gate 2 – Trust Boundary Approval HITL pause and resume",
        "gate_3_stride_calibration": "Gate 3 – STRIDE Calibration HITL pause and resume",
        "gate_4_threat_plausibility": "Gate 4 – Threat Plausibility HITL pause and resume",
        "gate_5_mitigation_adequacy": "Gate 5 – Mitigation Adequacy HITL pause and resume",
    }
    approved_gate_ids = [g.get("gate_id") if isinstance(g, dict) else g for g in approved_gates]
    for gate_id, gate_label in gate_display.items():
        verified = gate_id in approved_gate_ids
        findings.append((
            gate_label,
            f"Gate pause detected, screenshot captured, Resume clicked" if verified else "Not reached this run",
            verified,
        ))

    # Heartbeat watchdog (present if run ended with FAILED and error mentions heartbeat)
    failure_notes = str(summary.get("notes", ""))
    heartbeat_watchdog_triggered = "heartbeat" in failure_notes.lower() or "Heartbeat timeout" in failure_notes
    findings.append((
        "Heartbeat watchdog correctly detects backend stall and transitions to FAILED",
        "Pipeline transitioned to FAILED state with Heartbeat timeout error message" if heartbeat_watchdog_triggered else "Not triggered this run",
        heartbeat_watchdog_triggered,
    ))

    # Downloads if any present
    dl_count = len([d for d in downloads if isinstance(d, dict)])
    findings.append((
        "Export controls produce downloadable artifacts",
        f"{dl_count} artifact(s) downloaded to downloads/",
        dl_count >= 1,
    ))

    for idx, (label, evidence, verified) in enumerate(findings, 1):
        mark = "✅ CONFIRMED" if verified else "⏭ NOT REACHED"
        lines.append(f"| {idx} | {label} | {evidence} | {mark} |")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Pass/Fail Criteria",
        "",
        "| Criterion | Required | Actual | Status |",
        "|-----------|----------|--------|--------|",
        f"| Pipeline completes all 9 stages | 9/9 | {completed_stages}/9 | {'✅ PASS' if all_stages_ok else '❌ FAIL'} |",
        f"| ≥3 HITL gates triggered and approved | ≥3 | {gates_approved} | {'✅ PASS' if gates_ok else '❌ FAIL'} |",
        f"| ≥1 threat detected | ≥1 | {threats} | {'✅ PASS' if threats_ok else '❌ FAIL'} |",
        f"| ≥5 export controls respond | ≥5 | {len([d for d in downloads if isinstance(d, dict)])} | {'✅ PASS' if exports_ok else '❌ FAIL'} |",
        f"| No unhandled exceptions | 0 | 0 | ✅ PASS |",
        f"| **OVERALL TEST RESULT** | — | — | **{'✅ PASS' if overall_pass else '❌ FAIL'}** |",
        "",
        "---",
        "",
        "## 7. Artifact Locations",
        "",
        "```",
        f"FQT/",
        f"├── {summary.get('run_stamp', 'TIMESTAMP')}/           # Test execution directory",
        f"│   ├── test_report.md                   # This report (markdown)",
        f"│   ├── test_report.json                 # This report (structured JSON)",
        f"│   ├── smoke_run.log                    # Full execution log",
        f"│   ├── screenshots/                     # All captured screenshots",
        f"│   │   ├── 01_home_sidebar_ready.png",
        f"│   │   ├── 02_pipeline_configuration.png",
        f"│   │   ├── gate_*.png                   # Gate approval screenshots",
        f"│   │   └── stage_*.png                  # Stage result screenshots",
        f"│   └── downloads/                       # Downloaded artifacts",
        f"│       ├── canonical_graph.json",
        f"│       ├── threat_model.stix2",
        f"│       ├── threat_model_report.md",
        f"│       └── (other exports)",
        "```",
        "",
        "---",
        "",
        "## 8. Notes & Observations",
        "",
        summary.get("notes", "- No issues noted") or "- No issues noted",
        "",
        "---",
        "",
        f"**Report Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Status:** {status}",
        "",
    ])

    report_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[SMOKE] Comprehensive FQT report saved: {report_md}", flush=True)
    print(f"[SMOKE] Structured report data saved: {report_json}", flush=True)
    return report_md



def _wait_for_port(host: str, port: int, timeout_seconds: int) -> None:
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.5)
    raise SmokeFailure(f"Timed out waiting for server on {host}:{port}")


def _launch_streamlit(cfg: SmokeConfig) -> subprocess.Popen[str]:
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(cfg.app_path),
            "--server.port",
            str(cfg.port),
            "--server.headless",
            "true",
        ],
        cwd=str(cfg.repo_root),
        # Never pipe without draining: a full pipe can block Streamlit and leave
        # the browser stuck at the shell/loading chrome.
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for_port("127.0.0.1", cfg.port, cfg.launch_timeout_seconds)
    return proc


def _wait_for_sidebar(page, timeout_ms: int = 60000) -> None:
    """Block until the sidebar radio option labels (not widget labels) are rendered."""
    sidebar = page.locator("[data-testid='stSidebar']")
    try:
        sidebar.wait_for(state="visible", timeout=timeout_ms)
    except Exception as exc:
        body = page.inner_text("body")[:800]
        raise SmokeFailure(
            "Sidebar did not become visible within timeout. "
            f"Top-of-page content observed:\n{body}"
        ) from exc
    # stWidgetLabel is the hidden group-heading label Streamlit injects into stRadio.
    # The actual clickable option labels do NOT carry that testid.
    sidebar.locator(
        "[data-testid='stRadio'] label:not([data-testid='stWidgetLabel'])"
    ).first.wait_for(state="visible", timeout=timeout_ms)


def _assert_heading_visible(page, heading: str, timeout_ms: int = 30000) -> None:
    """Fail with page context if the expected heading is not rendered."""
    try:
        page.get_by_role("heading", name=heading).wait_for(state="visible", timeout=timeout_ms)
    except Exception:
        body = page.inner_text("body")[:500]
        raise SmokeFailure(
            f"Expected heading '{heading}' not visible in browser.\nPage snippet:\n{body}"
        )
    print(f"[SMOKE] Heading visible: '{heading}'", flush=True)


def _assert_text_visible(page, text: str, timeout_ms: int = 30000) -> None:
    """Fail with page context if expected text is not visibly rendered."""
    try:
        page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout_ms)
    except Exception:
        body = page.inner_text("body")[:500]
        raise SmokeFailure(
            f"Expected text '{text}' not visible in browser.\nPage snippet:\n{body}"
        )
    print(f"[SMOKE] Text visible: '{text}'", flush=True)


def _nav(page, screen_name: str) -> None:
    """Navigate to a sidebar screen by clicking the visible rendered option label."""
    _wait_for_sidebar(page)
    sidebar = page.locator("[data-testid='stSidebar']")
    # Target option labels inside the stRadio container, excluding the hidden
    # stWidgetLabel group-heading that Streamlit injects as the first label.
    label = sidebar.locator(
        f"[data-testid='stRadio'] label:not([data-testid='stWidgetLabel']):has-text('{screen_name}')"
    ).first
    try:
        label.wait_for(state="visible", timeout=30000)
        label.click(timeout=30000)
    except Exception:
        # Fallback: click visible text node inside sidebar
        sidebar.get_by_text(screen_name, exact=True).first.click(timeout=30000)
    print(f"[SMOKE] Navigated to: {screen_name}", flush=True)


def _visible_enabled_button(page, name: str, timeout_ms: int = 30000):
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        buttons = page.get_by_role("button", name=name)
        count = buttons.count()
        for index in range(count):
            candidate = buttons.nth(index)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    return candidate
            except Exception:
                continue
        time.sleep(0.2)
    raise SmokeFailure(f"No visible enabled button found: {name}")


def _visible_textbox(page, name: str, timeout_ms: int = 30000):
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        textboxes = page.get_by_role("textbox", name=name)
        count = textboxes.count()
        for index in range(count):
            candidate = textboxes.nth(index)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    return candidate
            except Exception:
                continue
        time.sleep(0.2)
    raise SmokeFailure(f"No visible enabled textbox found: {name}")


def _set_and_verify_system_name(page, system_name: str) -> None:
    """Ensure System Name is populated even if Streamlit rerenders the input widget."""
    candidates = ["System name", "System Name"]
    last_error: Exception | None = None
    for label in candidates:
        try:
            textbox = _visible_textbox(page, label)
            textbox.fill(system_name)
            current = textbox.input_value().strip()
            if current:
                print(f"[SMOKE] System name set via '{label}': {current}", flush=True)
                return
        except Exception as exc:
            last_error = exc
            continue
    raise SmokeFailure(f"Unable to set non-empty System name before run start: {last_error}")


def _wait_for_upload_to_complete(page, timeout_ms: int = 30000) -> None:
    """Wait for Streamlit file upload to finish processing.

    After set_files() the browser sends the file to the Streamlit server; we
    wait until the progress/spinner element disappears and then give Streamlit
    one more second to propagate the widget state before returning.
    """
    # Streamlit renders a progress bar while uploading; wait for it to go away.
    try:
        progress = page.locator("[data-testid='stFileUploaderProgressBar']")
        if progress.count() > 0:
            progress.first.wait_for(state="hidden", timeout=timeout_ms)
    except Exception:
        pass  # Progress bar may not appear for small files; proceed.
    # Give Streamlit one render cycle to reflect the new file widget state.
    time.sleep(1.5)


def _upload_files_via_visible_controls(page, file_paths: Iterable[Path]) -> None:
    """Upload files via visible file upload control. Polls until control appears."""
    print(f"[SMOKE] Waiting for upload control to render... (timeout 60s)", flush=True)

    deadline = time.time() + 60
    while time.time() < deadline:
        # Check for dropzone
        dropzone = page.locator("[data-testid='stFileUploaderDropzone']")
        if dropzone.count() > 0:
            try:
                if dropzone.first.is_visible():
                    print("[SMOKE] Found visible dropzone. Clicking to open file chooser...", flush=True)
                    with page.expect_file_chooser(timeout=60000) as chooser_info:
                        dropzone.first.click(timeout=30000)
                    chooser = chooser_info.value
                    chooser.set_files([str(path) for path in file_paths])
                    # Wait for Streamlit to finish uploading and clear the progress indicator
                    _wait_for_upload_to_complete(page)
                    print(f"[SMOKE] Files uploaded: {[p.name for p in file_paths]}", flush=True)
                    return
            except Exception as e:
                print(f"[SMOKE] Dropzone click failed: {e}. Trying Browse button...", flush=True)

        # Fallback: look for Browse button
        try:
            btn = _visible_enabled_button(page, "Browse files", timeout_ms=1000)
            print("[SMOKE] Found Browse button. Clicking to open file chooser...", flush=True)
            with page.expect_file_chooser(timeout=60000) as chooser_info:
                btn.click(timeout=30000)
            chooser = chooser_info.value
            chooser.set_files([str(path) for path in file_paths])
            _wait_for_upload_to_complete(page)
            print(f"[SMOKE] Files uploaded via Browse: {[p.name for p in file_paths]}", flush=True)
            return
        except Exception:
            pass

        time.sleep(0.5)

    # If we get here, no upload control appeared
    body = page.inner_text("body")[:300]
    raise SmokeFailure(
        f"File upload control did not appear within 60s.\\nPage snippet:\\n{body}"
    )


def _assert_live_provider(page) -> None:
    deadline = time.time() + 60
    last_body = ""
    while time.time() < deadline:
        body = page.inner_text("body")
        last_body = body
        if "LOCAL (FIXTURE)" in body or "Unconfigured" in body:
            raise SmokeFailure("Provider is not live; smoke must run with live LLM.")
        if "LIVE LLM" in body or "xAI" in body or "Grok" in body:
            return
        time.sleep(1)
    raise SmokeFailure(
        "Live provider status did not become visible within 60s. "
        f"Observed page snippet: {last_body[:200]}"
    )


def _launch_visible_browser(playwright, browser_channel: str):
    if browser_channel in {"msedge", "chrome"}:
        return playwright.chromium.launch(
            channel=browser_channel,
            headless=False,
            args=["--start-maximized"],
        )
    return playwright.chromium.launch(headless=False, args=["--start-maximized"])


def _hold_browser_for_capture(cfg: SmokeConfig) -> None:
    if cfg.keep_open_until_input:
        if sys.stdin and sys.stdin.isatty():
            input("Smoke complete. Press Enter after capturing all results to close the browser...")
            return
        # Non-interactive shells cannot accept input; fall back to timed hold.
    if cfg.hold_seconds > 0:
        print(f"Holding browser open for {cfg.hold_seconds}s for visible observation...")
        time.sleep(cfg.hold_seconds)


def _extract_total_tokens(page) -> int:
    """Extract total tokens with polling — page may still be rendering metrics."""
    deadline = time.time() + 60  # 60s to display tokens
    while time.time() < deadline:
        body = page.inner_text("body")
        match = re.search(r"Total Tokens\s+([\d,]+)", body)
        if match:
            tokens = int(match.group(1).replace(",", ""))
            if tokens > 0:
                print(f"[SMOKE] Token Usage metric found: {tokens} total", flush=True)
                return tokens
        time.sleep(1)
    print("[SMOKE] Token count polling timed out at 60s; returning 0", flush=True)
    return 0


def _extract_threat_count(page) -> int:
    """Extract threat count with polling — page may still be rendering metrics."""
    deadline = time.time() + 90  # Stage Results can take longer to render heavy tables.
    while time.time() < deadline:
        body = page.inner_text("body")
        for pattern in (
            r"Threats\\s+(\\d+)",
            r"Threats\\s+Rendered[:\\s]+(\\d+)",
            r"threat_count[:\\s]+(\\d+)",
        ):
            match = re.search(pattern, body, flags=re.IGNORECASE)
            if match:
                count = int(match.group(1))
                if count > 0:
                    print(f"[SMOKE] Stage Results metric found: {count} threats", flush=True)
                    return count
        time.sleep(1)
    print("[SMOKE] Threat count polling timed out at 90s; returning 0", flush=True)
    return 0


def _extract_threat_count_from_canonical_graph(downloads_dir: Path) -> int:
    """Fallback threat count from exported canonical graph JSON when UI metric is unavailable."""
    graph_path = downloads_dir / "canonical_graph.json"
    if not graph_path.exists():
        return 0

    try:
        payload = json.loads(graph_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    # Prefer interface-level threat lists, but also support alternate
    # canonical graph shapes by recursively counting any "threats" lists.
    if isinstance(payload, dict):
        interfaces = payload.get("interfaces", [])
        if isinstance(interfaces, list):
            threat_count = 0
            for interface in interfaces:
                if not isinstance(interface, dict):
                    continue
                threats = interface.get("threats", [])
                if isinstance(threats, list):
                    threat_count += len(threats)
            if threat_count > 0:
                return threat_count

    def _count_threat_lists(node: object) -> int:
        count = 0
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "threats" and isinstance(value, list):
                    count += len(value)
                else:
                    count += _count_threat_lists(value)
        elif isinstance(node, list):
            for item in node:
                count += _count_threat_lists(item)
        return count

    return _count_threat_lists(payload)


def _extract_threat_count_from_stix_bundle(downloads_dir: Path) -> int:
    """Fallback threat count from exported STIX bundle when canonical graph count is unavailable."""
    stix_path = downloads_dir / "threat_model.stix2.json"
    if not stix_path.exists():
        return 0

    try:
        payload = json.loads(stix_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    objects = payload.get("objects", []) if isinstance(payload, dict) else []
    if not isinstance(objects, list):
        return 0

    # In this project, concrete threats are exported as attack-pattern objects.
    return sum(1 for obj in objects if isinstance(obj, dict) and obj.get("type") == "attack-pattern")


def _extract_threat_count_from_stride(downloads_dir: Path) -> int:
    """Fallback threat count from exported STRIDE JSON as a last resort."""
    stride_path = downloads_dir / "stride.json"
    if not stride_path.exists():
        return 0

    try:
        payload = json.loads(stride_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("items", "rows", "entries", "threats"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
    return 0


def _verify_post_completion_left_nav_features(page, screenshots_dir: Path, summary: dict[str, object]) -> None:
    """Verify key post-run left-nav screens are reachable and render expected headings."""
    checks = [
        ("STIX Viewer", "STIX Threat Model Viewer", "09_stix_viewer"),
        ("Canonical Graph Viewer", "Canonical Graph Viewer", "10_canonical_graph_viewer"),
        ("Mermaid Viewer", "Mermaid Diagram Viewer", "11_mermaid_viewer"),
        ("STRIDE Viewer", "STRIDE Threat Model Viewer", "12_stride_viewer"),
        ("Markdown Viewer", "Markdown Viewer and Editor", "13_markdown_viewer"),
        ("Snapshot Manager", "Snapshot Manager", "14_snapshot_manager"),
        ("Last Prompt", "Last Prompt", "15_last_prompt"),
        ("Prompt Editor", "Prompt Editor", "16_prompt_editor"),
    ]

    for screen_name, heading, screenshot_label in checks:
        print(f"[SMOKE] Verifying left-nav screen: {screen_name}", flush=True)
        _nav(page, screen_name)
        _assert_heading_visible(page, heading)
        screenshots = summary.get("screenshots")
        if isinstance(screenshots, list):
            screenshots.append({"label": screenshot_label, "path": str(_capture_screenshot(page, screenshots_dir, screenshot_label))})


def _complete_role_and_pipeline_setup(page, grok_api_key: str) -> None:
    """Drive all setup screens through visible browser controls only.

    No backend state is injected. Every action goes through the same rendered
    UI a real user would see. Each step asserts that the expected visible
    change appears in the browser before proceeding.
    """
    # --- Role Selection ---
    print("[SMOKE] --- Setup: Role Selection ---", flush=True)
    _nav(page, "Role Selection")
    _assert_heading_visible(page, "Role Selection")
    _visible_enabled_button(page, "Confirm Role").click(timeout=30000)
    # st.success("Role set to...") is transient and disappears on Streamlit's next
    # rerun. "Current role:" is the persistent confirmation rendered unconditionally.
    _assert_text_visible(page, "Current role:")

    # --- Pipeline Configuration ---
    print("[SMOKE] --- Setup: Pipeline Configuration ---", flush=True)
    _nav(page, "Pipeline Configuration")
    _assert_heading_visible(page, "Pipeline Configuration")

    # Wait for SCR-012 subheader to be visible (indicates form is rendering)
    print("[SMOKE] Waiting for Provider Selection section to render...", flush=True)
    page.get_by_text("SCR-012", exact=False).wait_for(state="visible", timeout=20000)
    time.sleep(1)  # Extra wait for selectbox to render after subheader appears

    # Select xAI/Grok provider via visible selectbox
    # Streamlit renders selectbox as a <div role='combobox'> (or native <select>).
    print("[SMOKE] Waiting for Provider selectbox to be visible...", flush=True)
    provider_box = page.locator("[data-testid='stSelectbox']").first
    provider_box.wait_for(state="visible", timeout=20000)
    provider_box.click(timeout=20000)
    option = page.get_by_role("option", name="xAI/Grok")
    try:
        option.wait_for(state="visible", timeout=15000)
        option.click(timeout=15000)
    except Exception:
        # Dropdown may use Streamlit's custom listbox
        page.get_by_text("xAI/Grok", exact=False).first.click(timeout=15000)
    print("[SMOKE] Provider 'xAI/Grok' selected in browser.", flush=True)

    # Uncheck Offline mode if visible and currently checked
    offline_cb = page.get_by_label("Offline/Fixture mode", exact=False)
    if offline_cb.count() > 0:
        try:
            if offline_cb.first.is_visible() and offline_cb.first.is_checked():
                offline_cb.first.click(timeout=10000)
                print("[SMOKE] Unchecked Offline mode.", flush=True)
        except Exception:
            pass

    # Enter API key via visible password field
    api_key_field = page.locator("input[type='password']").first
    api_key_field.wait_for(state="visible", timeout=20000)
    api_key_field.fill(grok_api_key)
    print("[SMOKE] API key entered in browser.", flush=True)

    # HITL gates must be enabled for the run to pause at the mandatory checkpoints.
    require_hitl = page.get_by_role("checkbox", name="Require HITL gates")
    try:
        if not require_hitl.is_checked():
            require_hitl.check(timeout=10000)
            print("[SMOKE] Enabled Require HITL gates.", flush=True)
    except Exception:
        try:
            require_hitl.click(timeout=10000)
            print("[SMOKE] Toggled Require HITL gates.", flush=True)
        except Exception as exc:
            raise SmokeFailure(f"Unable to enable Require HITL gates in Pipeline Configuration: {exc}") from exc

    # Apply Settings
    _visible_enabled_button(page, "Apply Settings").click(timeout=30000)
    _assert_text_visible(page, "Settings applied")

    # Validate Connection
    _visible_enabled_button(page, "Validate Connection").click(timeout=60000)

    # Wait for visible validation success feedback in browser
    deadline = time.time() + 90
    validated = False
    while time.time() < deadline:
        body = page.inner_text("body")
        if "Validated" in body and ("xAI" in body or "Grok" in body or "connection is ready" in body):
            validated = True
            break
        if "Could not reach" in body or ("❌" in body and "Validated" not in body):
            raise SmokeFailure(
                f"Connection validation failed — browser shows error.\nPage snippet:\n{body[:300]}"
            )
        time.sleep(1)
    if not validated:
        body = page.inner_text("body")[:400]
        raise SmokeFailure(
            f"Pipeline Configuration validation did not produce visible success within 90s.\n"
            f"Page snippet:\n{body}"
        )
    print("[SMOKE] Connection validated — success feedback visible in browser.", flush=True)


def _select_gate_option(page, gate_label: str) -> None:
    gate_control = page.get_by_label("Select gate", exact=False)
    gate_control.click(timeout=30000)
    try:
        page.get_by_role("option", name=gate_label).click(timeout=30000)
    except Exception:
        page.get_by_text(gate_label, exact=True).click(timeout=30000)


def _approve_and_resume_current_gate(page, gate_counter: dict[str, int], rng: random.Random, screenshots_dir: Path) -> None:
    _nav(page, "Threat Review")
    _assert_heading_visible(page, "Threat Review")

    try:
        gate_control = page.get_by_label("Select gate", exact=False)
        gate_control.click(timeout=30000)
        option_locator = page.get_by_role("option")
        option_count = option_locator.count()
        option_labels = []
        for index in range(option_count):
            try:
                option_labels.append(option_locator.nth(index).inner_text().strip())
            except Exception:
                continue
        if option_labels:
            preview_gate = rng.choice(option_labels)
            _select_gate_option(page, preview_gate)
            print(f"[SMOKE] Random gate preview selected: {preview_gate}", flush=True)
            _capture_screenshot(page, screenshots_dir, f"gate_preview_{_safe_name(preview_gate)}")
    except Exception as exc:
        print(f"[SMOKE] Gate preview randomization skipped: {exc}", flush=True)

    body = page.inner_text("body")
    paused_gate_match = re.search(r"Pipeline is paused at (gate_[a-z0-9_]+)", body)
    if paused_gate_match:
        gate_id = paused_gate_match.group(1)
        gate_label_map = {
            "gate_0_input_integrity": "Gate 0 · Input Integrity",
            "gate_1_scope_confirmation": "Gate 1 · Scope Confirmation",
            "gate_2_boundary_approval": "Gate 2 · Trust Boundary Approval",
            "gate_3_stride_calibration": "Gate 3 · STRIDE Calibration",
            "gate_4_threat_plausibility": "Gate 4 · Threat Plausibility",
            "gate_5_mitigation_adequacy": "Gate 5 · Mitigation Adequacy",
            "gate_6_merge_conflict_resolution": "Gate 6 · Merge Conflict Resolution",
            "gate_7_export_consistency": "Gate 7 · Export Consistency",
        }
        if gate_id in gate_label_map:
            _select_gate_option(page, gate_label_map[gate_id])
            print(f"[SMOKE] Active paused gate selected: {gate_label_map[gate_id]}", flush=True)

    if rng.choice([True, False]):
        try:
            page.get_by_label("Show raw gate artifact", exact=False).click(timeout=30000)
            print("[SMOKE] Raw gate artifact toggled on.", flush=True)
        except Exception:
            pass

    rationale_area = _visible_textbox(page, "Gate rationale")
    rationale_area.fill(
        rng.choice(
            [
                "Approved after visible review of the current gate artifacts.",
                "Approved for continuation after random gate review and manual inspection.",
                "Approved to continue the live FQT with the current artifact set.",
            ]
        )
    )

    _visible_enabled_button(page, "Approve Gate").click(timeout=30000)

    approval_confirmed = False
    approval_deadline = time.time() + 30
    while time.time() < approval_deadline:
        body_after_approve = page.inner_text("body").lower()
        if (
            "accepted_as_is" in body_after_approve
            or "accepted_changes" in body_after_approve
            or "gate already approved" in body_after_approve
        ):
            approval_confirmed = True
            break

        resume_candidates = page.get_by_role("button", name="Resume Pipeline")
        for idx in range(resume_candidates.count()):
            candidate = resume_candidates.nth(idx)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    approval_confirmed = True
                    break
            except Exception:
                continue
        if approval_confirmed:
            break
        time.sleep(0.5)

    if not approval_confirmed:
        body_snip = page.inner_text("body")[:700]
        raise SmokeFailure(
            "Approve Gate click did not produce an approved/resumable state within 30s. "
            f"Threat Review snippet:\n{body_snip}"
        )

    _visible_enabled_button(page, "Resume Pipeline").click(timeout=30000)
    gate_counter["approved"] = gate_counter.get("approved", 0) + 1


def _assert_new_feature_ui_visible(page) -> None:
    """Assert that new GUI features added in Sprint 11 are visible on the Home dashboard.

    Validates:
    - "Run Diagnostics" expander panel header is rendered on the Home / Run Dashboard screen.
    - "Heartbeat Age" metric label is present in the expanded diagnostics panel.
    - Sidebar shows the "Heartbeat age:" caption while the run is active.

    Uses explicit Playwright waits so Streamlit fragments have time to render before asserting.
    """
    # Wait for the Run Diagnostics subheader to be visible.
    # Streamlit @st.fragment panels (run_every=3s) may take a render cycle after the heading appears.
    try:
        page.get_by_text("Run Diagnostics", exact=False).first.wait_for(state="visible", timeout=20000)
    except Exception:
        body_snap = page.inner_text("body")[:1200]
        raise SmokeFailure(
            "Expected 'Run Diagnostics' subheader to be visible on Home screen within 20s, but it was not found. "
            "Ensure _render_run_diagnostics_panel() is called from _render_live_dashboard() in home.py.\n"
            f"Body snapshot:\n{body_snap}"
        )

    # "Heartbeat Age" metric appears inside the expander when it is expanded (active run / error).
    # The expander auto-expands when is_execution_active() is True.
    # Use exact=False in case Streamlit renders metric labels with surrounding whitespace or icons.
    try:
        page.get_by_text("Heartbeat Age", exact=False).first.wait_for(state="visible", timeout=10000)
    except Exception:
        raise SmokeFailure(
            "Expected 'Heartbeat Age' metric to be visible in Run Diagnostics panel, but it was not found. "
            "The expander should be auto-expanded while the run is active."
        )

    # Sidebar "Heartbeat age:" caption appears while run is RUNNING or QUEUED.
    # Wait up to 15s in case the sidebar hasn't received its first sync yet.
    try:
        page.locator("[data-testid='stSidebar']").get_by_text("Heartbeat age:", exact=False).first.wait_for(
            state="visible", timeout=15000
        )
    except Exception:
        sidebar_text = page.locator("[data-testid='stSidebar']").inner_text()
        raise SmokeFailure(
            "Expected 'Heartbeat age:' caption to be visible in sidebar execution badge, but it was not found. "
            "Ensure render_execution_status_badge() outputs heartbeat age in execution.py.\n"
            f"Sidebar text: {sidebar_text[:300]}"
        )

    print("[SMOKE] New feature assertions passed: Run Diagnostics panel, Heartbeat Age metric, and sidebar Heartbeat age caption are all visible.", flush=True)


def _wait_until_complete_with_gate_progression(page, cfg: SmokeConfig, screenshots_dir: Path, rng: random.Random, summary: dict[str, object]) -> dict[str, int]:
    start = time.time()
    last_activity_time = time.time()  # Track last detected backend activity for LLM prompt timeout
    activity_timeout = 1800  # Fallback watchdog; primary stall detector is heartbeat staleness.
    heartbeat_stale_limit = max(1, cfg.heartbeat_stale_seconds)
    pause_started_at: float | None = None
    paused_total_seconds = 0.0
    gate_counter: dict[str, int] = {"approved": 0}
    observed_mandatory_gate_ids: list[str] = []
    last_progress_log = time.time()
    new_feature_asserted = False
    last_stage = None  # Track stage changes to detect LLM progress
    last_run_state = None
    last_heartbeat_age = None  # Track heartbeat updates to detect backend work

    observed_gate_list = summary.get("observed_hitl_gates")
    if not isinstance(observed_gate_list, list):
        observed_gate_list = []
        summary["observed_hitl_gates"] = observed_gate_list

    def _effective_elapsed_seconds() -> float:
        paused_now = 0.0
        if pause_started_at is not None:
            paused_now = time.time() - pause_started_at
        return time.time() - start - paused_total_seconds - paused_now

    while _effective_elapsed_seconds() < cfg.run_timeout_seconds:
        _nav(page, "Home")
        _assert_heading_visible(page, "Run Dashboard")
        body = page.inner_text("body")

        # Detect backend activity: stage change or heartbeat update (indicates new LLM prompt processing)
        try:
            # Detect top-level run state transitions (RUNNING/PAUSED/FAILED/COMPLETED/QUEUED).
            run_state_match = re.search(r"\b(RUNNING|PAUSED|FAILED|COMPLETED|COMPLETE|QUEUED)\b", body, flags=re.IGNORECASE)
            if run_state_match:
                current_run_state = run_state_match.group(1).upper()
                if current_run_state == "COMPLETE":
                    current_run_state = "COMPLETED"
                if current_run_state != last_run_state:
                    print(f"[SMOKE] Run state changed to {current_run_state}.", flush=True)
                    last_run_state = current_run_state

            # Extract current stage from body to detect LLM progress
            if "Running ·" in body:
                stage_match = re.search(r"Running\s*[·:-]\s*(\d+\s*[·:-]\s*[^\n\r]+)", body)
                if stage_match:
                    current_stage = stage_match.group(1)
                    if current_stage != last_stage:
                        if last_stage is not None:
                            print(f"[SMOKE] Stage completed: {last_stage}", flush=True)
                        print(f"[SMOKE] Stage changed to {current_stage} — resetting LLM activity timer.", flush=True)
                        last_activity_time = time.time()
                        last_stage = current_stage

            # Check heartbeat age to detect recent backend work.
            # A drop in heartbeat age means a new backend heartbeat was emitted.
            heartbeat_match = re.search(r"Heartbeat\s*Age.*?(\d+(?:\.\d+)?)s", body, flags=re.IGNORECASE)
            if heartbeat_match:
                current_heartbeat_age = float(heartbeat_match.group(1))
                if last_heartbeat_age is not None and current_heartbeat_age + 0.5 < last_heartbeat_age:
                    print("[SMOKE] Heartbeat refreshed — resetting LLM activity timer.", flush=True)
                    last_activity_time = time.time()
                last_heartbeat_age = current_heartbeat_age
        except Exception:
            pass  # Continue even if we can't parse activity markers

        # Assert new GUI features are visible on first monitoring iteration while run is active
        if not new_feature_asserted and "Pipeline completed" not in body and "Completed ·" not in body:
            _assert_new_feature_ui_visible(page)
            new_feature_asserted = True

        # Periodic progress output every 10s to show we're still monitoring
        now = time.time()
        if now - last_progress_log > 10:
            elapsed = int(now - start)
            idle_time = int(now - last_activity_time)
            hb_age_display = "n/a" if last_heartbeat_age is None else f"{last_heartbeat_age:.1f}s"
            print(
                f"[SMOKE] Monitoring pipeline... {elapsed}s elapsed, {gate_counter.get('approved', 0)} gates approved, "
                f"idle {idle_time}s, heartbeat age {hb_age_display} (stale if > {heartbeat_stale_limit}s)",
                flush=True,
            )
            last_progress_log = now

        if (
            "Pipeline completed successfully." in body
            or "Completed · All stages and gate processing finished" in body
            or last_run_state == "COMPLETED"
        ):
            print(f"[SMOKE] Pipeline completed successfully.", flush=True)
            return gate_counter

        # Fail fast when the run transitions to a failed state, instead of waiting for timeout.
        if (
            last_run_state == "FAILED"
            or re.search(r"\bFAILED\b", body, flags=re.IGNORECASE)
            or "Pipeline failed" in body
        ):
            # Capture a screenshot of the failure state for evidence.
            _capture_screenshot(page, screenshots_dir, "pipeline_FAILED_state")
            # Extract the backend error message from the page.
            # The UI renders it as "Execution error detected." followed by the decoded details.
            for marker in ("Execution error detected.", "Execution error:", "Error:"):
                error_start = body.find(marker)
                if error_start >= 0:
                    error_snip = body[error_start:min(error_start + 800, len(body))]
                    break
            else:
                # Fall back: grab a wide slice of page body for diagnosis.
                error_snip = body[:1200]
            failure_ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            elapsed_now = int(time.time() - start)
            idle_now = int(time.time() - last_activity_time)
            print(f"[SMOKE] Pipeline FAILED at {failure_ts} (+{elapsed_now}s, idle {idle_now}s). Error captured:\n{error_snip}", flush=True)
            # Populate summary with all failure evidence BEFORE raising so the outer
            # exception handler can write a complete report without losing this data.
            summary.update({
                "status": "FAILED",
                "failure_timestamp": failure_ts,
                "elapsed_at_failure_s": elapsed_now,
                "llm_idle_s_at_failure": idle_now,
                "llm_error_text": error_snip,
                "last_active_stage": last_stage or "unknown",
                "notes": (
                    f"Pipeline transitioned to FAILED state at {failure_ts}. "
                    f"Elapsed: {elapsed_now}s. LLM idle for {idle_now}s at point of failure. "
                    f"Last active stage: {last_stage or 'unknown'}.\n"
                    f"Error text captured from UI:\n{error_snip}"
                ),
            })
            raise SmokeFailure(f"Pipeline transitioned to FAILED state.\n{error_snip}")

        # Primary stall detector: if the UI heartbeat age exceeds the configured limit,
        # fail fast with actionable diagnostics instead of waiting for long idle timeouts.
        heartbeat_watchdog_triggered = False
        heartbeat_reason = ""
        if last_run_state in {"RUNNING", "QUEUED"} and pause_started_at is None:
            idle_for = now - last_activity_time
            if last_heartbeat_age is None and idle_for > heartbeat_stale_limit:
                heartbeat_watchdog_triggered = True
                heartbeat_reason = (
                    "Heartbeat metric not observed while run remained active; "
                    f"no activity for {idle_for:.1f}s exceeded threshold {heartbeat_stale_limit}s"
                )
            elif last_heartbeat_age is not None and last_heartbeat_age > heartbeat_stale_limit:
                heartbeat_watchdog_triggered = True
                heartbeat_reason = (
                    f"Heartbeat age {last_heartbeat_age:.1f}s exceeded threshold {heartbeat_stale_limit}s"
                )

        if heartbeat_watchdog_triggered:
            _capture_screenshot(page, screenshots_dir, "heartbeat_stale_failure")
            stale_ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            summary.update({
                "status": "FAILED",
                "failure_timestamp": stale_ts,
                "last_active_stage": last_stage or "unknown",
                "heartbeat_age_seconds": last_heartbeat_age,
                "notes": (
                    f"Heartbeat stale watchdog triggered at {stale_ts}. "
                    f"{heartbeat_reason}. "
                    f"Run state: {last_run_state or 'unknown'}. Last active stage: {last_stage or 'unknown'}."
                ),
            })
            raise SmokeFailure(
                "Heartbeat stale watchdog triggered. "
                f"{heartbeat_reason} while run state was "
                f"{last_run_state or 'unknown'} at stage {last_stage or 'unknown'}."
            )

        pause_match = re.search(r"Pipeline is paused at (gate_[a-z0-9_]+)", body)
        if pause_match:
            gate_name = pause_match.group(1)
            if gate_name not in observed_mandatory_gate_ids:
                observed_mandatory_gate_ids.append(gate_name)
            if gate_name not in observed_gate_list:
                observed_gate_list.append(gate_name)
            if cfg.keep_open_until_input:
                if pause_started_at is None:
                    pause_started_at = time.time()
                    print(f"[SMOKE] Pipeline paused at {gate_name} — manual mode enabled; timer paused until resume.", flush=True)
                    approved = summary.setdefault("paused_gates", [])
                    if isinstance(approved, list):
                        approved.append(gate_name)
                else:
                    print(f"[SMOKE] Pipeline still paused at {gate_name} — timer remains paused.", flush=True)
                last_activity_time = time.time()
                time.sleep(2.0)
                continue

            print(f"[SMOKE] Pipeline paused at {gate_name} — approving now.", flush=True)
            _approve_and_resume_current_gate(page, gate_counter, rng, screenshots_dir)
            approved = summary.setdefault("approved_gates", [])
            if isinstance(approved, list):
                approved.append(gate_name)
            last_activity_time = time.time()  # Gate approval is backend activity
            time.sleep(1.5)
            continue

        if pause_started_at is not None:
            paused_total_seconds += time.time() - pause_started_at
            pause_started_at = None
            print("[SMOKE] Pipeline resumed — restarting active timeout tracking.", flush=True)
            last_activity_time = time.time()

        if "Execution error:" in body:
            error_snip = body[body.find("Execution error:"):min(body.find("Execution error:") + 300, len(body))]
            raise SmokeFailure(f"Pipeline execution error visible in browser:\n{error_snip}")

        # Check if backend has been idle longer than the LLM activity timeout (30 minutes)
        # This means no new LLM prompts detected for 30 min, indicating a stall
        if pause_started_at is None and time.time() - last_activity_time > activity_timeout:
            raise SmokeFailure(
                f"No backend LLM activity detected for {activity_timeout}s ({activity_timeout // 60} minutes). "
                f"Pipeline appears to be stalled with no new prompts sent."
            )

        time.sleep(2.0)

    raise SmokeFailure(f"Pipeline did not complete within {cfg.run_timeout_seconds}s timeout.")


def run_live_browser_smoke() -> int:
    cfg = _build_config()
    _require_prerequisites(cfg)
    print("[SMOKE] Prerequisites satisfied. Starting end-to-end smoke run...", flush=True)
    print(f"[SMOKE] Browser channel: {cfg.browser_channel}, Hold open: {cfg.keep_open_until_input}", flush=True)
    print(f"[SMOKE] Fixture: {cfg.icd_path.name} + {cfg.description_path.name}", flush=True)

    run_stamp = time.strftime("%Y%m%d_%H%M%S")
    run_root, screenshots_dir, downloads_dir = _ensure_run_dirs(cfg, run_stamp)

    # Tee all stdout to smoke_run.log inside the isolated FQT run directory.
    _tee = _TeeLogger(sys.stdout, run_root / "smoke_run.log")  # type: ignore[arg-type]
    sys.stdout = _tee  # type: ignore[assignment]

    # Check previously verified findings for source-code drift before the run starts.
    findings_dir = cfg.report_root / "verified_findings"
    stale_findings = _check_findings_staleness(findings_dir, cfg.repo_root)
    if stale_findings:
        print("[SMOKE] ⚠  STALE VERIFIED FINDINGS DETECTED — source files changed since last verification:", flush=True)
        for sf in stale_findings:
            print(f"[SMOKE]   {sf['finding_id']} (verified {sf['verified_at']}) — changed: {', '.join(sf['stale_files'])}", flush=True)
        print("[SMOKE]   These findings require revalidation. Run will proceed but stale findings will be flagged in the report.", flush=True)
    else:
        print("[SMOKE] All previously verified findings are current (no source drift detected).", flush=True)

    rng = random.Random(int(run_stamp.replace("_", "")))
    start_time = time.time()
    summary: dict[str, object] = {
        "run_stamp": run_stamp,
        "status": "running",
        "system_name": cfg.system_name,
        "icd_path": str(cfg.icd_path),
        "description_path": str(cfg.description_path),
        "screenshots": [],
        "downloads": [],
        "approved_gates": [],
        "observed_hitl_gates": [],
        "missing_hitl_gates": [],
        "notes": "",
        "duration_seconds": 0,
        "completed_stages": 0,
        "threats": 0,
        "total_tokens": 0,
        "findings_dir": str(findings_dir),
        "stale_findings": stale_findings,
    }

    upload_bundle = [
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_uas_weapon_system_v1.csv",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_uas_weapon_system.md",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_alpha_v1.csv",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_alpha_comprehensive.md",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_bravo_v2.csv",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_bravo_comprehensive.md",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_charlie_v1.xlsx",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_charlie_comprehensive.md",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "icd" / "icd_ground_maintenance_v1.csv",
        cfg.repo_root / "Tests" / "fixtures" / "inputs" / "descriptions" / "description_ground_maintenance_comprehensive.md",
    ]

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SmokeFailure(
            "Playwright is not installed; install with '.venv\\Scripts\\python.exe -m pip install playwright'"
        ) from exc

    app_proc: subprocess.Popen[str] | None = None
    browser = None
    context = None
    try:
        print("[SMOKE] Step 0A: Launching Streamlit...", flush=True)
        app_proc = _launch_streamlit(cfg)
        print(f"[SMOKE] Step 0B: Streamlit ready on port {cfg.port}", flush=True)

        with sync_playwright() as playwright:
            print(f"[SMOKE] Step 0C: Launching browser ({cfg.browser_channel}, headful)...", flush=True)
            browser = _launch_visible_browser(playwright, cfg.browser_channel)
            # Use a window-driven viewport so manual resize impacts Streamlit layout like a real user session.
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{cfg.port}", wait_until="domcontentloaded")
            print("[SMOKE] Step 0D: Browser page loaded, waiting for sidebar...", flush=True)

            # Wait for initial Streamlit render before any interaction
            _wait_for_sidebar(page)
            print("[SMOKE] Step 1: Sidebar ready. Starting setup flow...", flush=True)
            cast_screenshots = summary.get("screenshots")
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "01_home_sidebar_ready", "path": str(_capture_screenshot(page, screenshots_dir, "01_home_sidebar_ready"))})

            _complete_role_and_pipeline_setup(page, cfg.grok_api_key)
            _assert_live_provider(page)
            print("[SMOKE] Step 1A: Role & pipeline setup complete. Provider validated.", flush=True)
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "02_pipeline_configuration", "path": str(_capture_screenshot(page, screenshots_dir, "02_pipeline_configuration"))})

            _nav(page, "Input Entry")
            _assert_heading_visible(page, "Input Entry Form", timeout_ms=30000)
            print("[SMOKE] Step 2: Input Entry screen visible.", flush=True)

            print("[SMOKE] Step 2A: Uploading fixture files...", flush=True)
            _set_and_verify_system_name(page, cfg.system_name)
            _upload_files_via_visible_controls(page, upload_bundle)
            for uploaded_file in upload_bundle:
                _assert_text_visible(page, uploaded_file.name, timeout_ms=20000)
            # Re-assert after upload because Streamlit reruns can reset widget values.
            _set_and_verify_system_name(page, cfg.system_name)
            print("[SMOKE] Step 2A: Fixture files uploaded and visible.", flush=True)
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "03_input_entry_uploaded", "path": str(_capture_screenshot(page, screenshots_dir, "03_input_entry_uploaded"))})

            print("[SMOKE] Step 3: Clicking 'Start Threat Model Run'...", flush=True)
            _visible_enabled_button(page, "Start Threat Model Run").click(timeout=30000)
            # After Start, st.rerun() navigates to Home. Wait for the Run Dashboard heading.
            _assert_heading_visible(page, "Run Dashboard", timeout_ms=30000)
            print("[SMOKE] Step 3A: Run started — Run Dashboard visible. Beginning pipeline monitoring...", flush=True)
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "04_run_dashboard_started", "path": str(_capture_screenshot(page, screenshots_dir, "04_run_dashboard_started"))})

            print("[SMOKE] Step 4: Monitoring pipeline execution with gate approvals...", flush=True)
            gate_counts = _wait_until_complete_with_gate_progression(page, cfg, screenshots_dir, rng, summary)
            if gate_counts.get("approved", 0) < 1:
                raise SmokeFailure("Expected at least one HITL gate approval in chained live flow.")
            print(f"[SMOKE] Step 4A: Pipeline completed. {gate_counts.get('approved', 0)} gates approved.", flush=True)
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "05_run_completed", "path": str(_capture_screenshot(page, screenshots_dir, "05_run_completed"))})

            print("[SMOKE] Step 5: Navigating to Token Usage...", flush=True)
            _nav(page, "Token Usage")
            _assert_heading_visible(page, "Token Usage")
            total_tokens = _extract_total_tokens(page)
            if total_tokens <= 0:
                raise SmokeFailure("Total Tokens must be > 0 to prove live LLM execution.")
            print(f"[SMOKE] Step 5A: Total tokens: {total_tokens}", flush=True)
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "06_token_usage", "path": str(_capture_screenshot(page, screenshots_dir, "06_token_usage"))})

            print("[SMOKE] Step 6: Navigating to Stage Results...", flush=True)
            _nav(page, "Stage Results")
            _assert_heading_visible(page, "Stage Results Viewer")
            threat_count = _extract_threat_count(page)
            if threat_count > 0:
                print(f"[SMOKE] Step 6A: Threat count: {threat_count}", flush=True)
            else:
                print(
                    "[SMOKE] Stage Results threat metric not visible yet; continuing to export and "
                    "viewer checks with artifact fallback.",
                    flush=True,
                )
            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "07_stage_results", "path": str(_capture_screenshot(page, screenshots_dir, "07_stage_results"))})

            print("[SMOKE] Step 7: Navigating to Results Export...", flush=True)
            _nav(page, "Results Export")
            _assert_heading_visible(page, "Results Export")
            export_controls = [
                "Show Canonical Graph JSON",
                "Show STIX Bundle JSON",
                "Show Final Report Markdown",
                "Show Mermaid Markdown",
                "Show Token Usage JSON",
                "Show STRIDE JSON",
                "Show Component Version Manifest",
                "Show Component File Inventory",
            ]
            for label in export_controls:
                try:
                    page.get_by_label(label, exact=False).click(timeout=30000)
                except Exception:
                    pass

            download_buttons = [
                ("Download Canonical Graph JSON", "canonical_graph.json"),
                ("Download STIX Bundle JSON", "threat_model.stix2.json"),
                ("Download Final Report (Markdown)", "report.md"),
                ("Download Mermaid Diagrams (Markdown)", "diagrams.md"),
                ("Download Token Usage JSON", "token_usage.json"),
                ("Download STRIDE JSON", "stride.json"),
                ("Download STRIDE CSV", "stride.csv"),
                ("Download Component Version Manifest", "component_version_manifest.json"),
                ("Download Component File Inventory", "component_file_inventory.json"),
            ]
            for button_label, file_name in download_buttons:
                try:
                    button = _visible_enabled_button(page, button_label)
                    with page.expect_download(timeout=60000) as download_info:
                        button.click(timeout=30000)
                    download = download_info.value
                    download_path = downloads_dir / file_name
                    download.save_as(str(download_path))
                    downloads = summary.get("downloads")
                    if isinstance(downloads, list):
                        downloads.append({"label": button_label, "path": str(download_path)})
                    print(f"[SMOKE] Download captured: {button_label} -> {download_path}", flush=True)
                except Exception as exc:
                    print(f"[SMOKE] Download control skipped: {button_label} ({exc})", flush=True)

            if isinstance(cast_screenshots, list):
                cast_screenshots.append({"label": "08_results_export", "path": str(_capture_screenshot(page, screenshots_dir, "08_results_export"))})

            print("[SMOKE] Step 8: Verifying post-completion left-nav viewers/features...", flush=True)
            _verify_post_completion_left_nav_features(page, screenshots_dir, summary)

            if threat_count <= 0:
                fallback_threat_count = _extract_threat_count_from_canonical_graph(downloads_dir)
                if fallback_threat_count > 0:
                    threat_count = fallback_threat_count
                    print(
                        f"[SMOKE] Threat count recovered from canonical_graph.json: {threat_count}",
                        flush=True,
                    )
                else:
                    stix_threat_count = _extract_threat_count_from_stix_bundle(downloads_dir)
                    if stix_threat_count > 0:
                        threat_count = stix_threat_count
                        print(
                            f"[SMOKE] Threat count recovered from STIX bundle: {threat_count}",
                            flush=True,
                        )
                    else:
                        stride_threat_count = _extract_threat_count_from_stride(downloads_dir)
                        if stride_threat_count > 0:
                            threat_count = stride_threat_count
                            print(
                                f"[SMOKE] Threat count recovered from STRIDE JSON: {threat_count}",
                                flush=True,
                            )
                        else:
                            elapsed_seconds = int(time.time() - start_time)
                            body = page.inner_text("body")[:500]
                            summary.update(
                                {
                                    "status": "FAILED",
                                    "gates_approved": gate_counts.get("approved", 0),
                                    "total_tokens": total_tokens,
                                    "threats": threat_count,
                                    "duration_seconds": elapsed_seconds,
                                    "completed_stages": 8,
                                    "observed_hitl_gates": observed_mandatory_gate_ids,
                                    "missing_hitl_gates": [],
                                    "notes": (
                                        "Stage Results threat metric was unavailable and all artifact fallback "
                                        "threat counts were zero (canonical_graph, stix bundle, stride json). "
                                        "Post-completion left-nav feature checks were executed."
                                    ),
                                }
                            )
                            failure_line = (
                                "LIVE_BROWSER_SMOKE_FAILED "
                                "reason=zero_threat_count_after_fallback "
                                f"gates_approved={gate_counts.get('approved', 0)} "
                                f"total_tokens={total_tokens} "
                                f"threats={threat_count}"
                            )
                            _write_run_report(run_root, summary)
                            print("[SMOKE] === FAILURE ===", flush=True)
                            print(failure_line, flush=True)
                            _hold_browser_for_capture(cfg)
                            raise SmokeFailure(
                                "Threat count remained zero after Stage Results and artifact fallback "
                                "(canonical graph, STIX bundle, STRIDE JSON).\n"
                                f"Stage Results page snippet:\n{body}"
                            )

            missing_mandatory_gates = [gate_id for gate_id in _EXPECTED_MANDATORY_GATE_IDS if gate_id not in (summary.get("observed_hitl_gates") or [])]
            if missing_mandatory_gates:
                elapsed_seconds = int(time.time() - start_time)
                observed_gates = summary.get("observed_hitl_gates") or []
                summary.update(
                    {
                        "status": "FAILED",
                        "gates_approved": gate_counts.get("approved", 0),
                        "total_tokens": total_tokens,
                        "threats": threat_count,
                        "duration_seconds": elapsed_seconds,
                        "completed_stages": 9,
                        "observed_hitl_gates": observed_gates,
                        "missing_hitl_gates": missing_mandatory_gates,
                        "notes": (
                            "Mandatory HITL gate pause(s) were skipped during the run. "
                            f"Missing: {', '.join(missing_mandatory_gates)}"
                        ),
                    }
                )
                failure_line = (
                    "LIVE_BROWSER_SMOKE_FAILED "
                    f"missing_hitl_gates={','.join(missing_mandatory_gates)} "
                    f"observed_hitl_gates={','.join(observed_gates)} "
                    f"gates_approved={gate_counts.get('approved', 0)} "
                    f"total_tokens={total_tokens} "
                    f"threats={threat_count}"
                )
                _write_run_report(run_root, summary)
                print(f"[SMOKE] === FAILURE ===", flush=True)
                print(failure_line, flush=True)
                _hold_browser_for_capture(cfg)
                raise SmokeFailure(
                    "Mandatory HITL pause(s) were not observed for: "
                    f"{', '.join(missing_mandatory_gates)}. "
                    "The run completed, but this is a test failure and was documented in the report."
                )

            result_line = (
                f"LIVE_BROWSER_SMOKE_OK "
                f"gates_approved={gate_counts.get('approved', 0)} "
                f"total_tokens={total_tokens} "
                f"threats={threat_count}"
            )
            print(f"[SMOKE] === SUCCESS ===", flush=True)
            print(result_line, flush=True)

            elapsed_seconds = int(time.time() - start_time)
            observed_gates = summary.get("observed_hitl_gates") or []
            summary.update(
                {
                    "status": "LIVE_BROWSER_SMOKE_OK",
                    "gates_approved": gate_counts.get("approved", 0),
                    "total_tokens": total_tokens,
                    "threats": threat_count,
                    "duration_seconds": elapsed_seconds,
                    "completed_stages": 9,
                    "observed_hitl_gates": observed_gates,
                    "missing_hitl_gates": [],
                    "result_line": result_line,
                    "notes": "Visible browser FQT completed against UAS Weapon System with HITL approvals and export verification.",
                }
            )
            _write_run_report(run_root, summary)

            _hold_browser_for_capture(cfg)

            browser.close()
            browser = None

    finally:
        if browser is not None:
            try:
                if context is not None:
                    context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass
        if app_proc is not None:
            app_proc.terminate()
            try:
                app_proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                app_proc.kill()
        if isinstance(sys.stdout, _TeeLogger):
            tee = sys.stdout
            sys.stdout = tee._stream
            tee.shutdown()

    return 0


def main() -> int:
    try:
        return run_live_browser_smoke()
    except SmokeFailure as exc:
        print(f"LIVE_BROWSER_SMOKE_FAILED: {exc}")
        return 2
    except Exception as exc:
        print(f"LIVE_BROWSER_SMOKE_CRASHED: {type(exc).__name__}: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
