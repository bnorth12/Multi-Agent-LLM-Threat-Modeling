"""Shared state container for staged framework execution."""

from dataclasses import dataclass, field
from typing import Any

from .models import CanonicalThreatModelGraph


@dataclass
class FrameworkState:
    raw_text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)
    canonical_graph: CanonicalThreatModelGraph | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    stix_bundle: dict[str, Any] | None = None
    mermaid_diagrams: dict[str, str] = field(default_factory=dict)
    final_report: str | None = None
    human_feedback: str | None = None
    next_stage_id: str | None = None
    trust_boundary_review_needed: bool = False
    stride_complete: bool = False
    threats_generated: bool = False

    # LLM usage telemetry (captured only for live provider calls).
    llm_usage_by_stage: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    llm_attempts_by_stage: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    llm_prompts_by_stage: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    llm_prompt_history: list[dict[str, Any]] = field(default_factory=list)

    # HITL state — populated by gate engine interactions
    hitl_gate_checkpoint: dict[str, Any] | None = None  # serialised gate engine state
    hitl_paused_at_gate: str | None = None               # gate_id when pipeline is paused
    hitl_rejected_at_gate: str | None = None             # gate_id if analyst rejected
    threat_review_decisions: dict[str, dict[str, str]] = field(default_factory=dict)

    def record_message(self, stage_id: str, text: str) -> None:
        self.messages.append({"stage_id": stage_id, "text": text})

    def record_llm_usage(self, stage_id: str, usage: dict[str, Any]) -> None:
        if not stage_id or not usage:
            return
        self.llm_usage_by_stage.setdefault(stage_id, []).append(dict(usage))

    def record_llm_attempt(self, stage_id: str, attempt: dict[str, Any]) -> None:
        if not stage_id or not attempt:
            return
        self.llm_attempts_by_stage.setdefault(stage_id, []).append(dict(attempt))

    def record_llm_prompt(self, stage_id: str, prompt: dict[str, Any]) -> None:
        if not stage_id or not prompt:
            return
        entry = dict(prompt)
        entry.setdefault("stage_id", stage_id)
        self.llm_prompts_by_stage.setdefault(stage_id, []).append(entry)
        self.llm_prompt_history.append(entry)

    def latest_llm_prompt(self, stage_id: str | None = None) -> dict[str, Any] | None:
        if stage_id:
            entries = self.llm_prompts_by_stage.get(stage_id, [])
            if entries:
                return dict(entries[-1])
            return None
        if self.llm_prompt_history:
            return dict(self.llm_prompt_history[-1])
        return None

    def llm_usage_totals(self) -> dict[str, int]:
        totals = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "cached_tokens": 0,
            "total_tokens": 0,
            "request_count": 0,
        }

        for entries in self.llm_usage_by_stage.values():
            for entry in entries:
                totals["prompt_tokens"] += int(entry.get("prompt_tokens", 0) or 0)
                totals["completion_tokens"] += int(entry.get("completion_tokens", 0) or 0)
                totals["reasoning_tokens"] += int(entry.get("reasoning_tokens", 0) or 0)
                totals["cached_tokens"] += int(entry.get("cached_tokens", 0) or 0)
                totals["total_tokens"] += int(entry.get("total_tokens", 0) or 0)
                totals["request_count"] += 1

        return totals

    def llm_attempt_totals(self) -> dict[str, int]:
        totals = {
            "submitted": 0,
            "completed": 0,
            "failed": 0,
        }

        for entries in self.llm_attempts_by_stage.values():
            for entry in entries:
                status = str(entry.get("status", "")).lower()
                if status in totals:
                    totals[status] += 1

        totals["total"] = totals["submitted"] + totals["completed"] + totals["failed"]
        return totals

    def canonical_graph_dict(self) -> dict[str, Any]:
        if self.canonical_graph is None:
            return {}
        return self.canonical_graph.to_dict()
