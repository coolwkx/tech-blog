---
article_id: kp-e60aa04800d7b0a2
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 11
learning_objective: 理解并验证：注意力的稀疏化与 KV Cache
---

# 注意力的稀疏化与 KV Cache

> **学习目标**：能够解释「注意力的稀疏化与 KV Cache」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

**Sparse Attention（GPT-3 引入）**：传统 self-attention（dense attention）每个 token 两两计算，复杂度 $O(n^2)$；
sparse attention 让每个 token 只与部分 token 计算，复杂度 $O(n\log n)$。具体做法是：除相对距离不超过 $k$、
以及相对距离为 $k,2k,3k,\dots$ 的 token 外，其余全部置 0。好处是：① 契合「局部紧密相关、远程稀疏相关」的语言特性；
② 降低注意力层计算复杂度，节约显存与耗时，从而处理更长输入。

**KV Cache**：只存在于自回归 decoder 中（BERT 没有）。生成第 $n+1$ 个 token 时，前面的
$\{x_i^l \mid 1\le i\le n\}$ 与上一次计算完全相同，因此可以复用，避免重复计算 K/V。
实测在 Tesla T4 上生成 1000 个 token，用 KV cache 约 11 秒，不用则约 56 秒。
使用 `transformers` 时可通过 `generate(..., use_cache=True)` 控制。

**MHA / MQA / GQA**：这是减少 KV cache 开销的关键手段。

| 方案 | 结构 | 特点 |
|---|---|---|
| MHA | 每个 query 都有自己的一套 key/value 参数 | 效果最好，但参数量与 KV cache 最大 |
| MQA | 所有 query 共享**一套** key/value | 参数量、显存最省，效果略降 |
| GQA | 把 query 分组，共享 **N 套** key/value | MHA 与 MQA 的折中：保留速度，效果接近 MHA |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「注意力的稀疏化与 KV Cache」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
