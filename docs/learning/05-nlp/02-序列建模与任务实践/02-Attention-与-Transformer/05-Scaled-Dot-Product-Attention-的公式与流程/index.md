---
article_id: kp-42834ddedcad7957
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 4
learning_objective: 理解并验证：Scaled Dot-Product Attention 的公式与流程
---

# Scaled Dot-Product Attention 的公式与流程

> **学习目标**：能够解释「Scaled Dot-Product Attention 的公式与流程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 方法细节

## 本次只学这一点

$$
\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

流程（对应 attention 函数的五步）：

1. 求 $d_k$：`d_k = query.size[-1]`，即每个 head 的特征维度。
2. 打分：`scores = matmul(query, key.transpose(-2,-1)) / sqrt(d_k)`，形状 $[B,h,L,L]$。
3. 掩码：`scores = scores.masked_fill(mask == 0, -1e9)`。
4. 归一化：`p_attn = softmax(scores, dim=-1)`。
5. 加权求和：`matmul(p_attn, value)`，形状回到 $[B,h,L,d_k]$。

符号含义：$Q$ 是当前查询表示（$L_q\times d_k$），$K$ 是被查询的键（$L_k\times d_k$），$V$ 是被聚合的值（$L_k\times d_v$）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Scaled Dot-Product Attention 的公式与流程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
