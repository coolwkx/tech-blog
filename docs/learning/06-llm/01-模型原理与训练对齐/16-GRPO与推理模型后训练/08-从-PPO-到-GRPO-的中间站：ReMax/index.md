---
article_id: kp-71e353270838ed22
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-d7276d2e491b
learning_sourceId: d7276d2e491b
learning_order: 7
learning_objective: 理解并验证：从 PPO 到 GRPO 的中间站：ReMax
---

# 从 PPO 到 GRPO 的中间站：ReMax

> **学习目标**：能够解释「从 PPO 到 GRPO 的中间站：ReMax」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇（PPO 的四个模型、GAE、KL 惩罚）与第 02 篇（奖励模型与 reward hacking）；对「基线为什么不引入偏差」有印象会更顺。
>
> **所属主题**：-GRPO与推理模型后训练 · 核心概念

## 本次只学这一点

理解 GRPO 之前值得先看一个更简单的方案。ReMax 丢掉 Critic，改用**当前策略 greedy 解码得到的回答的得分**作为基线：

$$A=r(y_{\text{sample}})-r(y_{\text{greedy}})$$

它的直觉是：SFT 之后的模型对同一个 prompt 的输出方差不会太大，所以 greedy 结果可以作为「这个 prompt 的常规水平」的廉价代理。但与 GRPO 相比，它需要额外一次 greedy 生成（多一遍生成开销），且基线只有单点估计、方差较大。GRPO 用一组采样替代单点，估计更稳，代价是 $G$ 倍的生成本身。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从 PPO 到 GRPO 的中间站：ReMax」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)
