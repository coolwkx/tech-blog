---
article_id: kp-7ddd52c714bc42fa
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 3
learning_objective: 理解并验证：GPT 系列的演进（架构与训练目标）
---

# GPT 系列的演进（架构与训练目标）

> **学习目标**：能够解释「GPT 系列的演进（架构与训练目标）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 核心概念

## 本次只学这一点

| 模型 | 时间 | 参数规模 | 数据集 | 核心思想 | 关键变化 |
|---|---|---|---|---|---|
| GPT-1 | 2018.06 | 1.17 亿 | BooksCorpus（约 5GB，7400 万句） | 无监督预训练 + 有监督微调 | 12 层 / 12 head / 768 维 |
| GPT-2 | 2019.02 | 最大 15 亿 | WebText（约 800 万篇、40GB） | **zero-shot**：无监督多任务学习 | Pre-LayerNorm、最后一层后加 LN、序列长度 512→1024 |
| GPT-3 | 2020.05 | 最大 1750 亿 | 约 45TB 文本（清洗后 570GB） | **few-shot / in-context learning** | 引入 sparse attention、最大版本 96 层，head size 96，向量维度 12288，文本长度 2048 |
| ChatGPT | 2022.11 | 未公开 | — | 用人类反馈强化学习（RLHF）对齐 | SFT → RM → PPO 三步 |

GPT-3 的数据配比（训练 token 数）：

| 数据集 | tokens | 占比 |
|---|---|---|
| CommonCrawl (filtered) | 4100 亿 | 60% |
| WebText2 | 190 亿 | 22% |
| Books1 | 120 亿 | 8% |
| Books2 | 550 亿 | 8% |
| Wikipedia | 30 亿 | 2% |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GPT 系列的演进（架构与训练目标）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
