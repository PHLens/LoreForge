# Schema

LoreForge wiki instances use one shared wiki root with expert-owned domains.

## Wiki Shape

```text
wiki/
  00_System/
  Calendar/
    dailynotes/
  Shared/
    Raw/
      clip-or-source-title.*  # capture-only flat raw clips before ingest
      <source-id>/
        origin.md
        manifest.md
        original/
        extracted/
        assets/
    Templates/
  Domains/
    <domain>/
      SCHEMA.md
      index.md
      log.md
      Atlas/
      Cards/
      Sources/  # optional compiled source excerpts
      Spaces/
```

`00_System/` is the wiki-level operating surface. It typically contains
`index.md`, `domains.md`, and `wiki-layout.md`. `Calendar/` stores dated
personal notes such as daily notes. `Shared/Raw/` stores flat capture-only clips
first and normalized source packages under `Shared/Raw/<source-id>/` after
ingest. `Shared/Templates/` stores reusable templates once for the whole wiki.
Each `Domains/<domain>/` is a self-contained LLM Wiki maintained by one expert
agent.

## Calendar Files

| Path | Purpose |
|---|---|
| `Calendar/dailynotes/` | Default folder for daily diary or daily-note pages |

## Shared Files

| Path | Purpose |
|---|---|
| `Shared/Raw/` | Wiki-root raw source area. Capture writes flat raw clips here; ingest normalizes selected clips into `Shared/Raw/<source-id>/origin.md`, `manifest.md`, original artifacts, extracted artifacts, and any source-specific assets |
| `Shared/Templates/` | Wiki-root reusable note templates, including diary templates |

## Formula Notation

When wiki content includes equations or derivations, write them in LaTeX:

- use inline math `$...$` for expressions inside prose
- use display math `$$...$$` for standalone equations
- avoid plain-text pseudo-notation when the page is meant to be rendered and reviewed

This keeps Obsidian rendering and Markdown diffs consistent across wiki instances.

## Domain Files

| Path | Purpose |
|---|---|
| `SCHEMA.md` | Domain boundary, conventions, taxonomy, and update rules |
| `index.md` | Mechanical inventory with one-line page summaries |
| `log.md` | Reverse chronological action log, newest entry first |
| `Atlas/` | Maps of Content (MOCs), emergent thinking views |
| `Cards/` | Durable concepts, methods, patterns, tradeoffs, comparisons |
| `Sources/` | Optional source excerpts or source-specific lenses for large raw packages |
| `Spaces/` | Durable non-Card objects, contexts, and archive space |
| `Extras/` | Optional domain-owned non-source attachments; create only when needed |

Tags are stable classification labels, not keyword dumps. Prefer 1-3 tags per
page and treat tag sprawl as a lint smell rather than a richer description.

## Operating Rules

Agents should orient before writing domain pages:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read recent `log.md` entries.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages.

Routine maintenance writes directly inside the selected domain after
orientation. There is no staged promotion pipeline in the active core workflow.
Capture-only writes may create or refresh flat files under `Shared/Raw/` after
the wiki root is resolved; compiled domain updates still require orientation
first.

Query and ingest should stay question-driven: start from the problem being
answered, then decide whether the raw package, an optional domain Source note,
or a durable Card/Atlas/Space page is actually warranted.

When several raw clips are present, a router or caller may group them by
candidate domain and dispatch bounded parallel ingest jobs. Each domain expert
still owns normalization, domain page writes, index updates, and log entries for
its domain.

After substantive changes, update `index.md` when stable pages are created,
archived, renamed, or materially changed. Insert a concise newest-first
`log.md` entry directly below the log heading and instruction block, before the
previous newest entry.

## Source Capture

Raw source clips preserve the source language by default. Capture writes raw
clip files directly under `Shared/Raw/`. Ingest derives a stable `source-id`,
normalizes each selected clip into `Shared/Raw/<source-id>/`, and adds
`origin.md` for the raw clip/transcription plus `manifest.md` with the source
metadata, `content_hash`, `compiled_pages`, `candidate_domains`, capture notes,
and links to the original and extracted artifacts. For text articles, blogs,
docs, and pasted text, keep title, author/publisher, dates, canonical URL,
headings, links, and local image references. Prefer complete transcription when
the material is user-provided, local, permissively licensed, public domain, or
otherwise appropriate to reuse in full. Otherwise keep a faithful structured
capture and record only concrete limitations.

Compiled domain pages do not carry YAML `sources:` links. Put source-backed
provenance in body footnotes that point to raw manifests or domain source
notes, for example `[^1]: [[Shared/Raw/<source-id>/manifest.md]]` or
`[^1]: [[Sources/source-note-name]]`. Source metadata should point to wiki-local
files, not temporary extractor outputs such as `/tmp/topic-research/...`.

## Boundaries

- Do not store agent-local memory, preferences, task state, or chat transcripts
  in the wiki.
- Do not write across domains unless the user explicitly asks.
- Do not duplicate the same raw source or PDF under multiple domains.
- Do not treat capture and ingest as the same action.
- Do not mechanically split every source into a raw package, Source note, and
  new Cards.
  Start from the question and create durable synthesis only when it reduces
  future work.
- If `Extras/` exists, do not index it directly.
- Do not index `Spaces/_archive/` or transient workspace notes.
- Mark low-confidence and contested knowledge explicitly.
