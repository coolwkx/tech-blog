---
article_id: kp-be01b4d8cdf2d65f
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 9
learning_objective: 理解并验证：位置编码：从绝对到 RoPE
---

# 位置编码：从绝对到 RoPE

> **学习目标**：能够解释「位置编码：从绝对到 RoPE」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

| 方案 | 代表模型 | 特点 |
|---|---|---|
| 可学习绝对位置编码 | GPT-1/2、BERT | 实现简单，但外推性差，超出训练长度即失效 |
| 相对位置编码 | BLOOM | 建模相对距离，外推性更好 |
| 简化版相对位置编码（标量加到 logits） | T5 | 各层共享位置编码，同层不同头独立学习 |
| 旋转位置编码 RoPE | LLaMA、Qwen、Baichuan、ChatGLM | 对 Q/K 向量按「两两一组」做旋转变换，通过内积天然编码相对位置 |

RoPE 的计算流程：对序列中每个 token 的 embedding 先算出 query 和 key 向量，为每个位置计算对应的旋转位置编码，
再对 query/key 向量的元素**两两一组**应用旋转变换，最后计算 query 与 key 的内积得到 self-attention 结果。
RoPE 具有更好的**外推性**，是目前大模型应用最广的相对位置编码方案之一。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「位置编码：从绝对到 RoPE」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
