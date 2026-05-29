#!/usr/bin/env python3
"""Generate a concise executive summary from an FQT retention manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate FQT retention executive summary.")
    parser.add_argument("--manifest", required=True, help="Path to fqt_retention_manifest_YYYY-MM-DD.json")
    parser.add_argument("--out", required=True, help="Output markdown path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    out_path = Path(args.out)

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = payload.get("records", [])

    total = len(records)
    by_class = Counter(rec.get("classification", "UNKNOWN") for rec in records)

    sig_rollup: dict[str, Counter] = defaultdict(Counter)
    for rec in records:
        sig = rec.get("signature", "UNKNOWN")
        sig_rollup[sig]["total"] += 1
        sig_rollup[sig][rec.get("classification", "UNKNOWN")] += 1

    lines: list[str] = []
    lines.append("# FQT Retention Executive Summary\n\n")
    lines.append(f"Source manifest: `{manifest_path.as_posix()}`\n\n")
    lines.append(f"Generated from manifest timestamp: {payload.get('generated_at', 'unknown')}\n\n")
    lines.append("## High-Level Totals\n\n")
    lines.append(f"- Total run folders evaluated: {total}\n")
    lines.append(f"- Keep full: {by_class.get('KEEP_FULL', 0)}\n")
    lines.append(f"- Summarize-only: {by_class.get('SUMMARIZE_ONLY', 0)}\n\n")

    lines.append("## Signature Rollup\n\n")
    lines.append("| Signature | Total | Keep Full | Summarize-Only |\n")
    lines.append("|---|---:|---:|---:|\n")

    for signature in sorted(sig_rollup.keys()):
        c = sig_rollup[signature]
        lines.append(
            f"| {signature} | {c.get('total', 0)} | {c.get('KEEP_FULL', 0)} | {c.get('SUMMARIZE_ONLY', 0)} |\n"
        )

    lines.append("\n## Governance Notes\n\n")
    lines.append("- Successful runs are retained in full for release confidence evidence.\n")
    lines.append("- Duplicate failures are reduced to pointer-backed archived evidence to control noise without losing traceability.\n")
    lines.append("- Canonical first/last examples per signature remain in active evidence scope.\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote executive summary: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
