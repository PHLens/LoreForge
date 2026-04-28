# Writeback Packages

Staged packages produced from conversation or query synthesis.

Each package directory should include `manifest.md`.

## Example Manifest

```markdown
---
type: writeback
source_type: conversation_synthesis
status: staged
created: 2026-04-28
provenance:
  - conversation: durable synthesis from a user discussion
candidate_notes:
  - Cards/example-tradeoff.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: The discussion produced a reusable decision framework for stable Cards.
---
# Writeback Package: Example Tradeoff

## Candidate Knowledge
Short durable synthesis from the conversation.

## Proposed Changes
- create: Cards/example-tradeoff.md
- update: 00_System/+Wiki Index.md

## Rationale
Why this belongs in stable wiki knowledge after review.
```
