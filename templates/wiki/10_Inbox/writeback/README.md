# Writeback Packages

Staged packages produced from conversation or query synthesis.

Each package directory should include `manifest.md`.

## Example Manifest

```markdown
---
type: writeback
source_type: conversation_synthesis
status: staged
domain: Example
created: 2026-04-28
provenance:
  - conversation: durable synthesis from a user discussion
candidate_notes:
  - path: Cards/example-tradeoff.md
    kind: card
updates:
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: The discussion produced a reusable decision framework for the Example domain.
---
# Writeback Package: Example Tradeoff

## Candidate Knowledge
Short durable synthesis from the conversation.

## Proposed Changes
- create: Cards/example-tradeoff.md
- update: +Wiki Index.md

## Rationale
Why this belongs in stable wiki knowledge after review.
```
