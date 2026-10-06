---
article_id: kp-e029d86c716d99c7
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 0
learning_objective: 理解并验证：从原始 Transformer 到三类 LLM
---

# 从原始 Transformer 到三类 LLM

> **学习目标**：能够解释「从原始 Transformer 到三类 LLM」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 核心概念

## 本次只学这一点

2017 年《Attention Is All You Need》提出原始 Transformer，它同时包含 encoder 与 decoder。基于这一框架，
后续模型按「用了哪一部分」分成三类：

| 类别 | 英文 | 代表模型 | 注意力可见性 | 擅长任务 |
|---|---|---|---|---|
| 自编码模型 | AutoEncoder (AE), encoder-only | BERT | 双向（可见全句） | 自然语言理解 NLU：分类、情感分析、抽取式问答 |
| 自回归模型 | AutoRegressive (AR), decoder-only | GPT 系列、LLaMA、Qwen、ChatGLM | 单向（只能看左侧上文） | 自然语言生成 NLG：摘要、翻译、对话、续写 |
| 序列到序列模型 | Sequence-to-Sequence, encoder-decoder | T5、BART | encoder 双向 + decoder 因果 | 机器翻译、文本到文本的统一转换 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从原始 Transformer 到三类 LLM」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
