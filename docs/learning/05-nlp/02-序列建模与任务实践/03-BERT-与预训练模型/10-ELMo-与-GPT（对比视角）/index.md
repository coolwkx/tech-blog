---
article_id: kp-1fb866d27f0e754b
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 9
learning_objective: 理解并验证：ELMo 与 GPT（对比视角）
---

# ELMo 与 GPT（对比视角）

> **学习目标**：能够解释「ELMo 与 GPT（对比视角）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

| 模型 | 结构 | 语言模型 | 特点与局限 |
|------|------|----------|-----------|
| ELMo（2018.3，华盛顿大学） | 双向**双层 LSTM** + 特征融合 | 表面双向，实际是左右两个单向 LSTM 分别提特征后简单拼接 | 根据上下文动态调整词向量，能更好解决多义词；但特征提取器没选用更强大的 Transformer |
| GPT（OpenAI） | Transformer 的 **Decoder** | 单向（Masked Multi-Head Attention，未来信息不可见） | 把 3 层 Decoder Block 改为 2 层（删除 encoder-decoder attention），共 12 个 Block；两阶段：无监督预训练 + 有监督微调 |
| BERT | Transformer 的 **Encoder** | 最彻底的双向 | 同时关注 context before 与 context after |

三者对比的核心结论：**特征提取器不同**（BERT=Encoder，GPT=Decoder，ELMo=双层双向 LSTM），**单向/双向不同**（BERT 真双向，GPT 单向，ELMo 伪双向）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ELMo 与 GPT（对比视角）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
