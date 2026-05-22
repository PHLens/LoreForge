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
- preserve source language, useful structure, and human-captured artifact filenames
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
fit a source-id. Preserve the source language, title, headings, links, and
concrete capture limitations. For third-party web pages where full
transcription is not appropriate, keep a faithful structured capture with the
useful excerpts and grounded notes.

Use `manifest.md` for metadata and lifecycle state:

```yaml
---
title: "<source title>"
source_id: "<source-id>"
source_type: "web|pdf|file|paste|repo|export|research-pack"
source_language: "<language>"
captured_at: "YYYY-MM-DD"
canonical_url: "<url or empty>"
content_hash: "<sha256 of origin.md>"
origin: "Shared/Raw/<source-id>/origin.md"
candidate_domains: []
compiled_pages: []
status: captured
artifacts: []
limitations: "<concrete limitations or empty>"
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
