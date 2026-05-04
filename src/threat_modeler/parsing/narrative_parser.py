"""Narrative document ingestion: parses Markdown (and optionally docx) files.

Extracts:
  - system_name  : text of the first H1 heading (# ...) or filename stem
  - description  : first non-empty paragraph following the H1 heading
  - raw_text     : full document text
"""

import os
import re
from dataclasses import dataclass


@dataclass
class NarrativeParseResult:
    """Normalised content extracted from one architecture description file."""

    source_file: str
    system_name: str
    description: str
    raw_text: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_BLANK_LINE_RE = re.compile(r"\n{2,}")


def _parse_text(raw: str, source_file: str) -> NarrativeParseResult:
    """Extract system_name and description from plain text."""
    m = _H1_RE.search(raw)
    if m:
        system_name = m.group(1).strip()
        after_heading = raw[m.end():]
    else:
        system_name = os.path.splitext(os.path.basename(source_file))[0]
        after_heading = raw

    paragraphs = [p.strip() for p in _BLANK_LINE_RE.split(after_heading.strip()) if p.strip()]
    # Skip any immediate sub-heading lines as the description
    description = ""
    for para in paragraphs:
        if not para.startswith("#"):
            description = para
            break

    return NarrativeParseResult(
        source_file=source_file,
        system_name=system_name,
        description=description,
        raw_text=raw,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_markdown(path: str) -> NarrativeParseResult:
    """Parse a Markdown file and return a NarrativeParseResult."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    return _parse_text(raw, source_file=path)


def parse_docx(path: str) -> NarrativeParseResult:
    """Parse a .docx file.  Requires python-docx."""
    try:
        import docx  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "python-docx is required to parse docx files.  "
            "Install it with: pip install python-docx"
        ) from exc

    doc = docx.Document(path)
    raw = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return _parse_text(raw, source_file=path)


def parse(path: str) -> NarrativeParseResult:
    """Dispatch to the appropriate parser based on file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".md", ".txt"):
        return parse_markdown(path)
    if ext == ".docx":
        return parse_docx(path)
    raise ValueError(f"Unsupported narrative file extension: {ext!r}. Supported: .md, .txt, .docx")
