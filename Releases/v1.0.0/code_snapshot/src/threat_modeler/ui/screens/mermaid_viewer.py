"""GUI-020 — Mermaid Diagram Viewer screen."""

from __future__ import annotations

import html
import json
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from threat_modeler.ui.execution import sync_execution_state_to_session


def _diagram_rows(diagrams: dict[str, str]) -> list[dict[str, Any]]:
    """Build deterministic rows for diagram metadata display/tests."""
    rows: list[dict[str, Any]] = []
    for level in sorted(diagrams.keys()):
        source = str(diagrams[level]).strip()
        rows.append(
            {
                "level": level,
                "line_count": len(source.splitlines()) if source else 0,
                "char_count": len(source),
                "is_valid": _is_probably_valid_mermaid(source),
            }
        )
    return rows


def _is_probably_valid_mermaid(source: str) -> bool:
    """Lightweight syntax check to surface obvious invalid content."""
    text = source.strip()
    if not text:
        return False
    valid_starts = (
        "flowchart",
        "graph",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "erDiagram",
        "journey",
        "gantt",
    )
    return text.startswith(valid_starts)


def _render_mermaid_html(source: str, *, dark_mode: bool) -> None:
        """Render Mermaid source in an isolated HTML component using mermaid.js."""
        escaped = html.escape(source)
        theme_name = "dark" if dark_mode else "default"
        canvas_bg = "#0e1117" if dark_mode else "#ffffff"
        html_doc = f"""
        <!doctype html>
        <html>
        <head>
            <meta charset=\"utf-8\" />
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: {canvas_bg};
                }}
                .wrap {{
                    padding: 12px;
                    overflow: auto;
                }}
            </style>
        </head>
        <body>
            <div class=\"wrap\">
                <pre class=\"mermaid\">{escaped}</pre>
            </div>
            <script type=\"module\">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({json.dumps({'startOnLoad': True, 'theme': theme_name})});
            </script>
        </body>
        </html>
        """
        components.html(html_doc, height=700, scrolling=True)


def render() -> None:
    st.header("Mermaid Diagram Viewer")
    st.caption("GUI-020 — rendered/source toggle with explicit render-error visibility")

    sync_execution_state_to_session()

    state = st.session_state.get("pipeline_state")
    if state is None:
        st.warning("No active pipeline state. Start and run the pipeline first.")
        return

    diagrams = dict(getattr(state, "mermaid_diagrams", {}) or {})
    if not diagrams:
        st.warning("No Mermaid diagrams available in this run.")
        return

    st.subheader("Diagram Inventory")
    rows = _diagram_rows(diagrams)
    st.table(rows)

    levels = [row["level"] for row in rows]
    selected_level = st.selectbox("Diagram level", options=levels)
    source = str(diagrams[selected_level]).strip()

    show_source = st.toggle("Show Mermaid source text", value=False)
    dark_mode = str(st.session_state.get("theme", "Default")).strip().lower() == "dark"

    st.subheader(f"Selected Diagram: {selected_level}")
    if _is_probably_valid_mermaid(source):
        if show_source:
            st.code(source, language="text")
        else:
            _render_mermaid_html(source, dark_mode=dark_mode)
    else:
        st.error("Unable to render Mermaid diagram: source does not match expected Mermaid syntax.")
        st.code(source, language="text")
