#!/usr/bin/env python3
"""Dependency boundary guard for release-candidate hardening.

Ensures test/dev-only dependencies do not leak into runtime dependency manifests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_REQUIREMENTS = REPO_ROOT / "requirements.txt"
FRONTEND_PACKAGE = REPO_ROOT / "frontend" / "package.json"

PYTHON_TEST_ONLY = {
    "pytest",
    "pytest-cov",
    "pytest-playwright",
    "playwright",
    "streamlit",
}

FRONTEND_TEST_ONLY = {
    "@playwright/test",
    "playwright",
    "vitest",
    "jest",
    "cypress",
}


def parse_requirements_packages(path: Path) -> set[str]:
    packages: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = line.split("=", 1)[0].split("<", 1)[0].split(">", 1)[0].strip().lower()
        if name:
            packages.add(name)
    return packages


def main() -> int:
    errors: list[str] = []

    if not RUNTIME_REQUIREMENTS.exists():
        errors.append(f"Missing runtime requirements file: {RUNTIME_REQUIREMENTS}")
    else:
        runtime_pkgs = parse_requirements_packages(RUNTIME_REQUIREMENTS)
        leaked_python = sorted(runtime_pkgs.intersection(PYTHON_TEST_ONLY))
        if leaked_python:
            errors.append(
                "Runtime requirements.txt includes test-only Python packages: "
                + ", ".join(leaked_python)
            )

    if not FRONTEND_PACKAGE.exists():
        errors.append(f"Missing frontend package manifest: {FRONTEND_PACKAGE}")
    else:
        package_data = json.loads(FRONTEND_PACKAGE.read_text(encoding="utf-8"))
        frontend_runtime = {
            str(name).lower() for name in package_data.get("dependencies", {}).keys()
        }
        leaked_frontend = sorted(frontend_runtime.intersection(FRONTEND_TEST_ONLY))
        if leaked_frontend:
            errors.append(
                "frontend/package.json dependencies include test-only JS packages: "
                + ", ".join(leaked_frontend)
            )

    if errors:
        print("DEPENDENCY_BOUNDARY_CHECK_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DEPENDENCY_BOUNDARY_CHECK_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
