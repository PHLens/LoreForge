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

> Abstract: In deep learning, models typically reuse the same parameters for all
> inputs. Mixture of Experts (MoE) defies this and instead selects different
> parameters for each incoming example. The result is a sparsely-activated
> model -- with outrageous numbers of parameters -- but a constant computational
> cost. However, despite several notable successes of MoE, widespread adoption
> has been hindered by complexity, communication costs and training instability
> -- we address these with the Switch Transformer. We simplify the MoE routing
> algorithm and design intuitive improved models with reduced communication and
> computational costs. Our proposed training techniques help wrangle the
> instabilities and we show large sparse models may be trained, for the first
> time, with lower precision (bfloat16) formats.

## Structured Metadata

- site: arXiv
- language: en
- words: 132
- image:
- schema: arXiv Atom API entry; categories=cs.LG, cs.AI; pdf=https://arxiv.org/pdf/2101.03961v3
- selectors: arXiv abstract block; arXiv Atom API metadata entry

## Capture Limits

MCP wiki search was unavailable due to Confluence 401. Public arXiv abstract and
arXiv Atom API metadata were used as substitute sources. PDF body was not
downloaded or transcribed.
