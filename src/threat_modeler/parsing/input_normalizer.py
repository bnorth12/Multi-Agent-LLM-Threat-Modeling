"""Parsing interfaces for architecture text and table inputs."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParserInput:
    raw_text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)


class ParserInterface:
    def normalize(self, payload: ParserInput) -> dict[str, Any]:
        # TODO: Parse architecture text and tables into canonical graph form.
        return {
            "metadata": {"status": "parsed_placeholder"},
            "raw_text_present": bool(payload.raw_text),
            "table_count": len(payload.tables),
        }
