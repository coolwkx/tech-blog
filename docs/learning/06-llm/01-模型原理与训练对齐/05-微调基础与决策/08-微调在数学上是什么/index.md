---
article_id: kp-cdcdc43e5e99ce55
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-9bc2a0f8b073
learning_sourceId: 9bc2a0f8b073
learning_order: 7
learning_objective: 理解并验证：微调在数学上是什么
---

# 微调在数学上是什么

> **学习目标**：能够解释「微调在数学上是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制；预训练语言模型的 MLM / CLM 目标；LoRA 的公式（见《03-LoRA原理与工程实践》）；基本的 PyTorch 训练循环概念。
>
> **所属主题**：微调基础与决策 · 关键机制

## 本次只学这一点

预训练学到的是一个通用的条件分布 $p_{\theta_0}(y \mid x)$。下游微调做的事情是：在给定下游数据 $\mathcal{D}=\{(x^{(i)}, y^{(i)})\}_{i=1}^{N}$ 上，寻找参数 $\theta$，使得

$$
\theta^\star=\arg\min_{\theta}\ \mathbb{E}_{(x,y)\sim\mathcal{D}}\left[-\log p_{\theta}(y\mid x)\right]
$$

并且从 $\theta_0$ 出发做**局部**搜索，即 $\theta = \theta_0 + \Delta\theta$，且 $\|\Delta\theta\|$ 被学习率与训练步数隐式约束得很小。

这一条式子解释了微调的所有行为：**它只在你给的数据分布上抬高目标序列的概率，并顺带压低其他序列的概率**。压低的部分就是"遗忘"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「微调在数学上是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)
