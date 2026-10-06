---
article_id: kp-f4735ddc4d1c953d
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 2
learning_objective: 理解并验证：BERT 的宏观结构
---

# BERT 的宏观结构

> **学习目标**：能够解释「BERT 的宏观结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 核心概念

## 本次只学这一点

BERT（Bidirectional Encoder Representations from Transformers）是 2018 年 10 月 Google AI 提出的预训练模型，全称即「来自 Transformer 的双向编码器表示」。它在 SQuAD 1.1 上两个指标全面超越人类，把 GLUE 基准推高到 80.4%（绝对提升 7.6%），是 NLP 发展史上的里程碑。

BERT 宏观上分三个模块：

| 模块 | 内容 | 作用 |
|------|------|------|
| Embedding 模块 | Token + Segment + Position 三种 Embedding **直接相加** | 把 token 变成含位置与句段信息的向量 |
| 双向 Transformer 模块 | 只保留 Transformer 的 Encoder，完全舍弃 Decoder | 提取双向上下文特征 |
| 预微调模块 | 按任务加不同的输出头 | 分类取 `[CLS]`、NER 取每个 token、问答取 span |

三种 Embedding 的细节：

| Embedding | 作用 | 与经典 Transformer 的差异 |
|-----------|------|--------------------------|
| Token Embeddings | 词嵌入，第一个 token 是 `[CLS]` | 中文 BERT 是**字级** |
| Segment Embeddings | 区分句子 A / 句子 B | 服务 NSP 这类句对任务；单句任务全为 0 |
| Position Embeddings | 位置信息 | **不是三角函数固定编码，而是学习出来的** |

> 最后一个差异常被忽略：经典 Transformer 用 sin/cos 公式算位置编码，BERT 把位置编码当成可学习参数。代价是最大长度被固定（512），好处是位置表示更贴合数据。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 的宏观结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
