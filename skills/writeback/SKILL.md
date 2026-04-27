---
name: writeback
description: Use when conversation, query answer, comparison, decision rationale, human correction, or concept connection may become durable shared LoreForge wiki knowledge.
user-invocable: true
---

# Writeback

After delivering a substantive synthesized answer, evaluate whether it should be filed back into the wiki.

Writeback handles conversation-derived knowledge. The default output is a staged package, not a silent edit to stable knowledge.

## Trigger

Use when the user asks to save, file, record, write back, or preserve a synthesized answer.

The agent may also propose writeback after a reusable answer, but should not interrupt every conversation.

Skip:

- simple factual lookups
- one-off troubleshooting
- greetings and confirmations
- current task state
- agent-local experience, preferences, or workflow memories

## What Counts As Writeback Knowledge

Write back only shared professional knowledge:

- reusable concept explanation
- comparison, trade-off, or decision framework
- durable connection between existing concepts
- synthesis across multiple sources or prior notes
- reusable method, checklist, or pattern
- source-grounded clarification produced during the conversation

Do not write shared wiki notes for:

- agent-local operating experience
- user preferences
- temporary project state
- full transcripts
- one-off debugging details

Agent-local experience belongs in `pamem`, not LoreForge.

## Source Types

Use `source_type: conversation_synthesis` when the knowledge came primarily from reasoning during the conversation.

Use more specific types when applicable:

| Source type | Meaning |
|---|---|
| `conversation_synthesis` | Durable synthesis produced in this conversation |
| `query_result` | Answer synthesized from existing wiki notes |
| `source_grounded_answer` | Answer synthesized from cited external or wiki sources |
| `decision_rationale` | Reusable rationale or trade-off decision |
| `concept_connection` | Newly discovered relation between existing concepts |
| `human_correction` | User corrected or clarified professional knowledge |

## Evaluation

| Answer type | Value | Action |
|---|---|---|
| Comparison / trade-off analysis | High | Stage comparison card, MOC delta, or both |
| Discovered new connection between concepts | High | Stage link delta or relation card |
| Concept explanation with lasting value | Medium | Stage concept card |
| Professional method or reusable procedure | High | Stage shared method or domain card |
| Source-grounded summary | Medium | Stage source note |
| Simple lookup / one-off debug | Low | Skip |

## Routing

Resolve paths from `<wiki>/.loreforge/wiki.toml`; use these fallbacks if absent:

- inbox: `10_Inbox`
- writeback: `10_Inbox/writeback`
- domains: `20_Domains`
- shared: `30_Shared`

| Content type | Stable destination after approval | Initial staging |
|---|---|---|
| New link, See also, source reference | Existing domain card | `<writeback>/` |
| Comparison / contrast | `<domains>/<Domain>/Cards/` | `<writeback>/` |
| New concept | `<domains>/<Domain>/Cards/` | `<writeback>/` |
| Topic synthesis | `<domains>/<Domain>/MOCs/` or index delta | `<writeback>/` |
| Source-grounded summary | `<domains>/<Domain>/Sources/` | `<writeback>/` |
| Cross-domain method | `<shared>/Methods/` | `<writeback>/` |

## Flow

1. Deliver the answer first.
2. Locate the target wiki through registry, user path, or current wiki root.
3. Read `AGENTS.md`, the vault map, task view, domain map, and relevant index sections.
4. Evaluate whether the answer contains reusable professional knowledge.
5. If low value, skip or say no durable writeback is needed.
6. If useful, create a staged package under `<writeback>/<YYYY-MM-DD>-<short-slug>/`.
7. Include target domain, stable destinations, proposed new files, proposed edits, and source/provenance.
8. If the user approves stable writeback, hand off to `promote`.
9. Do not update stable cards or indexes directly from `writeback`.
10. Append a wiki log entry only when a substantive staged package is created.

## Staged Package Contract

A single conversation can produce multiple candidate notes. Put them in one package when they came from the same answer or discussion thread.

Recommended layout:

```text
<writeback>/<YYYY-MM-DD>-<short-slug>/
  manifest.md
  Cards/
  Sources/
  MOCs/
  Deltas/
```

Minimum `manifest.md`:

```markdown
---
type: writeback
source_type: conversation_synthesis
status: staged
created: YYYY-MM-DD
domain: <Domain>
provenance:
  - conversation
candidate_notes:
  - path: Cards/<candidate-card>.md
    kind: card
  - path: Sources/<candidate-source>.md
    kind: source
updates:
  - path: Cards/<existing-card>.md
    kind: note_delta
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: <why this belongs in the stable wiki>
---
# Writeback Package: <Title>

## Candidate Knowledge
<Short durable synthesis>

## Proposed Changes
- create: <path>
- update: <path> with <small delta>

## Rationale
<Why this belongs in the wiki>

## Provenance
- <conversation/source/card>
```

`promote` consumes this package and may promote multiple candidate notes in one batch.

## Stage Log Entry

For substantive writeback packages, append one wiki log entry:

```markdown
## YYYY-MM-DD | stage | writeback | <Domain or unknown>

- package:
  - `<writeback>/<YYYY-MM-DD>-<short-slug>/`
- source_type:
  - `<source type>`
- candidate_notes:
  - `Cards/<candidate-card>.md`
- reason:
  - <why this package may deserve promotion>
```

## Hard Boundary

This skill must not:

- silently edit stable wiki knowledge
- store agent-local experience in the wiki
- save full transcripts
- commit or push git changes
- rewrite indexes for unrelated topics

It may append a concise wiki log entry for a substantive staged writeback package.

## Comparison card format

```markdown
---
aliases:
tags:
  - concept
  - concept/comparison
domain: <Domain>
status: staged
created: YYYY-MM-DD
up: "[[Parent Topic]]"
---
X:: [[Concept A]]
X:: [[Concept B]]
# A vs B
## Summary
<One-line verdict>

| Dimension | A | B |
|---|---|---|
| ... | ... | ... |

## When to use A
## When to use B
## Trade-offs

## References
- [[Source Note]]
```
