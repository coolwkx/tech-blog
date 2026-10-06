---
article_id: kp-d195cbca53cb7f9b
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 2
learning_objective: 理解并验证：核心名词对照
---

# 核心名词对照

> **学习目标**：能够解释「核心名词对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · 核心概念

## 本次只学这一点

| 名词 | 英文 | 含义 |
|---|---|---|
| 模板 / 模式 | Pattern (Template) | 含 `[MASK]` 的短文本，把输入改写成完形填空 |
| 标签词映射 | Verbalizer | 类别 → 标签词（label word）的映射函数 |
| PVP | Pattern-Verbalizer Pair | 模板 + 映射的组合，Prompt-Tuning 的最小工作单元 |
| 子标签 | sub label | 与主标签语义相同、但更「好预测」的词，如 `手机` 的子标签可以是 `手机` 本身 |
| 伪 token | Pseudo Token | 软模板中无语义、仅作为可学习向量的占位符，如 `[unused1]` |
| 提示编码器 | Prompt Encoder | 把伪 token 向量再变换一次的网络（P-Tuning 用 MLP+LSTM） |
| 完形填空 | Cloze Question | 被 `[MASK]` 挖空的句子 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「核心名词对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
