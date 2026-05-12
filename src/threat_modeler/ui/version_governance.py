"""Version inventory helpers for GUI-024 and release evidence exports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


_COMPONENT_PATHS: dict[str, list[str]] = {
    "ui": ["src/threat_modeler/ui"],
    "agents": ["src/threat_modeler/agents"],
    "models": ["src/threat_modeler/models"],
    "orchestrator": ["src/threat_modeler/orchestrator.py", "src/threat_modeler/state.py"],
    "validation": ["src/threat_modeler/validation.py"],
    "exports": ["src/threat_modeler/exports"],
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _read_project_version() -> str:
    pyproject = _repo_root() / "pyproject.toml"
    if not pyproject.exists():
        return "0.0.0"

    for line in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("version") and "=" in stripped:
            value = stripped.split("=", 1)[1].strip().strip('"')
            if value:
                return value
    return "0.0.0"


def _iter_component_files(component: str) -> list[Path]:
    root = _repo_root()
    files: list[Path] = []
    for entry in _COMPONENT_PATHS.get(component, []):
        path = root / entry
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        elif path.is_file():
            files.append(path)
    return files


def generate_component_version_manifest() -> dict[str, Any]:
    """Build semantic version manifest for major components."""
    project_version = _read_project_version()
    components: list[dict[str, Any]] = []

    for component in sorted(_COMPONENT_PATHS.keys()):
        file_count = len(_iter_component_files(component))
        components.append(
            {
                "component": component,
                "version": project_version,
                "file_count": file_count,
            }
        )

    return {
        "manifest_version": "s09-component-version-v1",
        "project_version": project_version,
        "components": components,
    }


def _sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_component_file_inventory() -> dict[str, Any]:
    """Build deterministic file-level inventory for component-owned files."""
    root = _repo_root()
    rows: list[dict[str, Any]] = []

    for component in sorted(_COMPONENT_PATHS.keys()):
        for path in _iter_component_files(component):
            rel = path.relative_to(root).as_posix()
            rows.append(
                {
                    "component": component,
                    "path": rel,
                    "sha256": _sha256_hex(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    rows.sort(key=lambda row: (row["component"], row["path"]))
    return {
        "inventory_version": "s09-component-file-inventory-v1",
        "row_count": len(rows),
        "files": rows,
    }


def manifest_to_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def inventory_to_json(inventory: dict[str, Any]) -> str:
    return json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
