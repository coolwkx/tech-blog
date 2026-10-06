---
article_id: kp-84f315691c2311f4
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 4
learning_objective: 理解并验证：从策略梯度定理到 REINFORCE
---

# 从策略梯度定理到 REINFORCE

> **学习目标**：能够解释「从策略梯度定理到 REINFORCE」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

先把「生成一段回答」当成一条轨迹 $\tau=(a_1,\dots,a_T)$，其中 $a_t$ 是第 $t$ 个 token。我们想最大化期望奖励：

$$J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\left[r(\tau)\right]$$

**第一步：把期望写成求和形式。**

$$J(\theta)=\sum_{\tau} P_\theta(\tau)\, r(\tau),\qquad P_\theta(\tau)=\prod_{t=1}^{T}\pi_\theta(a_t\mid s_t)$$

**第二步：对 $\theta$ 求梯度，注意只有 $P_\theta(\tau)$ 依赖 $\theta$。**

$$\nabla_\theta J(\theta)=\sum_{\tau} \nabla_\theta P_\theta(\tau)\, r(\tau)$$

**第三步：用对数导数技巧（log-derivative trick）。** 因为 $\nabla_\theta \log P_\theta(\tau)=\dfrac{\nabla_\theta P_\theta(\tau)}{P_\theta(\tau)}$，所以 $\nabla_\theta P_\theta(\tau)=P_\theta(\tau)\nabla_\theta\log P_\theta(\tau)$。代回：

$$\nabla_\theta J(\theta)=\sum_\tau P_\theta(\tau)\,\nabla_\theta\log P_\theta(\tau)\,r(\tau)=\mathbb{E}_{\tau\sim\pi_\theta}\left[r(\tau)\,\nabla_\theta\log P_\theta(\tau)\right]$$

**第四步：把轨迹的联合对数概率拆开。** 注意 $P_\theta(\tau)=\prod_t\pi_\theta(a_t\mid s_t)$，取对数后求和：

$$\nabla_\theta\log P_\theta(\tau)=\sum_{t=1}^{T}\nabla_\theta\log\pi_\theta(a_t\mid s_t)$$

于是

$$\boxed{\ \nabla_\theta J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\left[\sum_{t=1}^{T} r(\tau)\,\nabla_\theta\log\pi_\theta(a_t\mid s_t)\right]\ }$$

这就是 REINFORCE。它有一个致命缺陷：**每一条轨迹只有一个最终标量 $r(\tau)$，却要用它去乘 $T$ 个随机变量之和**。$T$ 个随机变量的方差直接相加，梯度方差随句子长度线性甚至更快增长，训练几步 reward 就会崩掉。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从策略梯度定理到 REINFORCE」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
