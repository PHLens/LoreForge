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
| `capture` | Material may be useful but structure/value is unclear | short note under `<capture>/` |
| `process` | Source is ready to turn into wiki candidates | staged package under `<ingest>/` |
| `research` | Source needs additional research before staging | staged package under `<ingest>/` |

Acceptable inputs:

- inbox note created by `capture`
- source note
- local file
- URL or article
- paper, docs, transcript, issue, PR, repository, or dataset description
- user-provided source material

## Workflow

1. Locate the target wiki through `~/.config/loreforge/registry.toml`, a user-provided path, or the current directory if it contains `.loreforge/wiki.toml`.
2. Read `<wiki>/.loreforge/wiki.toml` and resolve configured paths. Fallbacks:
   - inbox: `10_Inbox`
   - capture: `10_Inbox/capture`
   - ingest: `10_Inbox/ingest`
   - cards: `Cards`
   - sources: `Sources`
   - mocs: `MOCs`
3. Read the wiki `AGENTS.md`, vault map, ingest view, card index, and relevant MOCs or cards.
4. If mode is `capture`, save a short capture note and stop.
5. If mode is `process` or `research`, read the source material or captured inbox note to understand content and provenance.
6. If content is incomplete and mode is `research`, use an appropriate research skill or web search.
7. Check existing Cards, MOCs, and Sources before creating new notes.
8. Create a staged package with source notes, candidate cards, optional MOC drafts, and deltas.
9. Add framework-required metadata and tags.
10. Propose related links, index additions, and promotion destinations.
11. Append a wiki log entry only when a substantive staged package is created.
12. Hand off approved stable writes to `promote`; do not update stable notes or indexes directly from `ingest`.

## Staging

- Capture notes go to `<capture>/<YYYY-MM-DD>-<short-slug>.md`.
- Processed material stages as a package under `<ingest>/<YYYY-MM-DD>-<short-slug>/`.
- Use subfolders under the staging root when helpful:
  - `Sources/<Type>/`
  - `Cards/`
  - `MOCs/`
  - `Deltas/`
  - `manifest.md`
- Stable promotion destinations:
  - source summaries: `<sources>/<Type>/`
  - concept cards: `<cards>/`
  - topic maps: `<mocs>/`
- If a wiki repo defines custom index or log paths, follow its `.loreforge/wiki.toml` after resolving the wiki.
- Wait for user confirmation before moving staged notes to stable locations.
- Use `promote` for stable moves, index updates, MOC updates, archive moves, and promotion log entries.

## Staged Package Contract

Every processed ingest package must include `manifest.md`.

Minimum manifest:

```markdown
---
type: ingest
source_type: <article|paper|docs|book|talk|repo|dataset|local|capture|research_synthesis|user_material>
status: staged
created: YYYY-MM-DD
provenance:
  - <source url/path/note>
candidate_notes:
  - Sources/Docs/<source-note>.md
  - Cards/<concept-card>.md
updates:
  - 00_System/+Wiki Index.md
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

If the package contains card candidates, `updates` must include the configured card index, usually `00_System/+Wiki Index.md`. MOC updates are optional. Source-only packages do not need an index update.

## Stage Log Entry

For substantive `process` or `research` packages, append one wiki log entry:

```markdown
## YYYY-MM-DD | stage | ingest | <package-slug>

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
status: staged
created: YYYY-MM-DD
kind: card
aliases:
  - Alternative names
tags:
  - concept
up: ""
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
