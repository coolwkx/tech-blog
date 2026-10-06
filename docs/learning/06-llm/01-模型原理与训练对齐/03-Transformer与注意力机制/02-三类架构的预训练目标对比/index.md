---
article_id: kp-7e151115dcf9a38f
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 1
learning_objective: 理解并验证：三类架构的预训练目标对比
---

# 三类架构的预训练目标对比

> **学习目标**：能够解释「三类架构的预训练目标对比」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 核心概念

## 本次只学这一点

| 模型 | 架构 | 预训练目标 | 关键设计 |
|---|---|---|---|
| BERT | Encoder-only | MLM（Masked LM）+ NSP（Next Sentence Prediction） | 双向 Transformer，输入含 Token/Segment/Position 三种 embedding |
| GPT-1 | Decoder-only | 单向语言模型（自回归 next-token prediction） | 12 层 Decoder Block，去掉第二个 encoder-decoder attention 子层 |
| T5 | Encoder-Decoder | 自监督（因果语言建模 + 填空任务） | 把所有 NLP 任务统一为 text-to-text |

> 补充：GPT-1 论文主张「生成式预训练 + 判别式微调」，而 BERT 论文主张「双向预训练 + 特征表示」。
> 结论是 GPT 更擅长 NLG，BERT 更擅长 NLU——这也是两类架构最本质的差异来源。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三类架构的预训练目标对比」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
