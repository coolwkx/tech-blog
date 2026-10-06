---
article_id: kp-67272b9f34402bbf
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 5
learning_objective: 理解并验证：基线与优势函数：降方差且不引入偏差
---

# 基线与优势函数：降方差且不引入偏差

> **学习目标**：能够解释「基线与优势函数：降方差且不引入偏差」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

**引理（基线无偏）**：对任意只依赖状态 $s_t$ 的函数 $b(s_t)$，

$$\mathbb{E}_{a_t\sim\pi_\theta}\left[b(s_t)\nabla_\theta\log\pi_\theta(a_t\mid s_t)\right]=b(s_t)\sum_{a}\pi_\theta(a\mid s_t)\nabla_\theta\log\pi_\theta(a\mid s_t)=b(s_t)\sum_a \nabla_\theta\pi_\theta(a\mid s_t)=b(s_t)\nabla_\theta\underbrace{\sum_a \pi_\theta(a\mid s_t)}_{=1}=0$$

**证明只用到了 $\nabla_\theta\log p=\nabla_\theta p/p$ 与概率之和为 1 这两个事实**。所以减去任意状态相关基线都不改变期望梯度，只改变方差。把「未来收益」的期望提出来，就得到

$$\nabla_\theta J(\theta)=\mathbb{E}\left[\sum_{t}\underbrace{\big(r(\tau)-b(s_t)\big)}_{\text{优势的朴素形式}}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\right]$$

严格的优势函数定义为 $A_t=Q(s_t,a_t)-V(s_t)$，其中

$$V(s_t)=\mathbb{E}\left[\sum_{t'\ge t}\gamma^{t'-t}R_{t'}\ \middle|\ s_t\right],\qquad Q(s_t,a_t)=\mathbb{E}\left[\sum_{t'\ge t}\gamma^{t'-t}R_{t'}\ \middle|\ s_t,a_t\right]$$

**其中 $\gamma$ 是折扣因子**，用于决定未来收益折算到当下的权重。Critic 网络要拟合的就是 $V(s_t)$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「基线与优势函数：降方差且不引入偏差」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
