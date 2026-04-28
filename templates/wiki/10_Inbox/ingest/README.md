# Ingest Packages

Staged packages produced from external sources.

Each package directory should include `manifest.md`.

## Example Manifest

```markdown
---
type: ingest
source_type: docs
status: staged
created: 2026-04-28
provenance:
  - https://example.com/source-doc
candidate_notes:
  - Sources/Docs/example-source.md
  - Cards/example-concept.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: The source defines a reusable concept that should be queryable from stable Cards.
---
# Package: Example Source

## Summary
Short summary of the source and candidate knowledge.

## Promotion Plan
- create: Sources/Docs/example-source.md
- create: Cards/example-concept.md
- update: 00_System/+Wiki Index.md
```
