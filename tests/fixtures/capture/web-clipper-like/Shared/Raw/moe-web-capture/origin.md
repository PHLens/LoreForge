---
title: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity"
source: "https://arxiv.org/abs/2101.03961"
author: "William Fedus, Barret Zoph, Noam Shazeer"
published: "2021-01-11T16:11:52Z"
created: "2026-06-10"
year: 2021
arxiv: "2101.03961"
tags:
  - "clippings"
  - "moe"
---

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
