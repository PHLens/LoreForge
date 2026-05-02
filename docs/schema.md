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
      <source-id>/
        manifest.md
        original/
        extracted/
    Templates/
  Domains/
    <domain>/
      SCHEMA.md
      index.md
      log.md
      Atlas/
      Cards/
      Sources/  # optional compiled source notes
      Spaces/
```

`00_System/` is the wiki-level operating surface. It typically contains
`index.md`, `domains.md`, and `wiki-layout.md`. `Calendar/` stores dated
personal notes such as daily notes. `Shared/Raw/<source-id>/` stores the
canonical raw source package, `Shared/Templates/` stores reusable templates
once for the whole wiki, and `Shared/SourceRecords/` is legacy compatibility
only. Each `Domains/<domain>/` is a self-contained LLM Wiki maintained by one
expert agent.

## Calendar Files

| Path | Purpose |
|---|---|
| `Calendar/dailynotes/` | Default folder for daily diary or daily-note pages |

## Shared Files

| Path | Purpose |
|---|---|
| `Shared/Raw/` | Wiki-root raw source packages. Each package holds a `manifest.md`, original artifacts, extracted artifacts, and any source-specific assets |
| `Shared/Templates/` | Wiki-root reusable note templates, including diary templates |
| `Shared/SourceRecords/` | Legacy shared source record area kept only for older imports and compatibility |

## Domain Files

| Path | Purpose |
|---|---|
| `SCHEMA.md` | Domain boundary, conventions, taxonomy, and update rules |
| `index.md` | Mechanical inventory with one-line page summaries |
| `log.md` | Reverse chronological action log, newest entry first |
| `Atlas/` | Maps of Content (MOCs), emergent thinking views |
| `Cards/` | Durable concepts, methods, patterns, tradeoffs, comparisons |
| `Sources/` | Optional `Domains/<domain>/Sources/` compiled source notes for special-purpose views, comparisons, or legacy compatibility |
| `Spaces/` | Durable non-Card objects, contexts, and archive space |
| `Extras/` | Optional domain-owned non-source attachments; create only when needed |

## Operating Rules

Agents should orient before writing:

1. Read `SCHEMA.md`.
2. Read `index.md`.
3. Read recent `log.md` entries.
4. Search existing pages for the topic.
5. Read relevant `Atlas/`, `Cards/`, `Sources/`, and `Spaces/` pages.

Routine maintenance writes directly inside the selected domain after
orientation. There is no staged promotion pipeline in the active core workflow.

Query and ingest should stay question-driven: start from the problem being
answered, then decide whether the raw package, a compiled source note, or a
durable Card/Atlas/Space page is actually warranted.

After substantive changes, update `index.md` when stable pages are created,
archived, renamed, or materially changed. Insert a concise newest-first
`log.md` entry directly below the log heading and instruction block, before the
previous newest entry.

## Source Capture

Raw source packages preserve the source language by default and live under
`Shared/Raw/<source-id>/`. Each package should include a `manifest.md` with the
source metadata, source hash, `compiled_pages`, capture notes, and links to the
original and extracted artifacts. For text articles, blogs, docs, and pasted
text, keep title, author/publisher, dates, canonical URL, headings, links, and
local image references. Prefer complete transcription when the material is
user-provided, local, permissively licensed, public domain, or otherwise
appropriate to reuse in full. Otherwise keep a faithful structured capture and
record only concrete limitations.

Domain `Sources/` pages are optional compiled source notes. Use them only when a
source deserves a special-purpose note, comparison, or legacy compatibility
note. They should summarize why the source matters to that domain and link to
the raw package and any compiled pages. Source metadata should point to
wiki-local files, not temporary extractor outputs such as
`/tmp/topic-research/...`.

## Boundaries

- Do not store agent-local memory, preferences, task state, or chat transcripts
  in the wiki.
- Do not write across domains unless the user explicitly asks.
- Do not duplicate the same raw source or PDF under multiple domains.
- Do not treat `Shared/SourceRecords/` as source-of-truth; if it exists, only
  use it for legacy migration or compatibility.
- Do not mechanically split every source into a Source note and new Cards.
  Start from the question and create durable synthesis only when it reduces
  future work.
- If `Extras/` exists, do not index it directly.
- Do not index `Spaces/_archive/` or transient workspace notes.
- Mark low-confidence and contested knowledge explicitly.
