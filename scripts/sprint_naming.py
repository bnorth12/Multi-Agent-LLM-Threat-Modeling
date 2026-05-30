#!/usr/bin/env python3
"""Shared sprint token parsing for governance automation."""

from __future__ import annotations

import re
from dataclasses import dataclass


SPRINT_TOKEN_PATTERN = re.compile(r"^(?P<year>\d{4})[-_](?P<ordinal>\d{2,3})$")


@dataclass(frozen=True)
class SprintToken:
    year: str
    ordinal: str

    @property
    def dash(self) -> str:
        return f"{self.year}-{self.ordinal}"

    @property
    def underscore(self) -> str:
        return f"{self.year}_{self.ordinal}"

    @property
    def tag(self) -> str:
        return f"S{self.ordinal}"


def parse_sprint_token(raw: str) -> SprintToken:
    match = SPRINT_TOKEN_PATTERN.fullmatch(raw.strip())
    if not match:
        raise ValueError("Sprint must be YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN")
    return SprintToken(year=match.group("year"), ordinal=match.group("ordinal"))


def increment_sprint_token(raw: str, offset: int, separator: str = "_") -> str:
    token = parse_sprint_token(raw)
    width = max(len(token.ordinal), 2)
    return f"{token.year}{separator}{int(token.ordinal) + offset:0{width}d}"
