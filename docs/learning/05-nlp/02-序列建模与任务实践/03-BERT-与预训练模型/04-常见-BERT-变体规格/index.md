---
article_id: kp-674a2e155aa761a5
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 3
learning_objective: 理解并验证：常见 BERT 变体规格
---

# 常见 BERT 变体规格

> **学习目标**：能够解释「常见 BERT 变体规格」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 核心概念

## 本次只学这一点

| 模型 | 层数 | 隐藏维度 | 注意力头 | 参数量 | 说明 |
|------|------|----------|----------|--------|------|
| `bert-base-uncased` | 12 | 768 | 12 | 110M | 小写英文 |
| `bert-large-uncased` | 24 | 1024 | 16 | 340M | 小写英文 |
| `bert-base-cased` | 12 | 768 | 12 | 110M | 区分大小写 |
| `bert-base-multilingual-uncased` | 12 | 768 | 12 | 110M | 102 种语言 |
| `bert-base-chinese` | 12 | 768 | 12 | 110M | 简体 + 繁体中文（字级） |

出现的其他主流模型：GPT、GPT-2、Transformer-XL、XLNet、XLM、RoBERTa、DistilBERT、ALBERT、T5、XLM-RoBERTa。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「常见 BERT 变体规格」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
