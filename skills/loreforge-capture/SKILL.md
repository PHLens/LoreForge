---
name: loreforge-capture
description: Internal LoreForge workflow for turning URLs, files, pasted text, documents, or research outputs into raw clips under Shared/Raw without compiling domain pages. Use before ingest when a source must be preserved first.
user-invocable: false
version: 0.1.0
---

# LoreForge Capture

Preserve source material once under the wiki-root `Shared/Raw/` area. Capture
does not decide domain synthesis and does not create durable domain pages.

Always:

- resolve the wiki root first, using `loreforge-config` rules
- write only flat raw clips under `Shared/Raw/`
- preserve source language and useful structure
- keep transient extractor paths out of durable wiki metadata
- report the captured path and concrete capture limitations

Do not:

- create `Cards/`, `Atlas/`, `Spaces/`, or domain `Sources/`
- create source-id directories, `origin.md`, or `manifest.md`
- update domain `index.md` or `log.md`
- route or choose final domain ownership

## Inputs

Accept:

- URLs and web pages
- PDFs and local files
- pasted text
- exported docs or repos
- `topic-research` research packs
- `convert-to-markdown` or `defuddle` output

Use helper skills as needed:

- `topic-research` for browser-backed pages, WeChat, Zhihu, and source packs
- `defuddle` for lightweight web-to-Markdown extraction
- `convert-to-markdown` for local documents and exported pages

## Raw Clip Shape

Write a single capture artifact directly under `Shared/Raw/`:

```text
Shared/Raw/<descriptive-source-name>.md
Shared/Raw/<descriptive-source-name>.pdf
Shared/Raw/<descriptive-source-name>.html
```

For multi-file captures, create a flat capture folder only when necessary:

```text
Shared/Raw/<descriptive-source-name>/
  clip.md
  assets/
```

Do not normalize into `Shared/Raw/<source-id>/origin.md` and `manifest.md`.
Normalization belongs to ingest.

## Output Contract

Return:

- capture path(s)
- source title or filename
- canonical URL or source description when known
- source language when known
- limitations, auth/session assumptions, or missing assets
- suggested candidate domains only if obvious, without writing domain pages
