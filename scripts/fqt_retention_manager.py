from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUCCESS_STATUS = "LIVE_BROWSER_SMOKE_OK"


@dataclass
class RunRecord:
    run_name: str
    run_path: Path
    has_test_report: bool
    has_failure_evidence: bool
    has_screenshots: bool
    file_count: int
    status: str
    raw_error: str
    signature: str
    first_seen: str
    classification: str
    action: str
    archive_target: str
    canonical_reason: str


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _extract_failure_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []

    top_error = payload.get("error")
    if isinstance(top_error, str) and top_error.strip():
        parts.append(top_error)

    runs = payload.get("runs")
    if isinstance(runs, dict):
        run_list = runs.get("runs")
        if isinstance(run_list, list):
            for item in run_list:
                if not isinstance(item, dict):
                    continue
                run_error = item.get("error")
                if isinstance(run_error, str) and run_error.strip():
                    parts.append(run_error)

    if not parts:
        try:
            return json.dumps(payload)
        except Exception:
            return ""

    return "\n".join(parts)


def _extract_timestamp_from_name(name: str) -> str:
    m = re.search(r"(\d{8}_\d{6})", name)
    if not m:
        return "99999999_999999"
    return m.group(1)


def _normalize_signature(status: str, raw_error: str, has_failure_evidence: bool, has_screenshots: bool, file_count: int) -> str:
    text = (raw_error or "").lower()

    if status == SUCCESS_STATUS:
        return "SUCCESS"

    if "provider http error 429" in text or "at capacity" in text or "resource has been exhausted" in text:
        return "FAIL_PROVIDER_429_CAPACITY"

    if "waiting for get_by_text(\"verified\")" in text or "locator.wait_for: timeout" in text:
        return "FAIL_UI_TIMEOUT_VERIFIED"

    if "live adapter required" in text and "adapter is missing" in text:
        return "FAIL_LIVE_ADAPTER_MISSING"

    if has_failure_evidence:
        return "FAIL_OTHER_FROM_FAILURE_EVIDENCE"

    if status == "NO_REPORT" and has_screenshots and file_count <= 1:
        return "NO_REPORT_SCREENSHOTS_ONLY"

    if status == "NO_REPORT" and file_count == 0:
        return "NO_REPORT_EMPTY"

    if status == "NO_REPORT":
        return "NO_REPORT_UNKNOWN"

    return "FAIL_OTHER"


def _collect_runs(fqt_root: Path) -> list[RunRecord]:
    records: list[RunRecord] = []

    for entry in sorted(fqt_root.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir():
            continue
        if entry.name in {"retention", "archive_dedup"}:
            continue

        test_report = entry / "test_report.json"
        failure_evidence = entry / "failure_evidence.json"
        screenshots = entry / "screenshots"

        has_test_report = test_report.exists()
        has_failure = failure_evidence.exists()
        has_screenshots = screenshots.exists() and screenshots.is_dir()

        file_count = sum(1 for _ in entry.rglob("*") if _.is_file())

        status = "NO_REPORT"
        raw_error = ""

        if has_test_report:
            report = _safe_read_json(test_report)
            status = str(report.get("status") or "UNKNOWN")
            raw_error = str(report.get("error") or report.get("failure_reason") or "")

        if has_failure:
            evidence = _safe_read_json(failure_evidence)
            evidence_text = _extract_failure_text(evidence)
            if not raw_error:
                raw_error = evidence_text
            elif evidence_text:
                raw_error = f"{raw_error}\n{evidence_text}"

        signature = _normalize_signature(status, raw_error, has_failure, has_screenshots, file_count)

        records.append(
            RunRecord(
                run_name=entry.name,
                run_path=entry,
                has_test_report=has_test_report,
                has_failure_evidence=has_failure,
                has_screenshots=has_screenshots,
                file_count=file_count,
                status=status,
                raw_error=raw_error,
                signature=signature,
                first_seen=_extract_timestamp_from_name(entry.name),
                classification="",
                action="",
                archive_target="",
                canonical_reason="",
            )
        )

    return records


def _classify(records: list[RunRecord]) -> None:
    by_signature: dict[str, list[RunRecord]] = {}

    for rec in records:
        by_signature.setdefault(rec.signature, []).append(rec)

    for sig, group in by_signature.items():
        group.sort(key=lambda r: (r.first_seen, r.run_name))

        if sig == "SUCCESS":
            for rec in group:
                rec.classification = "KEEP_FULL"
                rec.action = "NOOP"
                rec.canonical_reason = "successful_run"
            continue

        if len(group) == 1:
            only = group[0]
            only.classification = "KEEP_FULL"
            only.action = "NOOP"
            only.canonical_reason = "only_example_for_signature"
            continue

        first = group[0]
        last = group[-1]

        for rec in group:
            if rec is first:
                rec.classification = "KEEP_FULL"
                rec.action = "NOOP"
                rec.canonical_reason = "canonical_first_for_signature"
            elif rec is last:
                rec.classification = "KEEP_FULL"
                rec.action = "NOOP"
                rec.canonical_reason = "canonical_last_for_signature"
            else:
                rec.classification = "SUMMARIZE_ONLY"
                rec.action = "ARCHIVE_WITH_POINTER"
                rec.canonical_reason = "duplicate_signature"


def _write_matrix(records: list[RunRecord], retention_dir: Path, stamp: str) -> tuple[Path, Path, Path]:
    retention_dir.mkdir(parents=True, exist_ok=True)

    matrix_md = retention_dir / f"fqt_retention_matrix_{stamp}.md"
    matrix_csv = retention_dir / f"fqt_retention_matrix_{stamp}.csv"
    manifest_json = retention_dir / f"fqt_retention_manifest_{stamp}.json"

    header = (
        "# FQT Retention Matrix\n\n"
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
        "| Run Folder | Status | Signature | Classification | Action | Notes |\n"
        "|---|---|---|---|---|---|\n"
    )

    lines = [header]
    for rec in sorted(records, key=lambda r: (r.first_seen, r.run_name)):
        notes = rec.canonical_reason or ""
        lines.append(
            f"| {rec.run_name} | {rec.status} | {rec.signature} | {rec.classification} | {rec.action} | {notes} |\n"
        )

    matrix_md.write_text("".join(lines), encoding="utf-8")

    with matrix_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "run_name",
                "status",
                "signature",
                "classification",
                "action",
                "canonical_reason",
                "has_test_report",
                "has_failure_evidence",
                "has_screenshots",
                "file_count",
            ]
        )
        for rec in sorted(records, key=lambda r: (r.first_seen, r.run_name)):
            writer.writerow(
                [
                    rec.run_name,
                    rec.status,
                    rec.signature,
                    rec.classification,
                    rec.action,
                    rec.canonical_reason,
                    rec.has_test_report,
                    rec.has_failure_evidence,
                    rec.has_screenshots,
                    rec.file_count,
                ]
            )

    manifest_payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "records": [
            {
                "run_name": rec.run_name,
                "status": rec.status,
                "signature": rec.signature,
                "classification": rec.classification,
                "action": rec.action,
                "canonical_reason": rec.canonical_reason,
                "has_test_report": rec.has_test_report,
                "has_failure_evidence": rec.has_failure_evidence,
                "has_screenshots": rec.has_screenshots,
                "file_count": rec.file_count,
            }
            for rec in sorted(records, key=lambda r: (r.first_seen, r.run_name))
        ],
    }
    manifest_json.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")

    return matrix_md, matrix_csv, manifest_json


def _apply_archive(records: list[RunRecord], fqt_root: Path, retention_dir: Path, stamp: str) -> Path:
    archive_root = fqt_root / "archive_dedup" / stamp
    archive_root.mkdir(parents=True, exist_ok=True)

    actions: list[dict[str, Any]] = []

    for rec in records:
        if rec.classification != "SUMMARIZE_ONLY":
            continue

        source = rec.run_path
        if not source.exists():
            continue

        target = archive_root / rec.run_name
        if target.exists():
            suffix = dt.datetime.now().strftime("%H%M%S")
            target = archive_root / f"{rec.run_name}_{suffix}"

        shutil.move(str(source), str(target))

        source.mkdir(parents=True, exist_ok=True)

        pointer = {
            "run_name": rec.run_name,
            "archived_at": dt.datetime.now().isoformat(timespec="seconds"),
            "archive_target": str(target.as_posix()),
            "classification": rec.classification,
            "signature": rec.signature,
            "canonical_reason": rec.canonical_reason,
            "original_action": rec.action,
        }
        (source / "MANIFEST_POINTER.json").write_text(json.dumps(pointer, indent=2), encoding="utf-8")

        rec.archive_target = str(target.as_posix())

        actions.append(pointer)

    action_log = retention_dir / f"fqt_archive_actions_{stamp}.json"
    action_log.write_text(
        json.dumps(
            {
                "applied_at": dt.datetime.now().isoformat(timespec="seconds"),
                "archive_root": str(archive_root.as_posix()),
                "actions": actions,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return action_log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify and archive duplicate FQT evidence non-destructively.")
    parser.add_argument("--fqt-root", default="FQT", help="Path to FQT root directory")
    parser.add_argument("--retention-dir", default="FQT/retention", help="Path to retention output directory")
    parser.add_argument("--apply", action="store_true", help="Apply non-destructive archive for summarize-only runs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fqt_root = Path(args.fqt_root).resolve()
    retention_dir = Path(args.retention_dir).resolve()

    if not fqt_root.exists() or not fqt_root.is_dir():
        raise SystemExit(f"FQT root does not exist or is not a directory: {fqt_root}")

    records = _collect_runs(fqt_root)
    _classify(records)

    stamp = dt.date.today().isoformat()
    md_path, csv_path, manifest_path = _write_matrix(records, retention_dir, stamp)

    print(f"Wrote matrix markdown: {md_path}")
    print(f"Wrote matrix csv: {csv_path}")
    print(f"Wrote manifest json: {manifest_path}")

    if args.apply:
        action_log = _apply_archive(records, fqt_root, retention_dir, stamp)
        print(f"Applied archive actions log: {action_log}")
    else:
        print("Dry run complete. Use --apply to archive summarize-only runs.")

    total = len(records)
    keep_full = sum(1 for r in records if r.classification == "KEEP_FULL")
    summarize = sum(1 for r in records if r.classification == "SUMMARIZE_ONLY")

    print(f"Total runs: {total}")
    print(f"KEEP_FULL: {keep_full}")
    print(f"SUMMARIZE_ONLY: {summarize}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
