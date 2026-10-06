---
article_id: kp-628d9669c3088a2f
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 9
learning_objective: 理解并验证：Critic loss 的推导
---

# Critic loss 的推导

> **学习目标**：能够解释「Critic loss 的推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

Critic 的任务是让预测值 $V_t$ 逼近「实际收益」。最朴素的平方误差是

$$L^{VF}=\mathbb{E}_t\left[\big(V_t-\text{return}_t\big)^2\right]$$

因为 return 里含有旧 Critic 的估计（$A_t$ 与 $V_t$ 都来自采样时刻的模型），而在 `ppo_epochs` 内 $V_t$ 会不停更新，所以同样要用旧值做裁剪：

$$V_t^{clip}=\operatorname{clip}\big(V_t,\ V_t^{old}-\epsilon_v,\ V_t^{old}+\epsilon_v\big)$$

$$L^{Critic}(\phi)=\frac{1}{2}\,\mathbb{E}_t\left[\max\Big(\big(V_t-\text{return}_t\big)^2,\ \big(V_t^{clip}-\text{return}_t\big)^2\Big)\right]$$

**取 max 与 Actor 侧取 min 是对偶的**：Actor 侧是「对提升奖励的幅度设上限」，Critic 侧是「对价值函数变化的幅度设上限」，都为了保证一轮经验能被安全地复用多次。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Critic loss 的推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
