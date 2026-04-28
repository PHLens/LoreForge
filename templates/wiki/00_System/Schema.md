# Wiki Schema

Generic structure for a LoreForge wiki instance.

## Top-Level Layout

```text
00_System/       Rules, schema, task views, index, log
10_Inbox/        Staged ingest and writeback packages
Cards/           Flat stable atomic knowledge
Sources/         Source-grounded notes by source type
MOCs/            Emergent semantic views
Archive/         Closed packages and exceptional retired material
```

## Note Kinds

| Kind | Location | Purpose |
|---|---|---|
| Card | `Cards/` | Atomic professional knowledge |
| Source | `Sources/<Type>/` | Source-grounded notes and provenance |
| MOC | `MOCs/` | Navigation and synthesis over mature clusters |
| Index | `00_System/+Wiki Index.md` | Compact card inventory |
| Log | `00_System/Wiki Log.md` | Human-readable log of meaningful wiki evolution |

## Card Frontmatter

```yaml
---
status: stable
created: YYYY-MM-DD
kind: card
aliases: []
tags: []
up: ""
---
```

`kind` is structural only. Tags are freeform human and agent-maintained signals.

## Source Frontmatter

```yaml
---
status: stable
created: YYYY-MM-DD
kind: source
source_type: paper
source_system: zotero
url: ""
accessed: YYYY-MM-DD
---
```

`source_type` determines placement under `Sources/<Type>/`. `source_system` records the import or generation system.

## MOC Frontmatter

```yaml
---
status: stable
created: YYYY-MM-DD
kind: moc
aliases: []
tags:
  - map
up: ""
---
```

`map` is a recommended template default, not a lint-enforced taxonomy.

## Source Types

Common source type directories:

| Directory | Use for |
|---|---|
| `Sources/Papers/` | Research papers |
| `Sources/Articles/` | Web articles and essays |
| `Sources/Docs/` | Documentation |
| `Sources/Books/` | Books and chapters |
| `Sources/Talks/` | Talks, videos, podcasts, and lectures |
| `Sources/Repos/` | Repository or codebase notes |
| `Sources/Datasets/` | Dataset descriptions |
| `Sources/Local/` | Local files |
| `Sources/Other/` | Sources that do not fit the standard set |

## Wiki Index

`00_System/+Wiki Index.md` is the minimum card retrieval contract.

- Every stable card must appear in the index.
- MOCs may be listed as convenience pointers, but are not required.
- Sources are not listed by default.
- Staged packages and archived packages must not be listed.

## Staged Package

Processed `ingest` and `writeback` work should stage as a package:

```text
10_Inbox/<ingest|writeback>/<YYYY-MM-DD>-<short-slug>/
  manifest.md
  Cards/
  Sources/
  MOCs/
  Deltas/
```

Minimum `manifest.md`:

```yaml
---
type: <ingest|writeback>
source_type: <source type>
status: staged
created: YYYY-MM-DD
provenance:
  - <source path/url/conversation>
candidate_notes:
  - Cards/<candidate-card>.md
updates:
  - 00_System/+Wiki Index.md
promotion_reason: <why this should become stable wiki knowledge>
---
```

`candidate_notes` are package-relative path lists. `updates` are target-repo-relative paths changed by promotion. Do not use `domain`, `path:`, or `kind:` objects in the manifest.

## Promotion Boundary

Stable notes enter the wiki through `promote`.

Promotion updates should happen in one transaction:

1. create or move reviewed staged notes into stable locations
2. update `00_System/+Wiki Index.md` for promoted cards
3. optionally update MOCs
4. move consumed staging material to `Archive/promoted/` or `Archive/rejected/`
5. append one entry to `00_System/Wiki Log.md`

Do not index staged packages, sources, or archived packages in `00_System/+Wiki Index.md`.

## Wiki Log

Default path:

```text
00_System/Wiki Log.md
```

Log meaningful wiki evolution events:

- promoted staged ingest material
- promoted writeback packages
- approved stable note edits made during promotion
- card index updates caused by promotion
- lint pass with meaningful findings

Do not log ordinary query, ordinary staged package creation, incomplete staged drafts, read-only lint with no meaningful findings, or git sync.
