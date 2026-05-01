# Schema

LoreForge wiki instances use one shared wiki root with expert-owned domains.

## Wiki Shape

```text
wiki/
  00_System/
  Calendar/
    dailynotes/
  Shared/
    SourceRecords/
    Raw/
    Templates/
  Domains/
    <domain>/
      SCHEMA.md
      index.md
      log.md
      Atlas/
      Cards/
      Sources/
      Spaces/
      Extras/
```

`00_System/` is the wiki-level operating surface. It typically contains
`index.md`, `domains.md`, and `wiki-layout.md`. `Calendar/` stores dated
personal notes such as daily notes. `Shared/SourceRecords/` stores shared raw
source records, `Shared/Raw/` stores shared source attachments, and
`Shared/Templates/` stores reusable templates once for the whole wiki. Each
`Domains/<domain>/` is a self-contained LLM Wiki maintained by one expert agent.

## Calendar Files

| Path | Purpose |
|---|---|
| `Calendar/dailynotes/` | Default folder for daily diary or daily-note pages |

## Shared Files

| Path | Purpose |
|---|---|
| `Shared/SourceRecords/` | Wiki-root shared raw source records, captures, metadata, and source text |
| `Shared/Raw/` | Wiki-root shared source attachments such as PDFs, images, HTML snapshots, and manifests |
| `Shared/Templates/` | Wiki-root reusable note templates, including diary templates |

## Domain Files

| Path | Purpose |
|---|---|
| `SCHEMA.md` | Domain boundary, conventions, taxonomy, and update rules |
| `index.md` | Mechanical inventory with one-line page summaries |
| `log.md` | Reverse chronological action log, newest entry first |
| `Atlas/` | Maps of Content (MOCs), emergent thinking views |
| `Cards/` | Durable concepts, methods, patterns, tradeoffs, comparisons |
| `Sources/` | `Domains/<domain>/Sources/` domain-specific source lenses linked to wiki-root shared `Shared/SourceRecords/` records |
| `Spaces/` | Durable non-Card objects, contexts, and archive space |
| `Extras/` | `Domains/<domain>/Extras/` domain-owned non-source attachments; source artifacts belong in wiki-root `Shared/Raw/` |

## Operating Rules

Agents should orient before writing:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read recent `log.md` entries.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages.

Routine maintenance writes directly inside the selected domain after
orientation. There is no staged promotion pipeline in the active core workflow.

After substantive changes, update `index.md` when stable pages are created,
archived, renamed, or materially changed. Insert a concise newest-first
`log.md` entry directly below the log heading and instruction block, before the
previous newest entry.

## Source Capture

Raw source records preserve the source language by default and live under
`Shared/SourceRecords/`. For text articles, blogs, docs, and pasted text, keep title,
author/publisher, dates, canonical URL, headings, links, and local image
references. Prefer complete transcription when the material is user-provided,
local, permissively licensed, public domain, or otherwise appropriate to reuse in
full. Otherwise keep a faithful structured source record and record only
concrete capture limitations.

Durable source attachments belong under `Shared/Raw/<source-slug>/` and
should be linked from the shared source record and any relevant domain lens.
Domain `Sources/` pages should summarize why the shared source matters to that
domain and link to `Shared/SourceRecords/...`. Source metadata should point to
wiki-local files, not temporary extractor outputs such as
`/tmp/topic-research/...`.

## Boundaries

- Do not store agent-local memory, preferences, task state, or chat transcripts
  in the wiki.
- Do not write across domains unless the user explicitly asks.
- Do not duplicate the same raw source or PDF under multiple domains.
- Do not index `Extras/` directly.
- Do not index `Spaces/_archive/` or transient workspace notes.
- Mark low-confidence and contested knowledge explicitly.
