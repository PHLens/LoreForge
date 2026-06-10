---
title: "{{title}}"
source_id: "{{source_id}}"
source_type: web
source_language: "{{language}}"
retrieved_at: "{{date}}"
source_url: "{{url}}"
source_description: "{{description}}"
content_hash: "{{content_hash}}"
origin: "Shared/Raw/{{source_id}}/origin.md"
candidate_domains: []
compiled_pages: []
status: captured
artifacts: []
limitations: "{{limitations}}"
extraction:
  method: "{{capture_method}}"
  tool: "{{capture_tool}}"
  source_mode: "{{source_mode}}"
  template: "Shared/Templates/capture/web-origin.md"
  recipe: "Shared/Templates/capture/web-capture-recipe.md"
  variables:
    - title
    - url
    - author
    - site
    - description
    - published
    - language
    - words
    - image
    - favicon
    - content
    - contentHtml
    - selection
    - highlights
    - meta
    - schema
  selectors: []
  schema_triggers:
    - "schema:@Article"
    - "schema:@NewsArticle"
    - "schema:@BlogPosting"
  filters:
    - markdown
    - trim
  assets: "{{asset_policy}}"
  prompt_assisted: false
---

# {{title}}

Raw manifest template for a web capture package. Render this into
`Shared/Raw/{{source_id}}/manifest.md`, then replace `content_hash` with the
SHA-256 of the rendered `origin.md`.
