---
title: Default web capture recipe
type: capture-recipe
source_type: web
template_id: web-default
triggers:
  - "url:*"
schema_triggers:
  - "schema:@Article"
  - "schema:@NewsArticle"
  - "schema:@BlogPosting"
output:
  origin: "Shared/Templates/capture/web-origin.md"
  manifest: "Shared/Templates/capture/web-manifest.md"
---

# Default Web Capture Recipe

This recipe mirrors the Obsidian Web Clipper model for LoreForge raw packages:
extract page variables, render a source note template, and preserve extraction
lineage before any domain ingest.

## Required Variables

- Preset: `{{title}}`, `{{author}}`, `{{content}}`, `{{contentHtml}}`,
  `{{url}}`, `{{domain}}`, `{{description}}`, `{{favicon}}`, `{{image}}`,
  `{{published}}`, `{{site}}`, `{{language}}`, `{{words}}`, `{{date}}`
- User state: `{{selection}}`, `{{selectionHtml}}`, `{{highlights}}`
- Meta: `{{meta:name:description}}`, `{{meta:property:og:title}}`,
  `{{meta:property:og:image}}`
- Schema: `{{schema:@Article}}`, `{{schema:@NewsArticle}}`,
  `{{schema:@BlogPosting}}`
- LoreForge capture fields: `{{source_id}}`, `{{capture_method}}`,
  `{{capture_tool}}`, `{{source_mode}}`, `{{selectors}}`, `{{assets}}`,
  `{{asset_policy}}`, `{{limitations}}`, `{{prompt_assisted}}`,
  `{{content_hash}}`

## Capture Order

1. Save the original artifact when available:
   `Shared/Raw/<source-id>/original/<filename>`.
2. Extract clean article content with `defuddle`, `obsidian-clipper`, or a
   browser-backed `topic-research` artifact.
3. If article extraction misses stable material, add CSS selectors or
   schema.org triggers and write their output into `origin.md` or `extracted/`.
4. Render `web-origin.md`, calculate its SHA-256, then render
   `web-manifest.md`.
5. Localize important diagrams, screenshots, tables, PDFs, or downloadable
   files under `assets/` or `original/`; leave decorative images as remote
   links with a limitation note.
6. Stop after the raw package. Domain `Sources/`, Cards, Atlas pages, and
   Spaces belong to ingest/update workflows.

## Selector Pattern

Use selector variables only for stable page structure:

```text
{{selector:main article}}
{{selectorHtml:pre code|markdown}}
{{selector:img.hero?src}}
{{selector:.transcript}}
```

Record selector decisions in the manifest under `extraction.selectors`.

## Prompt Policy

Prefer deterministic variables, meta tags, schema.org data, and selectors.
Prompt-derived fields are allowed only when the source structure is inconsistent
and the prompt result is saved as an extraction aid, not as a replacement for
raw source text. Set `extraction.prompt_assisted: true` and record the
prompt/model/context summary when used.
