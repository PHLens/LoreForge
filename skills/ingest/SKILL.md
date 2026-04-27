---
name: ingest
description: Use for LoreForge source intake: capture URLs/notes, process articles/papers/docs/files/captured notes, or research and stage source-derived wiki candidate packages.
user-invocable: true
---

# Ingest

Ingest source material into a LoreForge wiki instance.

`ingest` handles external sources. It has a quick capture mode and heavier processing modes.

## Trigger

`ingest`, `capture`, `process note(s)`, `处理笔记`

Modes:

| Mode | Use when | Output |
|---|---|---|
| `capture` | Material may be useful but domain/value is unclear | short note under `<capture>/` |
| `process` | Source is ready to turn into wiki candidates | staged package under `<ingest>/` |
| `research` | Source needs additional research before staging | staged package under `<ingest>/` |

Acceptable inputs:

- inbox note created by `capture`
- source note
- local file
- URL or article
- paper, docs, transcript, issue, PR, or dataset description
- user-provided source material

## Workflow

1. Locate the target wiki through `~/.config/loreforge/registry.toml`, a user-provided path, or the current directory if it contains `.loreforge/wiki.toml`.
2. Read `<wiki>/.loreforge/wiki.toml` and resolve configured paths. Fallbacks:
   - inbox: `10_Inbox`
   - capture: `10_Inbox/capture`
   - ingest: `10_Inbox/ingest`
   - domains: `20_Domains`
   - shared: `30_Shared`
3. Read the wiki `AGENTS.md`, vault map, relevant task view, domain map, and relevant index sections.
4. If mode is `capture`, save a short capture note and stop.
5. If mode is `process` or `research`, read the source material or captured inbox note to understand content and provenance.
6. If content is incomplete and mode is `research`, use an appropriate research skill or web search.
7. Check for existing related source notes, cards, maps, and shared methods before creating new notes.
8. Create a staged package with source notes, candidate cards, optional MOC drafts, and deltas. Keep cards atomic: one durable concept per card.
9. Add framework-required metadata and tags.
10. Propose related links, index additions, and promotion destinations.
11. Append a wiki log entry only when a substantive staged package is created.
12. Hand off approved stable writes to `promote`; do not update stable notes or indexes directly from `ingest`.

## Staging

- Capture notes go to `<capture>/<YYYY-MM-DD>-<short-slug>.md`.
- Processed material stages as a package under `<ingest>/<YYYY-MM-DD>-<short-slug>/`.
- Use subfolders under the staging root when helpful:
  - `Sources/`
  - `Cards/`
  - `MOCs/`
  - `Deltas/`
  - `manifest.md`
- Stable promotion destinations:
  - source summaries: `<domains>/<Domain>/Sources/`
  - concept cards: `<domains>/<Domain>/Cards/`
  - topic maps: `<domains>/<Domain>/MOCs/`
  - cross-domain methods: `<shared>/Methods/`
- Obsidian adapter vaults may define different staging conventions; follow their adapter docs after resolving the wiki type.
- Wait for user confirmation before moving staged notes to stable locations.
- Use `promote` for stable moves, index updates, and promotion log entries.

## Staged Package Contract

Every processed ingest package must include `manifest.md`.

Minimum manifest:

```markdown
---
type: ingest
source_type: <url|paper|docs|local_file|source_note|capture|user_material|research_synthesis>
status: staged
domain: <Domain or unknown>
created: YYYY-MM-DD
provenance:
  - <source url/path/note>
candidate_notes:
  - path: Sources/<source-note>.md
    kind: source
  - path: Cards/<concept-card>.md
    kind: card
updates:
  - path: +Wiki Index.md
    kind: index_delta
promotion_reason: <why this should become stable wiki knowledge>
---
# Package: <Title>

## Summary
<What was ingested>

## Promotion Plan
- create: <candidate note path>
- update: <candidate delta path>
```

`promote` consumes this package. It may promote multiple candidate notes from one package.

## Stage Log Entry

For substantive `process` or `research` packages, append one wiki log entry:

```markdown
## YYYY-MM-DD | stage | ingest | <Domain or unknown>

- package:
  - `<ingest>/<YYYY-MM-DD>-<short-slug>/`
- source_type:
  - `<source type>`
- candidate_notes:
  - `Cards/<candidate-card>.md`
- reason:
  - <why this package may deserve promotion>
```

Do not log ordinary captures.

## Hard Boundary

This skill must not:

- store agent-local experience in the wiki
- save full chat transcripts
- silently edit stable cards
- commit or push git changes
- use raw web search when existing wiki knowledge is sufficient

It may append a concise wiki log entry for a substantive staged ingest package. It must not log ordinary captures.

## Concept Card Template

```markdown
---
aliases:
  - Alternative names
tags:
  - concept
  - concept/<domain>
domain: <Domain>
status: staged
created: YYYY-MM-DD
up: "[[Parent Concept]]"
---
X:: [[Related Concept]]
# <Concept>

## Why It Matters
<Motivation or reusable context>

## Definition
<Definition and details>

## References
- [[Source Note]]
```
