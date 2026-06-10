---
title: "{{title}}"
created: "{{date}}"
type: source
source_type: web
source_language: "{{language}}"
retrieved_at: "{{date}}"
source_url: "{{url}}"
origin: "Shared/Raw/{{source_id}}/origin.md"
candidate_domains: []
compiled_pages: []
status: captured
---

# {{title}}

> Source: {{url}}
> Site: {{site}}
> Author: {{author}}
> Published: {{published}}
> Retrieved: {{date}}
> Capture method: {{capture_method}}
> Limitations: {{limitations}}

## Metadata

- description: {{description}}
- language: {{language}}
- words: {{words}}
- image: {{image}}
- favicon: {{favicon}}

## Selection

{{selection}}

## Highlights

{{highlights}}

## Content

{{content}}

## Structured Fields

- schema article: {{schema:@Article}}
- schema news article: {{schema:@NewsArticle}}
- schema blog posting: {{schema:@BlogPosting}}
- meta description: {{meta:name:description}}
- og title: {{meta:property:og:title}}
- og image: {{meta:property:og:image}}

## Capture Notes

- source mode: {{source_mode}}
- template: Shared/Templates/capture/web-origin.md
- selectors: {{selectors}}
- assets: {{assets}}
- prompt assisted: {{prompt_assisted}}
