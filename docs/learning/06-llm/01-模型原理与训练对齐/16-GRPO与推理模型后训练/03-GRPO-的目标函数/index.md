---
article_id: kp-ba1f232d60c43965
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-d7276d2e491b
learning_sourceId: d7276d2e491b
learning_order: 2
learning_objective: 理解并验证：GRPO 的目标函数
---

# GRPO 的目标函数

> **学习目标**：能够解释「GRPO 的目标函数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇（PPO 的四个模型、GAE、KL 惩罚）与第 02 篇（奖励模型与 reward hacking）；对「基线为什么不引入偏差」有印象会更顺。
>
> **所属主题**：-GRPO与推理模型后训练 · 核心概念

## 本次只学这一点

$$\mathcal{J}_{GRPO}(\theta)=\mathbb{E}_{q\sim P(Q),\,\{y_i\}_{i=1}^{G}\sim\pi_{\theta_{old}}(\cdot\mid q)}\left[\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|y_i|}\sum_{t=1}^{|y_i|}\min\!\Big(w_{i,t}A_i,\ \operatorname{clip}\big(w_{i,t},1-\epsilon,1+\epsilon\big)A_i\Big)-\beta_{KL}\,D_{KL}\big(\pi_\theta\|\pi_{\text{ref}}\big)\right]$$

其中重要性采样权重

$$w_{i,t}=\frac{\pi_\theta(y_{i,t}\mid q,y_{i,<t})}{\pi_{\theta_{old}}(y_{i,t}\mid q,y_{i,<t})}$$

**逐项对照 PPO，只有两处不同：**

| 项 | PPO | GRPO |
|---|---|---|
| 优势 $A$ | 由 Critic + GAE 逐 token 递推 | 组内归一化得到一个常数，广播到所有 token |
| KL 惩罚的位置 | 混进每个 token 的即时奖励 $R_t$ 里（逐位置） | 单独作为一项加在总损失上（整体） |

> 关于 KL 项的位置：在 PPO 实现中它被写进逐 token 奖励；在 GRPO 中则通常作为独立的正则项一次性计算，并使用一种「恒非负」的近似估计（见 2.4）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GRPO 的目标函数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)
