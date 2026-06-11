---
title: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity"
source_id: "moe-web-capture"
source_type: "web"
source_language: "en"
retrieved_at: "2026-06-10"
source_url: "https://arxiv.org/abs/2101.03961"
source_description: "arXiv abstract page for the Switch Transformer MoE paper."
content_hash: "ca6d2d11587042e421dd27a955e9b8c4bd6966561bdb350bb2e402757d5b7156"
origin: "Shared/Raw/moe-web-capture/origin.md"
candidate_domains:
  - "gpu-arch-research"
compiled_pages: []
status: captured
artifacts:
  - "Shared/Raw/moe-web-capture/original/source.html"
  - "Shared/Raw/moe-web-capture/extracted/defuddle.md"
  - "Shared/Raw/moe-web-capture/extracted/arxiv-api.xml"
limitations: "MCP wiki search was unavailable due to Confluence 401. Public arXiv abstract and arXiv Atom API metadata were used as substitute sources. PDF body was not downloaded or transcribed."
extraction:
  primary_method: "defuddle"
  methods:
    - name: "defuddle"
      role: "primary-content"
      artifacts:
        - "Shared/Raw/moe-web-capture/extracted/defuddle.md"
    - name: "arxiv-api"
      role: "metadata-supplement"
      artifacts:
        - "Shared/Raw/moe-web-capture/extracted/arxiv-api.xml"
    - name: "manual-cleanup"
      role: "manual-cleanup"
      artifacts: []
  capture_card_format: "web-clipper-like"
  variables:
    - "title"
    - "source"
    - "author"
    - "published"
    - "created"
    - "description"
    - "tags"
    - "content"
  selectors:
    - "arXiv abstract block"
    - "arXiv Atom API metadata entry"
  schema_triggers:
    - "arXiv Atom API"
  filters:
    - "clean article markdown"
    - "dedupe fixed-field metadata"
  content_filters:
    - "dedupe fixed-field metadata"
  fallback:
    search_source: "mcp wiki confluence_search"
    status: "unavailable"
    reason: "Confluence token 401"
    substitute_sources:
      - "https://arxiv.org/abs/2101.03961"
      - "https://export.arxiv.org/api/query?id_list=2101.03961"
  assets: "linked"
  prompt_assisted: false
---

# Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

Golden fixture for a Web-Clipper-like LoreForge capture card and multi-method
manifest lineage.
