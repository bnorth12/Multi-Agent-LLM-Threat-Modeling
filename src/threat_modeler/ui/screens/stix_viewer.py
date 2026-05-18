"""GUI-018 — STIX Threat Model Viewer screen."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import streamlit as st

from threat_modeler.ui.execution import sync_execution_state_to_session


def _extract_stix_objects(bundle: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Return STIX object list from a bundle-like dict."""
    if not isinstance(bundle, dict):
        return []
    objects = bundle.get("objects")
    if not isinstance(objects, list):
        return []
    return [obj for obj in objects if isinstance(obj, dict)]


def _group_objects_by_type(objects: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group STIX objects by type name."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for obj in objects:
        grouped[str(obj.get("type", "unknown"))].append(obj)
    return dict(sorted(grouped.items(), key=lambda item: item[0]))


def _filter_objects(
    objects: list[dict[str, Any]],
    selected_types: set[str],
    search_text: str,
) -> list[dict[str, Any]]:
    """Filter by type and by name/id text."""
    needle = search_text.strip().lower()
    filtered: list[dict[str, Any]] = []
    for obj in objects:
        obj_type = str(obj.get("type", "unknown"))
        if selected_types and obj_type not in selected_types:
            continue
        if needle:
            name = str(obj.get("name", ""))
            obj_id = str(obj.get("id", ""))
            if needle not in name.lower() and needle not in obj_id.lower():
                continue
        filtered.append(obj)
    return filtered


def _build_object_name_index(objects: list[dict[str, Any]]) -> dict[str, str]:
    """Build object ID -> display label mapping for readable relationship refs."""
    index: dict[str, str] = {}
    for obj in objects:
        obj_id = str(obj.get("id", "")).strip()
        if not obj_id:
            continue
        name = str(obj.get("name", "")).strip()
        obj_type = str(obj.get("type", "")).strip()
        if name:
            index[obj_id] = f"{name} ({obj_type})" if obj_type else name
        elif obj_type:
            index[obj_id] = obj_type
        else:
            index[obj_id] = obj_id
    return index


def _resolve_ref(ref: str, index: dict[str, str]) -> str:
    """Return readable relationship reference while preserving canonical ID."""
    ref_id = str(ref or "").strip()
    if not ref_id:
        return ""
    label = index.get(ref_id)
    if not label:
        return ref_id
    return f"{label} [{ref_id}]"


def _summary_rows(
    objects: list[dict[str, Any]], id_index: dict[str, str] | None = None
) -> list[dict[str, str]]:
    """Build compact rows for table display."""
    if id_index is None:
        id_index = _build_object_name_index(objects)
    rows: list[dict[str, str]] = []
    for obj in objects:
        description = str(obj.get("description", "")).replace("\n", " ").strip()
        rows.append(
            {
                "Type": str(obj.get("type", "")),
                "ID": str(obj.get("id", "")),
                "Name": str(obj.get("name", "")),
                "Relationship": str(obj.get("relationship_type", "")),
                "Source": _resolve_ref(str(obj.get("source_ref", "")), id_index),
                "Target": _resolve_ref(str(obj.get("target_ref", "")), id_index),
                "Description": description[:120] + ("..." if len(description) > 120 else ""),
            }
        )
    return rows


def render() -> None:
    st.header("STIX Threat Model Viewer")
    st.caption("GUI-018 — grouped STIX object inspection with filter/search")

    sync_execution_state_to_session()

    state = st.session_state.get("pipeline_state")
    if state is None:
        st.warning("No active pipeline state. Start and run the pipeline first.")
        return

    objects = _extract_stix_objects(state.stix_bundle)
    if not objects:
        st.warning("No STIX bundle objects available in this run.")
        return

    grouped_all = _group_objects_by_type(objects)
    object_types = list(grouped_all.keys())

    st.subheader("Filter and Search")
    col_type, col_search = st.columns([0.5, 0.5])
    with col_type:
        selected_types = set(
            st.multiselect(
                "Object types",
                options=object_types,
                default=object_types,
                help="Filter by one or more STIX object types.",
            )
        )
    with col_search:
        search_text = st.text_input(
            "Search by name or ID",
            value="",
            help="Case-insensitive substring search over object name and id.",
        )

    filtered = _filter_objects(objects, selected_types, search_text)
    grouped_filtered = _group_objects_by_type(filtered)
    id_index = _build_object_name_index(objects)

    st.subheader("Bundle Summary")
    st.metric("Filtered objects", len(filtered))
    st.table(
        [
            {"Object Type": obj_type, "Count": len(items)}
            for obj_type, items in grouped_filtered.items()
        ]
    )

    st.subheader("Objects by Type")
    if not filtered:
        st.info("No objects match the selected filters.")
        return

    for obj_type, items in grouped_filtered.items():
        with st.expander(f"{obj_type} ({len(items)})", expanded=False):
            st.table(_summary_rows(items, id_index))
            st.caption("Raw objects")
            st.json(items)
