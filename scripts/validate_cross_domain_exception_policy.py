#!/usr/bin/env python3
"""Validate cross-domain same-level interface exception governance policy."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

REQUIRED_EXCEPTION_COLUMNS = [
    "exception_id",
    "interface_id",
    "producer_function_id",
    "consumer_function_id",
    "producer_domain",
    "consumer_domain",
    "level_pair",
    "exception_class",
    "trust_boundary_classification",
    "rationale",
    "gate_targets",
    "gate_evidence_refs",
    "status",
    "disposition",
    "risk_acceptance_id",
    "mitigation_due_date",
    "approved_by",
    "approval_date",
    "threat_model_row_id",
    "vv_test_case_ids",
    "icd_section_ref",
    "schema_version",
]

ALLOWED_LEVEL_PAIRS = {"L1->L1", "L2->L2"}
ALLOWED_TRUST_BOUNDARIES = {
    "TB-CONTROL-INTERDOMAIN",
    "TB-DATA-INTERDOMAIN",
    "TB-MAINTENANCE-OFFBOARD",
    "TB-PASSENGER-SERVICE",
}
ALLOWED_DISPOSITIONS = {
    "proposed",
    "under_review",
    "accepted",
    "mitigated",
    "waived",
    "rejected",
    "closed",
}
ALLOWED_STATUSES = {"open", "in_progress", "closed"}
REQUIRED_EVIDENCE_TOKENS = {
    "EA-ICD",
    "EA-SCHEMA",
    "EA-TRUST-BOUNDARY-ANALYSIS",
    "EA-VV-TEST",
}


def _split_tokens(value: str | None) -> Set[str]:
    return {token.strip() for token in (value or "").split(";") if token.strip()}


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _non_empty(value: str | None) -> bool:
    return bool((value or "").strip())


def _load_function_map(function_catalog_path: Path) -> Dict[str, Tuple[str, str]]:
    rows = _read_csv(function_catalog_path)
    mapping: Dict[str, Tuple[str, str]] = {}
    for row in rows:
        function_id = (row.get("function_id") or "").strip()
        function_level = (row.get("function_level") or "").strip()
        domain = (row.get("l0_domain") or "").strip()
        if function_id:
            mapping[function_id] = (function_level, domain)
    return mapping


def _expected_exception_interfaces(
    interface_rows: Iterable[Dict[str, str]],
    function_map: Dict[str, Tuple[str, str]],
) -> Set[str]:
    expected: Set[str] = set()
    for row in interface_rows:
        interface_id = (row.get("interface_id") or "").strip()
        producer_fn = (row.get("producer_function_id") or "").strip()
        consumer_fn = (row.get("consumer_function_id") or "").strip()

        if not interface_id or not producer_fn or not consumer_fn:
            continue

        producer_meta = function_map.get(producer_fn)
        consumer_meta = function_map.get(consumer_fn)
        if not producer_meta or not consumer_meta:
            continue

        producer_level, producer_domain = producer_meta
        consumer_level, consumer_domain = consumer_meta

        same_level = producer_level == consumer_level and producer_level in {"L1", "L2"}
        cross_domain = producer_domain and consumer_domain and producer_domain != consumer_domain

        if same_level and cross_domain:
            expected.add(interface_id)

    return expected


def _classify_trust_boundary(level_pair: str, producer_fn: str, consumer_fn: str) -> str:
    if level_pair == "L1->L1":
        return "TB-CONTROL-INTERDOMAIN"

    passenger_patterns = ("OPS.PAX.", "COM.DLNK.106", "COM.DLNK.107")
    maintenance_patterns = ("OPS.MAINT.", "OPS.OMMS.")
    if any(p in producer_fn or p in consumer_fn for p in passenger_patterns):
        return "TB-PASSENGER-SERVICE"
    if any(p in producer_fn or p in consumer_fn for p in maintenance_patterns):
        return "TB-MAINTENANCE-OFFBOARD"
    return "TB-DATA-INTERDOMAIN"


def _domain_from_function_id(function_id: str) -> str:
    prefix = function_id.split(".", 1)[0].strip().upper()
    return {
        "AVI": "AVIATE",
        "NAV": "NAVIGATE",
        "COM": "COMMUNICATE",
        "OPS": "OPERATE",
    }.get(prefix, "")


def _next_exception_number(exception_rows: Iterable[Dict[str, str]]) -> int:
    max_num = 0
    for row in exception_rows:
        ex_id = (row.get("exception_id") or "").strip()
        if ex_id.startswith("EXC-"):
            suffix = ex_id.replace("EXC-", "", 1)
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return max_num + 1


def _build_missing_exception_proposals(
    missing_interface_ids: Iterable[str],
    interface_rows: Iterable[Dict[str, str]],
    function_map: Dict[str, Tuple[str, str]],
    exception_rows: Iterable[Dict[str, str]],
) -> List[Dict[str, str]]:
    interface_by_id = {
        (row.get("interface_id") or "").strip(): row for row in interface_rows if row.get("interface_id")
    }
    proposals: List[Dict[str, str]] = []
    next_num = _next_exception_number(exception_rows)

    for interface_id in sorted(missing_interface_ids):
        source = interface_by_id.get(interface_id)
        if not source:
            continue

        producer_fn = (source.get("producer_function_id") or "").strip()
        consumer_fn = (source.get("consumer_function_id") or "").strip()
        producer_meta = function_map.get(producer_fn)
        consumer_meta = function_map.get(consumer_fn)
        if not producer_meta or not consumer_meta:
            continue

        producer_level, producer_domain = producer_meta
        consumer_level, consumer_domain = consumer_meta
        if producer_level != consumer_level or producer_level not in {"L1", "L2"}:
            continue

        level_pair = f"{producer_level}->{consumer_level}"
        trust_boundary = _classify_trust_boundary(level_pair, producer_fn, consumer_fn)
        if level_pair == "L1->L1":
            exception_class = "system_context_bridge"
            rationale = (
                "Cross-domain L1 coordination path required for mission/system context handoff "
                "across top-level domains."
            )
            gate_targets = "G5-THREAT;G4-VERIFICATION"
            gate_evidence_refs = (
                "EA-ICD;EA-SCHEMA;EA-TRUST-BOUNDARY-ANALYSIS;EA-VV-TEST;EA-THREAT-MODEL-TRACE"
            )
            threat_model_row_id = "TM-BRIDGE-" + interface_id.replace("IF-", "")
        else:
            exception_class = "operational_data_exchange_bridge"
            rationale = (
                "Cross-domain L2 data exchange required to support end-to-end operational flow "
                "across decomposed functions."
            )
            gate_targets = "G4-VERIFICATION;G9-READINESS"
            gate_evidence_refs = (
                "EA-ICD;EA-SCHEMA;EA-TRUST-BOUNDARY-ANALYSIS;EA-VV-TEST;EA-LOGGING"
            )
            threat_model_row_id = "TM-DATA-" + interface_id.replace("IF-", "")

        ex_id = f"EXC-{next_num:03d}"
        next_num += 1
        proposals.append(
            {
                "exception_id": ex_id,
                "interface_id": interface_id,
                "producer_function_id": producer_fn,
                "consumer_function_id": consumer_fn,
                "producer_domain": producer_domain or _domain_from_function_id(producer_fn),
                "consumer_domain": consumer_domain or _domain_from_function_id(consumer_fn),
                "level_pair": level_pair,
                "exception_class": exception_class,
                "trust_boundary_classification": trust_boundary,
                "rationale": rationale,
                "gate_targets": gate_targets,
                "gate_evidence_refs": gate_evidence_refs,
                "status": "open",
                "disposition": "proposed",
                "risk_acceptance_id": "",
                "mitigation_due_date": "",
                "approved_by": "",
                "approval_date": "",
                "threat_model_row_id": threat_model_row_id,
                "vv_test_case_ids": "VV-" + interface_id + "-A;VV-" + interface_id + "-B",
                "icd_section_ref": "ICD-" + interface_id.replace("IF-", "") + ".1",
                "schema_version": "v2.0",
            }
        )

    return proposals


def _write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def validate(
    interface_matrix_path: Path,
    function_catalog_path: Path,
    exception_register_path: Path,
) -> Tuple[List[str], List[str], List[Dict[str, str]]]:
    errors: List[str] = []
    warnings: List[str] = []

    interface_rows = _read_csv(interface_matrix_path)
    function_map = _load_function_map(function_catalog_path)
    exception_rows = _read_csv(exception_register_path)

    header = []
    with exception_register_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])

    missing_cols = [c for c in REQUIRED_EXCEPTION_COLUMNS if c not in header]
    if missing_cols:
        errors.append("Missing required exception register columns: " + ", ".join(missing_cols))

    expected_interfaces = _expected_exception_interfaces(interface_rows, function_map)
    seen_interfaces: Set[str] = set()
    dup_interfaces: Set[str] = set()

    for row in exception_rows:
        ex_id = (row.get("exception_id") or "").strip()
        interface_id = (row.get("interface_id") or "").strip()
        if interface_id in seen_interfaces:
            dup_interfaces.add(interface_id)
        seen_interfaces.add(interface_id)

        required_non_empty = [
            "exception_id",
            "interface_id",
            "producer_function_id",
            "consumer_function_id",
            "level_pair",
            "exception_class",
            "trust_boundary_classification",
            "rationale",
            "gate_targets",
            "gate_evidence_refs",
            "status",
            "disposition",
            "threat_model_row_id",
            "vv_test_case_ids",
            "icd_section_ref",
            "schema_version",
        ]
        for key in required_non_empty:
            if not _non_empty(row.get(key)):
                errors.append(f"{ex_id or '[unknown]'}: required field '{key}' is empty")

        level_pair = (row.get("level_pair") or "").strip()
        if level_pair not in ALLOWED_LEVEL_PAIRS:
            errors.append(f"{ex_id}: invalid level_pair '{level_pair}'")

        trust_boundary = (row.get("trust_boundary_classification") or "").strip()
        if trust_boundary not in ALLOWED_TRUST_BOUNDARIES:
            errors.append(f"{ex_id}: invalid trust_boundary_classification '{trust_boundary}'")

        disposition = (row.get("disposition") or "").strip()
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{ex_id}: invalid disposition '{disposition}'")

        status = (row.get("status") or "").strip()
        if status not in ALLOWED_STATUSES:
            errors.append(f"{ex_id}: invalid status '{status}'")

        schema_version = (row.get("schema_version") or "").strip()
        if schema_version != "v2.0":
            errors.append(f"{ex_id}: schema_version must be 'v2.0', found '{schema_version}'")

        evidence_tokens = _split_tokens(row.get("gate_evidence_refs"))
        missing_evidence = sorted(REQUIRED_EVIDENCE_TOKENS - evidence_tokens)
        if missing_evidence:
            errors.append(
                f"{ex_id}: gate_evidence_refs missing required tokens: {', '.join(missing_evidence)}"
            )

        approved_by = (row.get("approved_by") or "").strip()
        approval_date = (row.get("approval_date") or "").strip()
        if disposition in {"accepted", "waived", "rejected", "closed"}:
            if not approved_by:
                errors.append(f"{ex_id}: approved_by is required when disposition is '{disposition}'")
            if not approval_date:
                errors.append(f"{ex_id}: approval_date is required when disposition is '{disposition}'")

        if disposition == "mitigated" and not _non_empty(row.get("mitigation_due_date")):
            errors.append(f"{ex_id}: mitigation_due_date is required when disposition is 'mitigated'")

        if status == "closed" and disposition not in {"accepted", "mitigated", "waived", "closed"}:
            errors.append(
                f"{ex_id}: status 'closed' requires disposition in accepted|mitigated|waived|closed"
            )

    if dup_interfaces:
        errors.append(
            "Duplicate exception rows detected for interface_id: " + ", ".join(sorted(dup_interfaces))
        )

    missing_exceptions = sorted(expected_interfaces - seen_interfaces)
    if missing_exceptions:
        errors.append(
            "Missing exception entries for cross-domain same-level interfaces: "
            + ", ".join(missing_exceptions)
        )

    proposals = _build_missing_exception_proposals(
        missing_interface_ids=missing_exceptions,
        interface_rows=interface_rows,
        function_map=function_map,
        exception_rows=exception_rows,
    )

    extra_exceptions = sorted(seen_interfaces - expected_interfaces)
    if extra_exceptions:
        warnings.append(
            "Exception entries exist for interfaces not currently detected as cross-domain same-level: "
            + ", ".join(extra_exceptions)
        )

    return errors, warnings, proposals


def _default_paths(repo_root: Path) -> Tuple[Path, Path, Path]:
    base = repo_root / "data" / "inputs" / "Aerospace_Architecture" / "03_mapping_for_threat_alignment"
    return (
        base / "interface_governance_matrix.csv",
        base / "function_catalog.csv",
        base / "cross_domain_interface_exception_register.csv",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate cross-domain exception policy completeness and governance fields."
    )
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--interface-matrix")
    parser.add_argument("--function-catalog")
    parser.add_argument("--exception-register")
    parser.add_argument(
        "--propose-missing",
        action="store_true",
        help="Generate proposed exception rows for newly-detected missing cross-domain same-level links.",
    )
    parser.add_argument(
        "--proposal-out",
        help="Write proposal CSV output to this path when --propose-missing is enabled.",
    )
    parser.add_argument(
        "--proposal-only",
        action="store_true",
        help="Generate proposals and return success without enforcing policy failure semantics.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    default_interface, default_function, default_exception = _default_paths(repo_root)

    interface_path = Path(args.interface_matrix).resolve() if args.interface_matrix else default_interface
    function_path = Path(args.function_catalog).resolve() if args.function_catalog else default_function
    exception_path = (
        Path(args.exception_register).resolve() if args.exception_register else default_exception
    )

    for path in (interface_path, function_path, exception_path):
        if not path.exists():
            print(f"ERROR: required input file not found: {path}")
            return 2

    errors, warnings, proposals = validate(interface_path, function_path, exception_path)

    print("Cross-domain exception policy validation report")
    print(f"- Interface matrix: {interface_path}")
    print(f"- Function catalog: {function_path}")
    print(f"- Exception register: {exception_path}")

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")

    if args.propose_missing:
        print(f"PROPOSALS: {len(proposals)} missing exception row(s) can be auto-generated.")
        if proposals:
            if args.proposal_out:
                proposal_path = Path(args.proposal_out)
                if not proposal_path.is_absolute():
                    proposal_path = repo_root / proposal_path
                proposal_path.parent.mkdir(parents=True, exist_ok=True)
                _write_csv(proposal_path, proposals, REQUIRED_EXCEPTION_COLUMNS)
                print(f"- Proposal CSV written: {proposal_path}")
            else:
                print("- Proposal rows (CSV):")
                writer = csv.DictWriter(sys.stdout, fieldnames=REQUIRED_EXCEPTION_COLUMNS)
                writer.writeheader()
                for row in proposals:
                    writer.writerow({key: row.get(key, "") for key in REQUIRED_EXCEPTION_COLUMNS})

    if args.proposal_only:
        print("Proposal-only mode complete.")
        return 0

    if errors:
        print(f"FAIL ({len(errors)} errors):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: exception register covers all cross-domain same-level interfaces with valid governance fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
