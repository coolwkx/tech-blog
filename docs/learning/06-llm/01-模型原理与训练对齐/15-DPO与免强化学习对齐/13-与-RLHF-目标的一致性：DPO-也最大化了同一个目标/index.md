---
article_id: kp-3b7497cf8e8cb1b3
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 12
learning_objective: 理解并验证：与 RLHF 目标的一致性：DPO 也最大化了同一个目标
---

# 与 RLHF 目标的一致性：DPO 也最大化了同一个目标

> **学习目标**：能够解释「与 RLHF 目标的一致性：DPO 也最大化了同一个目标」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

代回验证一下。把隐式奖励代回 RLHF 的目标：

$$J(\pi_\theta)=\mathbb{E}_{y\sim\pi_\theta}\Big[\hat r_\theta(x,y)\Big]-\beta D_{KL}\big(\pi_\theta\|\pi_{\text{ref}}\big)$$

$$=\mathbb{E}_{y\sim\pi_\theta}\Big[\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]-\beta D_{KL}\big(\pi_\theta\|\pi_{\text{ref}}\big)$$

**注意这两项其实是同一个东西**：第一项就是 $\beta D_{KL}(\pi_\theta\|\pi_{\text{ref}})$，两者相减恒为 0。这不是巧合，而是「用最优解反解出的奖励」所满足的**自洽性条件**——只有在 $\pi_\theta=\pi^*$ 时该式才有意义。这也提醒我们：**DPO 的推导是「在最优解附近做重参数化」，它并不直接优化原始 RL 目标，而是优化一个 surrogate；因此它的理论保证依赖于「最优策略落在策略族内」这个假设。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「与 RLHF 目标的一致性：DPO 也最大化了同一个目标」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
