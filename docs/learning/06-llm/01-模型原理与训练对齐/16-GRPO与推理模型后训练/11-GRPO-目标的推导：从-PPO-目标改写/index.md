---
article_id: kp-fdcdc37a17036a28
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-d7276d2e491b
learning_sourceId: d7276d2e491b
learning_order: 10
learning_objective: 理解并验证：GRPO 目标的推导：从 PPO 目标改写
---

# GRPO 目标的推导：从 PPO 目标改写

> **学习目标**：能够解释「GRPO 目标的推导：从 PPO 目标改写」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇（PPO 的四个模型、GAE、KL 惩罚）与第 02 篇（奖励模型与 reward hacking）；对「基线为什么不引入偏差」有印象会更顺。
>
> **所属主题**：-GRPO与推理模型后训练 · 数学推导

## 本次只学这一点

**第一步：写出 token 级的裁剪目标（PPO 形式）。**

$$L^{CLIP}(\theta)=\mathbb{E}\left[\frac{1}{\sum_i|y_i|}\sum_{i=1}^{G}\sum_{t=1}^{|y_i|}\min\Big(w_{i,t}A_{i,t},\ \operatorname{clip}(w_{i,t},1\pm\epsilon)A_{i,t}\Big)\right]$$

**第二步：把 $A_{i,t}$ 替换为常数 $A_i$（由 2.1 的第二步）。** 因为 $A_i$ 与 $t$ 无关，可以提取出来，得到按「每个回答等权」还是「按 token 数等权」两种归约方式的差异：

$$\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|y_i|}\sum_{t=1}^{|y_i|}\min\Big(w_{i,t}A_i,\ \operatorname{clip}(w_{i,t},1\pm\epsilon)A_i\Big)$$

**这里先对每个回答内部按 token 平均、再对 $G$ 个回答平均**，这样长回答不会因为 token 多而主导损失。（若改成全局 token 平均，长回答的权重会更大。）

**第三步：加上 KL 正则项。**

$$-\beta_{KL}\,D_{KL}\big(\pi_\theta(\cdot\mid q)\|\pi_{\text{ref}}(\cdot\mid q)\big)$$

得到 1.3 节给出的完整目标。**注意 GRPO 把 KL 放在总损失里而不是逐 token 奖励里**，这省掉了逐位置构造奖励的复杂度，也让 KL 系数的作用更直观。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GRPO 目标的推导：从 PPO 目标改写」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)
