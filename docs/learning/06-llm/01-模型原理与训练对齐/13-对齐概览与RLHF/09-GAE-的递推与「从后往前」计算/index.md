---
article_id: kp-c99d0615fc41e821
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 8
learning_objective: 理解并验证：GAE 的递推与「从后往前」计算
---

# GAE 的递推与「从后往前」计算

> **学习目标**：能够解释「GAE 的递推与「从后往前」计算」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

GAE 的定义式本身就是递推式，所以可以从最后一个位置开始倒推：

$$\underbrace{A_T=\delta_T}_{\text{因为 }A_{T+1}=0}\ \Longrightarrow\ A_{T-1}=\delta_{T-1}+\gamma\lambda A_T\ \Longrightarrow\ \cdots$$

**实际收益（returns）的推导**：

$$\text{returns}_t=A_t+V_t=\delta_t+\gamma\lambda A_{t+1}+V_t=\big(R_t+\gamma V_{t+1}-V_t\big)+\gamma\lambda A_{t+1}+V_t=R_t+\gamma\big(V_{t+1}+\lambda A_{t+1}\big)$$

$$=R_t+\gamma V_{t+1}^{\text{target}}$$

其中 target 就是 Critic 的回归目标。**回推过程只遍历 response 部分。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GAE 的递推与「从后往前」计算」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
