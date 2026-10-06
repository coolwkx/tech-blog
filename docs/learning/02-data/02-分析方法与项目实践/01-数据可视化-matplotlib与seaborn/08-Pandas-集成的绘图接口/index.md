---
article_id: kp-074f0019cbf7a079
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 7
learning_objective: 理解并验证：Pandas 集成的绘图接口
---

# Pandas 集成的绘图接口

> **学习目标**：能够解释「Pandas 集成的绘图接口」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 核心概念

## 本次只学这一点

`Series`/`DataFrame` 自带 `.plot`（对 Matplotlib 的封装，默认折线图）：`s.plot` 折线、`s.plot(kind='bar')` / `'barh'` 柱状/横向柱状、`s.plot(kind='pie')` 饼图、`s.plot(kind='hist')` 直方图、`s.plot(legend=True)` 带图例、`pro.plot(kind='bar', stacked=True)` 堆叠柱状图（看比例构成）。注意在脚本里 `.plot` 之后仍需 `plt.show`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Pandas 集成的绘图接口」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
