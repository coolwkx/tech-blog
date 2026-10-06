---
article_id: kp-6dd22b6ab79947d9
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 5
learning_objective: 理解并验证：出发：带 KL 约束的 RLHF 目标
---

# 出发：带 KL 约束的 RLHF 目标

> **学习目标**：能够解释「出发：带 KL 约束的 RLHF 目标」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

第 01 篇给出的 RLHF 目标（在固定 prompt $x$ 下写开）：

$$\max_{\pi}\ \mathbb{E}_{y\sim\pi(\cdot\mid x)}\Big[r(x,y)\Big]-\beta\, D_{KL}\Big(\pi(\cdot\mid x)\,\big\|\,\pi_{\text{ref}}(\cdot\mid x)\Big)$$

其中 $r$ 是（未知的）真实奖励，$\pi_{\text{ref}}$ 是参考策略（SFT 模型），$\beta>0$ 是 KL 惩罚系数。第一项希望奖励高，第二项希望别离参考太远。注意这里是**反向 KL**（期望在 $\pi$ 下取），它倾向于让 $\pi$ 集中到参考分布中奖励高的模式上——这被称为 mode-seeking，正是 RLHF 想让输出「变好」而不是「变多样」的原因。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「出发：带 KL 约束的 RLHF 目标」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
