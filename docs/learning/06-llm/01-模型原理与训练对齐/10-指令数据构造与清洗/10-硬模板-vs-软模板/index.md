---
article_id: kp-3df384fcbfb999fc
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 9
learning_objective: 理解并验证：硬模板 vs 软模板
---

# 硬模板 vs 软模板

> **学习目标**：能够解释「硬模板 vs 软模板」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · P-Tuning 详解：可学习软模板

## 本次只学这一点

P-Tuning 出自论文《GPT Understands, Too》。它要解决的是 PET 最疼的两点：**模板靠人写**、**离散词表限制了模板的表达能力**。

| 维度 | 硬模板（Hard / Discrete Prompt） | 软模板（Soft / Continuous Prompt） |
|---|---|---|
| 模板形态 | 真实自然语言字符串，如 `这是一条[MASK]评论：` | 一组无实义的向量，如 `[unused1] [unused2] ...` |
| 是否更新 | 固定不动 | **可训练**，随梯度更新 |
| 初始化 | 无需初始化 | 随机初始化或从真实词的 embedding 初始化 |
| 表达能力 | 受词表限制，只能取「最接近」的那个词 | 连续空间，可以表达词表里不存在的语义 |
| 稳定性 | 换一个词可能差 20 个点 | 稳定，但需要更多训练步收敛 |
| 人工成本 | 高，需要领域先验 | 低，只需指定伪 token 的个数与位置 |

P-Tuning 的模板形式可以写成：

```
T = [x] [v1] [v2] ... [vn] [MASK]
```

其中 `[v1]...[vn]` 就是伪 token（Pseudo Token）。它们的 id 在词表里真实存在（通常借用 `[unused1] ~ [unusedN]` 这类预留位），但**它们代表什么词并不重要，重要的是它们对应的 embedding 会被训练**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「硬模板 vs 软模板」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
