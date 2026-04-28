# Ingest Packages

Staged packages produced from external sources.

Each package directory should include `manifest.md`.

## Example Manifest

```markdown
---
type: ingest
source_type: docs
status: staged
domain: Example
created: 2026-04-28
provenance:
  - https://example.com/source-doc
candidate_notes:
  - path: Sources/example-source.md
    kind: source
  - path: Cards/example-concept.md
    kind: card
updates:
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: The source defines a reusable concept that should be queryable from the Example domain.
---
# Package: Example Source

## Summary
Short summary of the source and candidate knowledge.

## Promotion Plan
- create: Sources/example-source.md
- create: Cards/example-concept.md
- update: +Wiki Index.md
```
