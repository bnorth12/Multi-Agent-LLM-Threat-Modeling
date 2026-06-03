#!/usr/bin/env python3
"""Enforce full-chain traceability for reachable source modules.

This gate intentionally excludes sprint/planning artifacts so traceability survives
sprint archival. A reachable module must be traceable across all persistent domains:
requirements, capabilities, functions, architecture, design, verification.
"""

from __future__ import annotations

import ast
import re
from argparse import ArgumentParser
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

REQ_ID_PATTERN = re.compile(
    r"\b(?:ADM|GUI|HITL|INT|LLM|ORCH|PRJ|RHMI|RIC|SCR|VS|PRM|C\d{2}(?:-[A-Z0-9_]+)?)-\d{1,3}[A-Z]?\b"
)
CAPABILITY_TOKEN = re.compile(r"\bC\d{2}-[A-Z0-9_]+(?:-\d+)?\b")
FUNCTION_TOKEN = re.compile(r"\bF-[A-Z0-9_\-/]+\b")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def collect_text(paths: Iterable[Path]) -> str:
    chunks: List[str] = []
    for path in paths:
        try:
            chunks.append(read_text(path))
        except OSError:
            continue
    return "\n".join(chunks)


def file_to_module(path: Path, src_root: Path) -> str:
    rel = path.resolve().relative_to(src_root)
    return ".".join(rel.with_suffix("").parts)


def module_to_file(module: str, src_root: Path, module_map: Dict[str, Path]) -> Path | None:
    if module in module_map:
        return module_map[module]
    pkg_init = src_root / Path(*module.split(".")) / "__init__.py"
    if pkg_init.exists():
        return pkg_init.resolve()
    py_file = src_root / Path(*module.split(".")).with_suffix(".py")
    if py_file.exists():
        return py_file.resolve()
    return None


def resolve_import(current_module: str, node: ast.AST, module_map: Dict[str, Path]) -> List[str]:
    resolved: List[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "threat_modeler" or alias.name.startswith("threat_modeler."):
                resolved.append(alias.name)
        return resolved

    if not isinstance(node, ast.ImportFrom):
        return resolved

    level = node.level or 0
    module = node.module or ""
    current_parts = current_module.split(".")
    if level > 0:
        base = current_parts[:-level]
        full = ".".join(base + (module.split(".") if module else []))
    else:
        full = module

    if full == "threat_modeler" or full.startswith("threat_modeler."):
        resolved.append(full)

    for alias in node.names:
        if alias.name == "*":
            continue
        candidate = (full + "." + alias.name).strip(".")
        if candidate in module_map:
            resolved.append(candidate)

    return resolved


def discover_reachable_modules(repo_root: Path) -> List[Tuple[str, Path, str]]:
    src_root = repo_root / "src"
    package_root = src_root / "threat_modeler"
    entrypoints = [
        package_root / "__main__.py",
        package_root / "ui" / "app.py",
    ]

    all_py = {path.resolve() for path in package_root.rglob("*.py")}
    module_map: Dict[str, Path] = {}
    for path in all_py:
        module_map[file_to_module(path, src_root)] = path

    visited: Set[str] = set()
    queue: deque[str] = deque(file_to_module(path, src_root) for path in entrypoints)

    while queue:
        module = queue.popleft()
        if module in visited:
            continue
        file_path = module_to_file(module, src_root, module_map)
        if not file_path or file_path not in all_py:
            continue
        visited.add(module)
        try:
            tree = ast.parse(read_text(file_path))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for dependency in resolve_import(module, node, module_map):
                    if dependency.startswith("threat_modeler") and dependency not in visited:
                        queue.append(dependency)

    reachable: List[Tuple[str, Path, str]] = []
    for module in sorted(visited):
        file_path = module_to_file(module, src_root, module_map)
        if not file_path or file_path not in all_py:
            continue
        rel = file_path.relative_to(repo_root).as_posix()
        if rel.endswith("/__init__.py"):
            continue
        reachable.append((module, file_path, rel))
    return reachable


def count_unique_functions(reachable: List[Tuple[str, Path, str]]) -> Tuple[int, Dict[str, int]]:
    seen: Set[str] = set()
    by_module: Dict[str, int] = {}

    class Collector(ast.NodeVisitor):
        def __init__(self, module_name: str) -> None:
            self.module_name = module_name
            self.class_stack: List[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def _add_symbol(self, node: ast.AST) -> None:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return
            qual = ".".join(self.class_stack + [node.name]) if self.class_stack else node.name
            symbol = f"{self.module_name}.{qual}"
            if symbol in seen:
                return
            seen.add(symbol)
            by_module[self.module_name] = by_module.get(self.module_name, 0) + 1

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._add_symbol(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._add_symbol(node)
            self.generic_visit(node)

    for module_name, file_path, _ in reachable:
        try:
            tree = ast.parse(read_text(file_path))
        except SyntaxError:
            continue
        Collector(module_name).visit(tree)

    return len(seen), by_module


def evaluate_domains(repo_root: Path, reachable: List[Tuple[str, Path, str]]) -> Tuple[List[dict], Dict[str, int], int, int]:
    requirements_files = sorted((repo_root / "Requirements").rglob("*.md"))
    architecture_files = sorted((repo_root / "docs" / "architecture").rglob("*.md"))
    design_files = sorted((repo_root / "docs" / "design").rglob("*.md"))
    verification_files = sorted((repo_root / "Tests").rglob("*.py")) + sorted((repo_root / "Tests").rglob("*.md"))

    capability_files = [p for p in architecture_files if "Capability" in p.name]
    function_files = [p for p in architecture_files if "Function" in p.name]

    req_text = collect_text(requirements_files)
    arch_text = collect_text(architecture_files)
    design_text = collect_text(design_files)
    verification_text = collect_text(verification_files)

    # Capability/function quality checks rely on architecture rows carrying explicit tokens.
    architecture_lines = arch_text.splitlines()

    rows: List[dict] = []
    domain_counts = {
        "requirements": 0,
        "capabilities": 0,
        "functions": 0,
        "architecture": 0,
        "design": 0,
        "verification": 0,
    }
    existing_relationships = 0

    for _, file_path, rel in reachable:
        module_code = read_text(file_path)
        ids_in_code = sorted(set(REQ_ID_PATTERN.findall(module_code)))

        requirement_match = rel in req_text
        architecture_match = rel in arch_text
        design_match = rel in design_text
        verification_match = rel in verification_text

        capability_match = False
        function_match = False
        for line in architecture_lines:
            if rel not in line:
                continue
            if CAPABILITY_TOKEN.search(line):
                capability_match = True
            if FUNCTION_TOKEN.search(line):
                function_match = True

        domains = {
            "requirements": requirement_match,
            "capabilities": capability_match,
            "functions": function_match,
            "architecture": architecture_match,
            "design": design_match,
            "verification": verification_match,
        }

        for key, matched in domains.items():
            if matched:
                domain_counts[key] += 1

        existing = sum(1 for matched in domains.values() if matched)
        existing_relationships += existing

        missing_domains = [key for key, matched in domains.items() if not matched]
        rows.append(
            {
                "module": rel,
                "requirement_ids": ids_in_code,
                "domains": domains,
                "existing": existing,
                "missing": missing_domains,
            }
        )

    return rows, domain_counts, existing_relationships, len(reachable)


def write_report(
    output_path: Path,
    rows: List[dict],
    domain_counts: Dict[str, int],
    reachable_count: int,
    unique_functions: int,
    existing_relationships: int,
) -> None:
    full = sum(1 for row in rows if row["existing"] == 6)
    partial = sum(1 for row in rows if 0 < row["existing"] < 6)
    unmatched = sum(1 for row in rows if row["existing"] == 0)

    lines: List[str] = []
    lines.append("# Reachable Full-Chain Traceability Gate Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("Scope:")
    lines.append("")
    lines.append("- Reachable modules discovered from runtime entrypoints: src/threat_modeler/__main__.py and src/threat_modeler/ui/app.py")
    lines.append("- Persistent trace corpora only: Requirements/, docs/architecture/, docs/design/, Tests/")
    lines.append("- Sprint/planning artifacts are intentionally excluded from gate scoring")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(f"- Reachable modules: {reachable_count}")
    lines.append(f"- Unique functions (including methods): {unique_functions}")
    lines.append(f"- Full-chain modules: {full}")
    lines.append(f"- Partial modules: {partial}")
    lines.append(f"- Unmatched modules: {unmatched}")
    lines.append(f"- Existing relationships: {existing_relationships}")
    lines.append("")
    lines.append("## Domain Coverage")
    lines.append("")
    for key in ["requirements", "capabilities", "functions", "architecture", "design", "verification"]:
        lines.append(f"- {key}: {domain_counts[key]}/{reachable_count}")

    lines.append("")
    lines.append("## Modules Missing Full Chain")
    lines.append("")
    if partial == 0 and unmatched == 0:
        lines.append("(none)")
    else:
        for row in rows:
            if row["existing"] == 6:
                continue
            missing = ", ".join(row["missing"])
            ids = ", ".join(row["requirement_ids"]) if row["requirement_ids"] else "(none)"
            lines.append(f"- {row['module']} | missing: {missing} | requirement_ids_in_code: {ids}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = ArgumentParser(description="Verify full-chain traceability for reachable modules (persistent artifacts only)")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--report",
        default="test_reports/reachable_full_chain_traceability_report.md",
        help="Output report path relative to repo root",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report_path = (repo_root / args.report).resolve()

    reachable = discover_reachable_modules(repo_root)
    unique_functions, _ = count_unique_functions(reachable)
    rows, domain_counts, existing_relationships, reachable_count = evaluate_domains(repo_root, reachable)

    write_report(
        output_path=report_path,
        rows=rows,
        domain_counts=domain_counts,
        reachable_count=reachable_count,
        unique_functions=unique_functions,
        existing_relationships=existing_relationships,
    )

    missing = [row for row in rows if row["existing"] < 6]
    if missing:
        print("[reachable-full-chain] FAIL: modules missing full-chain traceability")
        print(f"[reachable-full-chain] report: {report_path.as_posix()}")
        for row in missing:
            print(
                f"[reachable-full-chain] {row['module']} missing={','.join(row['missing'])} "
                f"req_ids={','.join(row['requirement_ids']) or '(none)'}"
            )
        return 1

    print("[reachable-full-chain] PASS: all reachable modules have full-chain traceability")
    print(f"[reachable-full-chain] report: {report_path.as_posix()}")
    print(f"[reachable-full-chain] reachable_modules={reachable_count} unique_functions={unique_functions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
