---
article_id: kp-0ff2e7fdcdbfbd46
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 1
learning_objective: 理解并验证：三条技术路线
---

# 三条技术路线

> **学习目标**：能够解释「三条技术路线」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 核心概念

## 本次只学这一点

现在主流的预训练语言模型基本都是基于 Transformer 迭代而来，按用了 Transformer 的哪一部分来划分：

| 路线 | 结构 | 代表模型 | 语言模型方向 | 擅长 |
|------|------|----------|-------------|------|
| Encoder-Only | 只用编码器 | BERT、RoBERTa、ALBERT、MacBERT | 双向（同时看左右上下文） | 理解类任务：分类、NER、抽取式问答 |
| Decoder-Only | 只用解码器 | GPT、GPT-2、GPT-3 | 单向（只看左侧上下文） | 生成类任务：续写、对话、代码生成 |
| Encoder-Decoder | 完整 Transformer | T5、BART | 编码双向 + 解码单向 | 序列到序列：翻译、摘要、生成式问答 |

一句话判断路线：**看它擅长理解还是生成**。理解类任务用 Encoder-Only，生成类任务用 Decoder-Only，输入输出都是序列且不等长用 Encoder-Decoder。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三条技术路线」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
