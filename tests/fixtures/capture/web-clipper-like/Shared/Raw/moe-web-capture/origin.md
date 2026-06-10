---
title: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity"
source_id: "moe-web-capture"
type: source
source_type: web
source_language: "en"
retrieved_at: "2026-06-10"
created: "2026-06-10"
source_url: "https://arxiv.org/abs/2101.03961"
author: "William Fedus, Barret Zoph, Noam Shazeer"
published: "2021-01-11T16:11:52Z"
site: "arXiv"
description: "arXiv abstract page for the Switch Transformer MoE paper."
tags:
  - "raw-capture"
  - "web"
  - "moe"
origin: "Shared/Raw/moe-web-capture/origin.md"
candidate_domains:
  - "gpu-arch-research"
compiled_pages: []
status: captured
capture_card:
  format: web-clipper-like
  source_mode: "article"
  variables:
    - "title"
    - "source"
    - "author"
    - "published"
    - "created"
    - "description"
    - "tags"
    - "content"
---

# Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

> Source: https://arxiv.org/abs/2101.03961
> Author: William Fedus, Barret Zoph, Noam Shazeer
> Published: 2021-01-11T16:11:52Z
> Captured: 2026-06-10

## Description

arXiv abstract page for the Switch Transformer MoE paper.

## Content

Mixture of Experts selects different parameters for each incoming example,
creating a sparsely activated model with many parameters and roughly constant
per-token compute. Switch Transformer simplifies MoE routing and reports more
stable sparse training with lower precision formats.

## Structured Metadata

- site: arXiv
- language: en
- words: 72
- image:
- schema: arXiv Atom API entry; categories=cs.LG, cs.AI; pdf=https://arxiv.org/pdf/2101.03961v3
- selectors: arXiv abstract block; arXiv Atom API metadata entry

## Capture Limits

MCP wiki search was unavailable due Confluence 401. Public arXiv abstract and
arXiv Atom API metadata were used as substitute sources. PDF body was not
downloaded or transcribed.
