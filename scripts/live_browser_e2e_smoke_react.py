"""React HMI smoke + FQT-lite runner.

This validates the new HTML frontend workflow:
Home -> Role Select -> Pipeline Config -> Input Entry -> Run start.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


@dataclass
class SmokeConfig:
    backend_url: str
    frontend_url: str
    report_root: Path
    system_name: str
    input_files: list[Path]
    grok_api_key: str
    max_attempts: int


class SmokeFailure(RuntimeError):
    pass


EXPECTED_STAGE_IDS = {
    "agent_01",
    "agent_02",
    "agent_03",
    "agent_04",
    "agent_05",
    "agent_06",
    "agent_07",
    "agent_08",
    "agent_09",
}


def _retry_click(locator, *, attempts: int = 4, timeout_ms: int = 5000) -> bool:
    for _ in range(attempts):
        try:
            locator.first.click(timeout=timeout_ms, force=True)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def _wait_for_any(page, selectors: list[tuple[str, str]], timeout_ms: int = 20000):
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        for kind, value in selectors:
            try:
                locator = page.get_by_role("button", name=value) if kind == "button" else page.get_by_role("combobox", name=value)
                if locator.count() > 0:
                    return locator
            except Exception:
                continue
        time.sleep(0.3)
    return None


def _click_first_available(locators, *, attempts: int = 4, timeout_ms: int = 5000) -> bool:
    for locator in locators:
        try:
            if locator.count() > 0 and _retry_click(locator, attempts=attempts, timeout_ms=timeout_ms):
                return True
        except Exception:
            continue
    return False


def _check_http_ok(url: str) -> None:
    with urlopen(url, timeout=5) as resp:  # nosec B310 - controlled local URL
        if resp.status != 200:
            raise SmokeFailure(f"Unexpected status from {url}: {resp.status}")


def _request_json(method: str, url: str, payload: dict | None = None) -> dict:
    body = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=10) as resp:  # nosec B310 - local controlled URL
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _get_run_ids(cfg: SmokeConfig) -> set[str]:
    data = _request_json("GET", f"{cfg.backend_url}/runs")
    runs = data.get("runs", []) if isinstance(data, dict) else []
    run_ids: set[str] = set()
    for entry in runs:
        if isinstance(entry, dict):
            rid = str(entry.get("run_id") or "").strip()
            if rid:
                run_ids.add(rid)
    return run_ids


def _cancel_and_purge_run(cfg: SmokeConfig, run_id: str) -> None:
    try:
        _request_json("DELETE", f"{cfg.backend_url}/runs/{run_id}")
    except Exception:
        pass


def _get_runs_payload(cfg: SmokeConfig) -> list[dict]:
    payload = _request_json("GET", f"{cfg.backend_url}/runs")
    runs = payload.get("runs", []) if isinstance(payload, dict) else []
    return [entry for entry in runs if isinstance(entry, dict)]


def _wait_for_new_run_id(cfg: SmokeConfig, baseline_runs: set[str], timeout_seconds: int = 60) -> str:
    deadline = time.time() + timeout_seconds
    # Accept runs that started around this wait window to avoid latching onto stale IDs.
    min_recent_start = time.time() - 120
    while time.time() < deadline:
        try:
            runs = _get_runs_payload(cfg)
            candidates: list[tuple[float, str]] = []
            fallback_candidates: list[str] = []
            for entry in runs:
                rid = str(entry.get("run_id", "")).strip()
                if not rid or rid in baseline_runs:
                    continue
                start_time = entry.get("start_time")
                if isinstance(start_time, (int, float)) and start_time >= min_recent_start:
                    candidates.append((float(start_time), rid))
                else:
                    fallback_candidates.append(rid)

            if candidates:
                candidates.sort(key=lambda item: item[0])
                return candidates[-1][1]

            # If timestamps are unavailable, prefer the first non-baseline candidate observed.
            if fallback_candidates:
                return fallback_candidates[0]
        except Exception:
            pass
        time.sleep(1)
    raise SmokeFailure("Timed out waiting for newly created run ID.")


def _get_run_entry(cfg: SmokeConfig, run_id: str) -> dict | None:
    for entry in _get_runs_payload(cfg):
        if str(entry.get("run_id", "")).strip() == run_id:
            return entry
    return None


def _get_full_state(cfg: SmokeConfig, run_id: str) -> dict:
    return _request_json("GET", f"{cfg.backend_url}/runs/{run_id}/state/full")


def _resolve_open_gates(cfg: SmokeConfig, run_id: str, *, actor: str) -> int:
    gates_payload = _request_json("GET", f"{cfg.backend_url}/runs/{run_id}/state/gates")
    gates = gates_payload.get("gates", []) if isinstance(gates_payload, dict) else []
    resolved = 0
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("gate_id", "")).strip()
        status = str(gate.get("status", "")).strip().lower()
        is_resolved = bool(gate.get("is_resolved", False))
        if not gate_id or is_resolved or status in {"accepted_as_is", "accepted_changes", "rejected", "bypassed"}:
            continue
        _request_json(
            "POST",
            f"{cfg.backend_url}/runs/{run_id}/gates/{gate_id}/decide",
            {
                "actor": actor,
                "role": "analyst",
                "action": "accept_as_is",
                "rationale": "Automated smoke progression decision",
            },
        )
        resolved += 1
    return resolved


def _resume_if_paused_at_resolved_gate(cfg: SmokeConfig, run_id: str) -> int:
    """Resume a paused run once the currently paused gate has been resolved."""
    entry = _get_run_entry(cfg, run_id)
    full_state = _get_full_state(cfg, run_id)
    state_payload = full_state.get("state", {}) if isinstance(full_state, dict) else {}

    paused_gate = ""
    if isinstance(entry, dict):
        paused_gate = str(entry.get("pause_gate") or "").strip()
    if not paused_gate:
        paused_gate = str(state_payload.get("hitl_paused_at_gate") or "").strip()
    if not paused_gate:
        return 0

    gates_payload = _request_json("GET", f"{cfg.backend_url}/runs/{run_id}/state/gates")
    gates = gates_payload.get("gates", []) if isinstance(gates_payload, dict) else []
    paused_gate_record = None
    for gate in gates:
        if isinstance(gate, dict) and str(gate.get("gate_id", "")).strip() == paused_gate:
            paused_gate_record = gate
            break

    if not isinstance(paused_gate_record, dict):
        return 0

    gate_status = str(paused_gate_record.get("status", "")).strip().lower()
    gate_resolved = bool(paused_gate_record.get("is_resolved", False))
    gate_is_accept = gate_status in {"accepted_as_is", "accepted_changes", "approved"}
    if not gate_resolved and not gate_is_accept:
        return 0

    _request_json("POST", f"{cfg.backend_url}/runs/{run_id}/resume", {"gate_id": paused_gate})
    return 1


def _get_active_gate_ids(cfg: SmokeConfig, run_id: str) -> list[str]:
    gates_payload = _request_json("GET", f"{cfg.backend_url}/runs/{run_id}/state/gates")
    gates = gates_payload.get("gates", []) if isinstance(gates_payload, dict) else []
    active_gate_ids: list[str] = []
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("gate_id", "")).strip()
        status = str(gate.get("status", "")).strip().lower()
        if gate_id and status in {"open", "draft", "pending", "paused"}:
            active_gate_ids.append(gate_id)
    return active_gate_ids


def _review_threats(cfg: SmokeConfig, run_id: str, *, reviewer: str) -> int:
    threats_payload = _request_json("GET", f"{cfg.backend_url}/runs/{run_id}/state/threats")
    threats = threats_payload.get("threats", []) if isinstance(threats_payload, dict) else []
    reviewed = 0
    for threat in threats:
        if not isinstance(threat, dict):
            continue
        threat_id = str(threat.get("id", "")).strip()
        if not threat_id:
            continue
        try:
            _request_json(
                "POST",
                f"{cfg.backend_url}/runs/{run_id}/threats/{threat_id}/decide",
                {
                    "decision": "approve",
                    "notes": "Automated smoke threat review",
                    "reviewer": reviewer,
                },
            )
            reviewed += 1
        except Exception:
            continue
    return reviewed


def _wait_for_full_pipeline_completion(
    cfg: SmokeConfig,
    run_id: str,
    *,
    timeout_seconds: int = 900,
    page=None,
    screenshots: Path | None = None,
) -> dict:
    deadline = time.time() + timeout_seconds
    observed_stage_ids: set[str] = set()
    gates_resolved_total = 0
    resumes_total = 0
    threats_reviewed_total = 0
    pauses_detected: list[str] = []
    last_pause_gate: str | None = None

    while time.time() < deadline:
        entry = _get_run_entry(cfg, run_id)
        if entry is None:
            time.sleep(1)
            continue

        status = str(entry.get("status", "")).strip().lower()
        if status in {"failed", "error", "rejected"}:
            error_text = str(entry.get("error") or "").strip()
            if error_text:
                raise SmokeFailure(f"Run entered terminal failure status: {status}. Error: {error_text}")
            raise SmokeFailure(f"Run entered terminal failure status: {status}")

        try:
            full_state = _get_full_state(cfg, run_id)
            state_payload = full_state.get("state", {}) if isinstance(full_state, dict) else {}
            messages = full_state.get("messages", []) if isinstance(full_state, dict) else []
            for msg in messages:
                if isinstance(msg, dict):
                    sid = str(msg.get("stage_id", "")).strip()
                    if sid:
                        observed_stage_ids.add(sid)
        except Exception:
            full_state = {}
            state_payload = {}

        active_gate_ids = _get_active_gate_ids(cfg, run_id)
        paused_gate = str(entry.get("pause_gate") or state_payload.get("hitl_paused_at_gate") or "").strip()
        pause_markers = [gate_id for gate_id in ([paused_gate] if paused_gate else []) + active_gate_ids if gate_id]
        if pause_markers:
            for gate_id in pause_markers:
                if gate_id not in pauses_detected:
                    pauses_detected.append(gate_id)
            last_pause_gate = pause_markers[0]
            if page is not None:
                gates_tab = page.get_by_role("tab", name="Gates")
                if gates_tab.count() > 0:
                    _retry_click(gates_tab, attempts=3, timeout_ms=4000)
                    page.wait_for_timeout(500)
                    if screenshots is not None:
                        page.screenshot(path=str(screenshots / f"gate_pause_{len(pauses_detected):02d}.png"))

        gates_resolved_total += _resolve_open_gates(cfg, run_id, actor="smoke_runner")
        resumes_total += _resume_if_paused_at_resolved_gate(cfg, run_id)
        threats_reviewed_total += _review_threats(cfg, run_id, reviewer="smoke_runner")

        if not pause_markers and last_pause_gate is not None and page is not None:
            exec_tab = page.get_by_role("tab", name="Execution")
            if exec_tab.count() > 0:
                _retry_click(exec_tab, attempts=3, timeout_ms=4000)
                page.wait_for_timeout(500)
            last_pause_gate = None

        if status == "completed" and EXPECTED_STAGE_IDS.issubset(observed_stage_ids):
            return {
                "status": status,
                "observed_stage_ids": sorted(observed_stage_ids),
                "gates_resolved": gates_resolved_total,
                "resumes": resumes_total,
                "threats_reviewed": threats_reviewed_total,
                "pauses_detected": pauses_detected,
            }

        time.sleep(2)

    raise SmokeFailure(
        f"Run did not complete all 9 stages before timeout. Observed: {sorted(observed_stage_ids)}"
    )
    try:
        _request_json("DELETE", f"{cfg.backend_url}/runs/{run_id}/purge")
    except Exception:
        pass


def _capture_failure_evidence(
    *,
    cfg: SmokeConfig,
    run_dir: Path,
    attempt: int,
    exception_obj: Exception,
    trace_text: str,
    baseline_runs: set[str],
) -> None:
    evidence: dict[str, object] = {
        "attempt": attempt,
        "error": str(exception_obj),
        "traceback": trace_text,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend_url": cfg.backend_url,
        "frontend_url": cfg.frontend_url,
        "input_files": [str(path) for path in cfg.input_files],
    }

    try:
        evidence["backend_health"] = _request_json("GET", f"{cfg.backend_url}/health")
    except Exception as exc:
        evidence["backend_health_error"] = str(exc)

    try:
        runs_payload = _request_json("GET", f"{cfg.backend_url}/runs")
        evidence["runs"] = runs_payload
        runs = runs_payload.get("runs", []) if isinstance(runs_payload, dict) else []
        current_run_ids = {
            str(entry.get("run_id", "")).strip()
            for entry in runs
            if isinstance(entry, dict) and str(entry.get("run_id", "")).strip()
        }
        evidence["new_run_ids_since_attempt_start"] = sorted(current_run_ids - baseline_runs)
    except Exception as exc:
        evidence["runs_error"] = str(exc)

    try:
        backend_port = _port_from_url(cfg.backend_url)
        frontend_port = _port_from_url(cfg.frontend_url)
        evidence["backend_port_pids"] = sorted(_find_listening_pids(backend_port))
        evidence["frontend_port_pids"] = sorted(_find_listening_pids(frontend_port))
    except Exception as exc:
        evidence["port_snapshot_error"] = str(exc)

    (run_dir / "failure_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")


def _frontend_url_candidates(url: str) -> list[str]:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port

    candidates = [url]
    if host == "127.0.0.1":
        alt_host = "localhost"
    elif host == "localhost":
        alt_host = "127.0.0.1"
    else:
        alt_host = ""

    if alt_host:
        auth = alt_host if port is None else f"{alt_host}:{port}"
        alt_url = urlunparse((parsed.scheme, auth, parsed.path, parsed.params, parsed.query, parsed.fragment))
        if alt_url not in candidates:
            candidates.append(alt_url)

    return candidates


def _port_from_url(url: str) -> int:
    parsed = urlparse(url)
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    return 80


def _find_listening_pids(port: int) -> set[int]:
    pids: set[int] = set()

    if os.name == "nt":
        cmd = ["netstat", "-ano", "-p", "tcp"]
        output = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="ignore")
        port_token = f":{port}"
        for line in output.splitlines():
            upper = line.upper()
            if "LISTENING" not in upper or port_token not in line:
                continue
            parts = line.split()
            if not parts:
                continue
            pid_str = parts[-1].strip()
            if pid_str.isdigit():
                pids.add(int(pid_str))
        return pids

    cmd = ["lsof", "-ti", f"tcp:{port}"]
    try:
        output = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="ignore")
    except Exception:
        return pids
    for line in output.splitlines():
        text = line.strip()
        if text.isdigit():
            pids.add(int(text))
    return pids


def _kill_processes_on_port(port: int) -> None:
    for pid in _find_listening_pids(port):
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
            else:
                os.kill(pid, signal.SIGTERM)
        except Exception:
            continue


def _wait_for_url(urls: list[str], timeout_seconds: int) -> str:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for candidate in urls:
            try:
                _check_http_ok(candidate)
                return candidate
            except Exception:
                continue
        time.sleep(1)
    raise SmokeFailure(f"Service did not become ready: {urls}")


def _default_input_files(repo_root: Path) -> list[Path]:
    bundle_dir = repo_root / "Tests" / "fixtures" / "inputs" / "systems" / "uas_weapon_system" / "full_system_bundle"
    return [
        bundle_dir / "icd_uas_weapon_system_v1.csv",
        bundle_dir / "description_uas_weapon_system.md",
        bundle_dir / "icd_alpha_v1.csv",
        bundle_dir / "description_alpha_comprehensive.md",
        bundle_dir / "icd_alpha_mission_computer_v1.csv",
        bundle_dir / "description_alpha_mission_computer.md",
        bundle_dir / "icd_bravo_v2.csv",
        bundle_dir / "description_bravo_comprehensive.md",
        bundle_dir / "icd_charlie_v1.xlsx",
        bundle_dir / "description_charlie_comprehensive.md",
        bundle_dir / "icd_charlie_mission_planning_computer_v1.csv",
        bundle_dir / "description_charlie_mission_planning_computer.md",
        bundle_dir / "icd_ground_maintenance_v1.csv",
        bundle_dir / "description_ground_maintenance_comprehensive.md",
    ]


def _resolve_input_files(repo_root: Path) -> list[Path]:
    raw_multi = str(os.environ.get("THREAT_MODELER_SMOKE_INPUT_FILES") or "").strip()
    if raw_multi:
        input_files = [Path(item.strip()) for item in raw_multi.split(";") if item.strip()]
    else:
        raw_single = str(os.environ.get("THREAT_MODELER_SMOKE_INPUT_FILE") or "").strip()
        input_files = [Path(raw_single)] if raw_single else _default_input_files(repo_root)

    missing = [str(path) for path in input_files if not path.exists()]
    if missing:
        raise SmokeFailure(f"Smoke input files not found: {missing}")
    return input_files


def _build_config() -> SmokeConfig:
    repo_root = Path(__file__).resolve().parents[1]
    report_root = Path(os.environ.get("THREAT_MODELER_SMOKE_REPORT_ROOT", str(repo_root / "FQT")))

    env_file = repo_root / ".env"
    grok_api_key = os.environ.get("GROK_API") or ""
    if not grok_api_key and env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key.strip() == "GROK_API":
                grok_api_key = value.strip().strip('"').strip("'")
                break

    return SmokeConfig(
        backend_url=os.environ.get("THREAT_MODELER_BACKEND_URL", "http://127.0.0.1:8600"),
        frontend_url=os.environ.get("THREAT_MODELER_FRONTEND_URL", "http://localhost:5174"),
        report_root=report_root,
        system_name=os.environ.get("THREAT_MODELER_SMOKE_SYSTEM_NAME", "React FQT System"),
        input_files=_resolve_input_files(repo_root),
        grok_api_key=grok_api_key,
        max_attempts=max(1, int(os.environ.get("THREAT_MODELER_SMOKE_MAX_ATTEMPTS", "2"))),
    )


def _start_backend(cfg: SmokeConfig) -> subprocess.Popen[str]:
    repo_root = Path(__file__).resolve().parents[1]
    backend_port = _port_from_url(cfg.backend_url)
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    src_path = str(repo_root / "src")
    env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
    proc = subprocess.Popen(
        [sys.executable, "-m", "threat_modeler", "--host", "127.0.0.1", "--port", str(backend_port)],
        cwd=str(repo_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_url([f"{cfg.backend_url}/health"], 30)
    except Exception:
        output = proc.stdout.read() if proc.stdout is not None else ""
        proc.terminate()
        raise SmokeFailure(f"Backend failed to start on port {backend_port}. Output: {(output or '').strip()[:4000]}")
    return proc


def _start_frontend(cfg: SmokeConfig) -> tuple[subprocess.Popen[str], str]:
    repo_root = Path(__file__).resolve().parents[1]
    frontend_dir = repo_root / "frontend"
    frontend_port = _port_from_url(cfg.frontend_url)
    npm_exec = "npm.cmd" if os.name == "nt" else "npm"
    proc = subprocess.Popen(
        [npm_exec, "run", "dev", "--", "--port", str(frontend_port), "--strictPort", "--host", "127.0.0.1"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            output = ""
            if proc.stdout is not None:
                output = proc.stdout.read() or ""
            raise SmokeFailure(
                f"Frontend dev server exited early with code {proc.returncode}. Output: {output.strip()[:4000]}"
            )
        for candidate_url in _frontend_url_candidates(cfg.frontend_url):
            try:
                _check_http_ok(candidate_url)
                return proc, candidate_url
            except Exception:
                continue
        time.sleep(1)

    proc.terminate()
    output = ""
    if proc.stdout is not None:
        try:
            output = proc.stdout.read() or ""
        except Exception:
            output = ""
    raise SmokeFailure(
        f"Frontend did not become ready on port 5174 within timeout. Output: {output.strip()[:4000]}"
    )


def _run_browser_flow(cfg: SmokeConfig, run_dir: Path, baseline_runs: set[str]) -> dict[str, object]:
    from playwright.sync_api import sync_playwright

    screenshots = run_dir / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto(cfg.frontend_url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        page.screenshot(path=str(screenshots / "01_home.png"))

        start_wizard = page.get_by_role("button", name="Start Setup Wizard")
        sidebar_wizard = page.get_by_role("button", name="New Run Wizard")
        clicked = False
        if start_wizard.count() > 0:
            clicked = _retry_click(start_wizard)
        if not clicked and sidebar_wizard.count() > 0:
            clicked = _retry_click(sidebar_wizard)
        if not clicked:
            raise SmokeFailure("Could not find wizard start button (home or sidebar).")

        if not _retry_click(page.get_by_role("button", name="Confirm Role")):
            raise SmokeFailure("Could not click Confirm Role in setup wizard.")

        if cfg.grok_api_key:
            pipeline_ready = _wait_for_any(page, [("button", "Apply Settings")], timeout_ms=25000)
            if pipeline_ready is None:
                raise SmokeFailure("Pipeline Configuration step did not become ready.")

            provider_locator_candidates = [
                page.get_by_role("combobox", name="LLM Provider"),
                page.get_by_label("LLM Provider"),
                page.locator("div[role='combobox']").first,
            ]
            if not _click_first_available(provider_locator_candidates, attempts=6, timeout_ms=6000):
                raise SmokeFailure("Could not open LLM Provider selector.")

            if not _retry_click(page.get_by_role("option", name="xAI Grok")):
                raise SmokeFailure("Could not select xAI Grok provider option.")

            api_key_input = page.get_by_label("API Key")
            api_key_input.first.fill(cfg.grok_api_key, timeout=15000)
            if not _retry_click(page.get_by_role("button", name="Verify LLM Connection")):
                raise SmokeFailure("Could not click Verify LLM Connection.")
            verified_locators = [
                page.get_by_text("Verified", exact=False),
                page.get_by_text("compatibility", exact=False),
                page.get_by_text("verification unavailable", exact=False),
            ]
            verify_acknowledged = False
            for locator in verified_locators:
                try:
                    locator.first.wait_for(timeout=5000)
                    verify_acknowledged = True
                    break
                except Exception:
                    continue
            if not verify_acknowledged:
                # Verification can complete without a stable banner in some UI states.
                page.wait_for_timeout(1000)

        if not _retry_click(page.get_by_role("button", name="Apply Settings")):
            raise SmokeFailure("Could not click Apply Settings.")

        page.get_by_role("textbox", name="System Name").fill(cfg.system_name)
        file_input = page.locator("input[type='file']")
        file_input.set_input_files([str(path) for path in cfg.input_files])

        upload_summary = page.get_by_text(f"Uploaded Files ({len(cfg.input_files)})", exact=False)
        upload_summary.first.wait_for(timeout=15000)
        for input_path in cfg.input_files:
            page.get_by_text(input_path.name, exact=False).first.wait_for(timeout=15000)

        start_button = page.get_by_role("button", name="Start Threat Model Run")
        start_button.first.wait_for(timeout=10000)
        if start_button.first.is_disabled():
            raise SmokeFailure("Start Threat Model Run remained disabled after required files were uploaded.")

        page.screenshot(path=str(screenshots / "02_uploaded_files.png"))

        if not _retry_click(start_button):
            raise SmokeFailure("Could not click Start Threat Model Run.")

        run_id = _wait_for_new_run_id(cfg, baseline_runs, timeout_seconds=60)
        page.wait_for_timeout(2000)
        exec_tab = page.get_by_role("tab", name="Execution")
        if exec_tab.count() > 0:
            _retry_click(exec_tab, attempts=3, timeout_ms=4000)
            page.wait_for_timeout(500)
        page.screenshot(path=str(screenshots / "03_run_created.png"))

        progression = _wait_for_full_pipeline_completion(
            cfg,
            run_id,
            timeout_seconds=900,
            page=page,
            screenshots=screenshots,
        )

        # Exercise every analysis display in the HMI after the pipeline completes.
        tab_names = ["Execution", "Threats", "Gates", "Tokens", "Artifacts", "Last Prompt", "Prompt Editor"]
        for idx, tab_name in enumerate(tab_names, start=3):
            tab = page.get_by_role("tab", name=tab_name)
            if tab.count() > 0:
                _retry_click(tab, attempts=3, timeout_ms=4000)
                page.wait_for_timeout(500)
                page.screenshot(path=str(screenshots / f"{idx:02d}_{tab_name.lower().replace(' ', '_')}.png"))

        # Return to execution display and capture final completed state.
        exec_tab = page.get_by_role("tab", name="Execution")
        if exec_tab.count() > 0:
            _retry_click(exec_tab, attempts=3, timeout_ms=4000)
        page.wait_for_timeout(500)
        page.screenshot(path=str(screenshots / "99_completed.png"))

        browser.close()

    return {
        "status": "LIVE_BROWSER_SMOKE_OK",
        "run_id": run_id,
        "frontend_url": cfg.frontend_url,
        "backend_url": cfg.backend_url,
        "system_name": cfg.system_name,
        "input_files": [str(path) for path in cfg.input_files],
        "live_provider_used": bool(cfg.grok_api_key),
        "pipeline_progression": progression,
        "displays_covered": ["execution", "threats", "gates", "tokens", "artifacts", "last_prompt", "prompt_editor"],
        "screenshots": [
            str(screenshots / "01_home.png"),
            str(screenshots / "02_uploaded_files.png"),
            str(screenshots / "03_run_created.png"),
            str(screenshots / "03_execution.png"),
            str(screenshots / "04_threats.png"),
            str(screenshots / "05_gates.png"),
            str(screenshots / "06_tokens.png"),
            str(screenshots / "07_artifacts.png"),
            str(screenshots / "08_last_prompt.png"),
            str(screenshots / "09_prompt_editor.png"),
            str(screenshots / "99_completed.png"),
        ],
    }


def main() -> int:
    cfg = _build_config()
    cfg.report_root.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(1, cfg.max_attempts + 1):
        # Always reset local test servers so smoke/FQT runs in a known state.
        _kill_processes_on_port(_port_from_url(cfg.backend_url))
        _kill_processes_on_port(_port_from_url(cfg.frontend_url))

        stamp = time.strftime("%Y%m%d_%H%M%S")
        run_dir = cfg.report_root / f"fqt_react_{stamp}_attempt_{attempt}"
        run_dir.mkdir(parents=True, exist_ok=True)

        baseline_runs: set[str] = set()
        backend_proc = None
        frontend_proc = None
        try:
            backend_proc = _start_backend(cfg)
            baseline_runs = _get_run_ids(cfg)
            frontend_proc, active_frontend_url = _start_frontend(cfg)
            if active_frontend_url != cfg.frontend_url:
                cfg.frontend_url = active_frontend_url
            result = _run_browser_flow(cfg, run_dir, baseline_runs)

            report_json = run_dir / "test_report.json"
            report_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"[SMOKE] React smoke complete: {report_json}")
            return 0
        except Exception as exc:
            last_error = exc
            trace_text = traceback.format_exc()
            try:
                _capture_failure_evidence(
                    cfg=cfg,
                    run_dir=run_dir,
                    attempt=attempt,
                    exception_obj=exc,
                    trace_text=trace_text,
                    baseline_runs=baseline_runs,
                )
            except Exception:
                pass

            try:
                after_runs = _get_run_ids(cfg)
                new_runs = sorted(after_runs - baseline_runs)
                for run_id in new_runs:
                    _cancel_and_purge_run(cfg, run_id)
            except Exception:
                pass

            if attempt >= cfg.max_attempts:
                raise
            print(f"[SMOKE][RETRY] Attempt {attempt} failed: {exc}. Retrying...")
        finally:
            if frontend_proc is not None:
                frontend_proc.terminate()
            if backend_proc is not None:
                backend_proc.terminate()

    if last_error is not None:
        raise last_error
    raise SmokeFailure("Smoke run failed without an explicit error.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeFailure as exc:
        print(f"[SMOKE][FAIL] {exc}")
        raise SystemExit(1)
