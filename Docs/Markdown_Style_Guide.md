# Markdown Style Guide

## Purpose

Provide a consistent markdown authoring standard to prevent recurring markdownlint issues.

## Required Structure Rules

1. Use ATX headings with one space after the hash.

1. Add a blank line before and after lists.

1. For ordered lists, use 1. for every item.

1. Use fenced code blocks with language tags when possible.

1. End files with a single trailing newline.

## List Rules

- Keep list marker style consistent within a list.
- Avoid nesting unless necessary.
- Do not place list items immediately under a paragraph line without a blank line.

## Table Rules

- Use simple pipe tables with consistent header and separator rows.
- Prefer this separator style:
  - | --- | --- |

## File Maintenance Rules

- Keep one concept per file where practical.
- Keep sections short and scannable.
- Update linked index files when adding or removing docs.

## Repo Workflow Rules

- Run markdownlint before opening a pull request.
- Fix lint warnings in files touched by the branch.
- Do not introduce new markdownlint warnings.
