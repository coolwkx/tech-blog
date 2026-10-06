---
article_id: kp-ed3654ffcd17f67a
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 7
learning_objective: 理解并验证：反解隐式奖励（implicit reward）
---

# 反解隐式奖励（implicit reward）

> **学习目标**：能够解释「反解隐式奖励（implicit reward）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

把 $Z(x)$ 的表达式代入闭式解并取对数：

$$\beta\log\frac{\pi^*(y\mid x)}{\pi_{\text{ref}}(y\mid x)}=r(x,y)-\beta\log Z(x)$$

于是奖励可以被表示为

$$r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\text{ref}}(y\mid x)}+\beta\log Z(x)$$

**因为 $Z(x)$ 只依赖 $x$，它对同一个 prompt 下的两条回答是同一个常数。** 定义隐式奖励（implicit reward）

$$\hat r_\theta(x,y)\triangleq \beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\text{ref}}(y\mid x)}$$

即：**我们不再训练一个奖励模型，而是把「策略相对参考模型的对数比」本身当作奖励**。这句话是整篇文档的枢纽。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「反解隐式奖励（implicit reward）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
