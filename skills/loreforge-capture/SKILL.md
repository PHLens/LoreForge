---
name: loreforge-capture
description: Internal LoreForge workflow for turning URLs, files, pasted text, documents, or research outputs into raw source packages under Shared/Raw without compiling domain pages. Use before ingest when a source must be preserved first.
user-invocable: false
version: 0.2.0
---

# LoreForge Capture

Preserve source material once as a wiki-root `Shared/Raw/<source-id>/` package.
Capture does not decide domain synthesis and does not create durable domain
pages.

Always:

- resolve the wiki root first, using `loreforge-config` rules
- derive a stable, readable `source-id`
- write only raw source packages under `Shared/Raw/<source-id>/`
- create `origin.md` and `manifest.md` for every capture
- preserve source language, useful structure, links, metadata, and
  human-captured artifact filenames
- choose and record a capture plan before extraction: source mode, extractor,
  selectors, fixed capture-card format, assets to localize, and expected
  limitations
- keep transient extractor paths out of durable wiki metadata
- report the captured path and concrete capture limitations

Do not:

- create `Cards/`, `Atlas/`, `Spaces/`, or domain `Sources/`
- update domain `index.md` or `log.md`
- route or choose final domain ownership

## Inputs

Accept:

- URLs and web pages
- PDFs and local files
- pasted text
- exported docs, human clipper captures, or repos
- `topic-research` research packs
- `convert-to-markdown` or `defuddle` output

Use helper skills as needed:

- `topic-research` for browser-backed pages, WeChat, Zhihu, and source packs
- `defuddle` for lightweight web-to-Markdown extraction
- `convert-to-markdown` for local documents and exported pages

## Web Capture Flow

For web pages, follow a clipper-style pipeline inspired by Obsidian Web
Clipper's capture model:

1. **Snapshot first.** Save a faithful source artifact under `original/` when
   available, such as exported Markdown, saved HTML, PDF, selected text, or a
   human clipper file. Do not treat an extractor's temporary path as durable
   provenance.
2. **Extract deterministic variables.** Prefer deterministic extraction before
   LLM interpretation: readable article body, title, author, site, description,
   published date, canonical URL, language, word count, favicon, social image,
   meta tags, schema.org JSON-LD, and user-provided selection/highlights when
   present.
3. **Use selectors for site-specific structure.** When the main article
   extractor misses important structure, record the CSS selectors or
   schema.org triggers used to capture comments, transcripts, code blocks,
   tables, figures, or other stable page regions. Selector output belongs in
   `origin.md` or `extracted/`, not in a domain page during capture.
4. **Render a fixed capture card.** Render `origin.md` in the
   clipper-like capture card format below. Mirror Web Clipper's default field
   logic: `title`, `source`, `author`, `published`, `created`,
   `description`, `tags`, and `content` are stable fields, while selector,
   schema, and meta variables fill optional structured fields. Use `created`
   for the capture-card creation date; keep `retrieved_at` as the raw package
   lifecycle field in frontmatter and `manifest.md`. For direct web capture
   they usually match, and the visible `Captured:` line renders `created`.
   Do not list `retrieved_at` as a capture-card variable unless the rendered
   card explicitly names it. Do not invent a new per-source card shape unless
   the source cannot fit the fixed format. Filter `content` before writing it:
   remove title, author, citation, source URL, publication date, and other
   metadata already promoted into frontmatter, the source quote block, or
   Structured Metadata. The content section should hold the article body,
   abstract, selected text, highlights, or source-specific substance, not a
   second nested capture card.
5. **Localize important assets.** Save figures, diagrams, screenshots, or
   downloaded files under `assets/` or `original/` when they matter for later
   audit or offline reuse. Rewrite important references in `origin.md` to
   wiki-local paths such as `Shared/Raw/<source-id>/assets/<name>`.
6. **Record extraction lineage.** `manifest.md` must say which capture route
   was used: helper skill or tool, extractor, source mode, selector choices,
   original artifact, extracted artifacts, asset handling, and any auth/session
   assumptions.

Treat this as a capture discipline, not as an Obsidian dependency. If the
`obsidian-clipper` CLI/API or an exported Obsidian Web Clipper note is already
available, its output is acceptable input. Otherwise use the bundled
`defuddle`, `topic-research`, and `convert-to-markdown` helpers to produce the
same raw-package contract.

Avoid prompt/LLM variables by default. Use them only when deterministic meta,
schema, selector, or article extraction cannot capture a stable field. When a
prompt-derived field is used, store the prompt/context/model or a concise
description in `manifest.md` and keep quoted source text grounded in the
deterministic source capture.

## Capture Card Format

For web pages, `origin.md` should use this fixed, Web Clipper-like field order.
Use empty values only when a field is genuinely unavailable.

```markdown
---
title: "<title>"
source_id: "<source-id>"
type: source
source_type: web
source_language: "<language>"
retrieved_at: "YYYY-MM-DD"
created: "YYYY-MM-DD"
source_url: "<canonical url>"
author: "<author>"
published: "<published date or empty>"
site: "<site or publisher>"
description: "<description or excerpt>"
tags:
  - raw-capture
  - web
origin: "Shared/Raw/<source-id>/origin.md"
candidate_domains: []
compiled_pages: []
status: captured
capture_card:
  format: web-clipper-like
  source_mode: "article|selection|highlights|selector|full"
  variables:
    - title
    - source
    - author
    - published
    - created
    - description
    - tags
    - content
---

# <title>

> Source: <canonical url>
> Author: <author>
> Published: <published date or empty>
> Captured: <created>

## Description

<description or excerpt>

## Content

<clean markdown content, selected text, or highlights; omit duplicated title,
author, citation, source URL, and publication metadata already captured above>

## Structured Metadata

- site: <site or publisher>
- language: <language>
- words: <word count>
- image: <social image or local asset path>
- schema: <schema.org values when useful>
- selectors: <selector names or empty>

## Capture Limits

<concrete limitations, auth/session assumptions, or missing assets>
```

`manifest.md` records package lifecycle and extraction lineage; `origin.md`
keeps the human- and agent-readable capture card.

## Raw Package Shape

Write one package per source:

```text
Shared/Raw/<source-id>/
  manifest.md
  origin.md
  original/
  extracted/
  assets/
```

Only `manifest.md` and `origin.md` are required. Create `original/`,
`extracted/`, and `assets/` only when useful. Paper workflows should default
to compact metadata-and-text capture rather than archiving every PDF binary;
see `loreforge-paper` for the paper-specific artifact policy.

Use `origin.md` for canonical agent-readable source text or for a thin wrapper
around preserved artifacts. For human-captured Markdown/HTML/PDF, keep the
export unchanged under `original/` with its original filename and record that
artifact in `manifest.md`; do not rename or rewrite the user's clip merely to
fit a source-id. Preserve the source language, title, headings, links, tables,
code blocks, figure captions, local image references, selected text, and
highlights when present. For third-party web pages where full transcription is
not appropriate, keep a faithful structured capture with useful excerpts,
source-grounded notes, and concrete limitations.

Use `manifest.md` for metadata and lifecycle state:

```yaml
---
title: "<source title>"
source_id: "<source-id>"
source_type: "web|pdf|file|paste|repo|export|research-pack"
source_language: "<language>"
retrieved_at: "YYYY-MM-DD"
source_url: "<canonical url when available>"
source_description: "<source description when no source_url is available>"
content_hash: "<sha256 of origin.md>"
origin: "Shared/Raw/<source-id>/origin.md"
candidate_domains: []
compiled_pages: []
status: captured
artifacts: []
limitations: "<concrete limitations or empty>"
extraction:
  primary_method: "defuddle|topic-research|obsidian-clipper|convert-to-markdown|manual"
  methods:
    - name: "<tool or helper>"
      role: "primary-content|metadata-supplement|asset-capture|manual-cleanup"
      artifacts: []
  capture_card_format: "web-clipper-like"
  variables: []
  selectors: []
  schema_triggers: []
  filters: []
  content_filters:
    - "dedupe fixed-field metadata"
  fallback:
    search_source: ""
    status: "available|unavailable|not-used"
    reason: ""
    substitute_sources: []
  assets: "none|linked|localized|partial"
  prompt_assisted: false
---
```

Capture leaves `compiled_pages` empty and `status: captured`. Ingest may update
the same package with candidate domains, compiled page pointers, additional
artifacts, and a compiled status.

## Output Contract

Return:

- capture path(s)
- raw package path
- `source-id`
- source title or filename
- canonical URL or source description when known
- source language when known
- limitations, auth/session assumptions, or missing assets
- suggested candidate domains only if obvious, without writing domain pages
