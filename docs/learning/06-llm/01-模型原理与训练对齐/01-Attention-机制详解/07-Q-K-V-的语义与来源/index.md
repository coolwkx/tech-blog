---
article_id: kp-0a29a5b2e2c73667
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 6
learning_objective: 理解并验证：Q/K/V 的语义与来源
---

# Q/K/V 的语义与来源

> **学习目标**：能够解释「Q/K/V 的语义与来源」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

$Q = XW_Q,\ K = XW_K,\ V = XW_V$，其中 $X \in \mathbb{R}^{n\times d_{model}}$，三个权重矩阵均为 $d_{model}\times d_{model}$。$W_Q,W_K$ 决定"什么算相关"，定义了一个可学习的**双线性相似度** $x_i^\top W_QW_K^\top x_j$；$W_V$ 决定"被关注后传递什么"。**相关度与传递内容的解耦**正是 Attention 强于"用相似度直接加权原始输入"之处——可以高相关但不传递信息，也可以低相关但传递关键信息。

**"自"注意力**指 $Q,K,V$ 全部来自同一个 $X$，序列自己关注自己；对比 **cross-attention**：$Q$ 来自解码器（或文本），$K,V$ 来自编码器输出（或图像），此时 $n_q \neq n_k$。

| 类型 | Q 来源 | K/V 来源 | scores 形状 | 典型场景 |
| --- | --- | --- | --- | --- |
| self-attention | $X$ | $X$ | $[B,h,n,n]$ | GPT/LLaMA 每一层 |
| cross-attention | 解码器状态 | 编码器输出 | $[B,h,n_q,n_k]$ | 翻译、Stable Diffusion 文本条件 |
| causal self-attention | $X$ | $X$（加掩码） | $[B,h,n,n]$，上三角置 $-\infty$ | 自回归语言模型 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Q/K/V 的语义与来源」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
