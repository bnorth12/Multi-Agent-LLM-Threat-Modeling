# Source Copies for Ingestion

## Purpose

This folder stores the actual artifacts intended for ingestion, not only summary notes.

## Why This Matters

- Summaries and links are useful for curation but are weak for reproducible retrieval.
- Captured source text supports stable embedding, citation, and auditability.

## Capture Rules

- Store only content you are authorized to retain and process.
- Prefer extracted text or excerpted notes with citation metadata when full redistribution is restricted.
- Record source URL, retrieval timestamp, and extractor method.

## Suggested Layout

- `queue/`: source capture queue and status tracker.
- `manifests/`: normalized capture manifests, including ISAC public-source schema extension artifacts.
- `raw/`: direct text captures where permitted.
- `extracted/`: normalized markdown/text for ingestion.

## Starter Status

Use `queue/capture_queue.md` to track pending and completed source captures.
