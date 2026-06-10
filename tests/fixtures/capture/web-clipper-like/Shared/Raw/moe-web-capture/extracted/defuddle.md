## Title: Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

Authors: William Fedus, Barret Zoph, Noam Shazeer

[View PDF](https://arxiv.org/pdf/2101.03961)

> Abstract: In deep learning, models typically reuse the same parameters for all inputs. Mixture of Experts (MoE) defies this and instead selects different parameters for each incoming example. The result is a sparsely-activated model -- with outrageous numbers of parameters -- but a constant computational cost. However, despite several notable successes of MoE, widespread adoption has been hindered by complexity, communication costs and training instability -- we address these with the Switch Transformer. We simplify the MoE routing algorithm and design intuitive improved models with reduced communication and computational costs. Our proposed training techniques help wrangle the instabilities and we show large sparse models may be trained, for the first time, with lower precision (bfloat16) formats.

| Subjects: | Machine Learning (cs.LG); Artificial Intelligence (cs.AI) |
| Cite as: | arXiv:2101.03961 [cs.LG] |
