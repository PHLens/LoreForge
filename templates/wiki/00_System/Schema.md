# Wiki Schema

Generic structure for a LoreForge wiki instance.

## Top-Level Layout

```text
00_System/       Rules, schema, task views, indexes
10_Inbox/        Unsorted captures and staged packages
20_Domains/      Domain-specific knowledge
30_Shared/       Cross-domain knowledge
40_Archive/      Retired material
```

## Domain Layout

```text
20_Domains/<Domain>/
  <Domain> Map.md
  +Wiki Index.md
  Cards/
  MOCs/
  Sources/
```

## Note Kinds

| Kind | Location | Purpose |
|---|---|---|
| Source | `Sources/` | Source-grounded notes, as immutable as practical |
| Card | `Cards/` | Atomic professional knowledge |
| MOC | `MOCs/` | Navigation and synthesis over mature clusters |
| Map | `<Domain> Map.md` | Domain entry point |
| Index | `+Wiki Index.md` | Compact agent-facing manifest |
| Log | `00_System/Wiki Log.md` | Human-readable log of stable promotion transactions |

## Required Frontmatter

```yaml
---
aliases:
tags:
up: "[[Parent Note]]"
status: stable
---
```

Use `status: staged` for drafts and `status: stable` for promoted notes.

## Staged Package

Processed `ingest` and `writeback` work should stage as a package:

```text
10_Inbox/<ingest|writeback>/<YYYY-MM-DD>-<short-slug>/
  manifest.md
  Sources/
  Cards/
  MOCs/
  Deltas/
```

Minimum `manifest.md`:

```yaml
---
type: <ingest|writeback>
source_type: <source type>
status: staged
domain: <Domain or Shared>
created: YYYY-MM-DD
provenance:
  - <source path/url/conversation>
candidate_notes:
  - path: Cards/<candidate-card>.md
    kind: card
updates:
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: <why this should become stable wiki knowledge>
---
```

One package may contain multiple candidate notes when they came from the same source or conversation.

## Source Types

Common source types:

| Source type | Use for |
|---|---|
| `url` | Web article or online document |
| `paper` | Research paper |
| `docs` | Documentation |
| `local_file` | Local file |
| `capture` | Previously captured inbox note |
| `research_synthesis` | Ingest result with added research |
| `conversation_synthesis` | Durable synthesis produced in conversation |
| `query_result` | Answer synthesized from existing wiki notes |
| `source_grounded_answer` | Answer synthesized from cited sources |
| `decision_rationale` | Reusable trade-off or decision rationale |
| `concept_connection` | Relation discovered between existing concepts |
| `human_correction` | User corrected or clarified professional knowledge |

## Promotion Boundary

Stable notes enter the wiki through `promote`.

Promotion updates should happen in one transaction:

1. create or move stable notes
2. update the target domain `+Wiki Index.md`
3. archive consumed staging material
4. append one entry to `00_System/Wiki Log.md`

Do not index captures or staged packages.

## Wiki Log

Default path:

```text
00_System/Wiki Log.md
```

Log meaningful wiki evolution events:

- promoted staged ingest material
- promoted writeback packages
- approved stable note edits made during promotion
- index updates caused by promotion
- substantive staged ingest package created
- substantive staged writeback package created
- lint pass with meaningful findings

Do not log ordinary query, ordinary capture, incomplete staged drafts, read-only lint with no meaningful findings, or git sync.
