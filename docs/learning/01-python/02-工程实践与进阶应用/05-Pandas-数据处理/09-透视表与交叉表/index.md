---
article_id: kp-853239111f998982
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 8
learning_objective: 理解并验证：透视表与交叉表
---

# 透视表与交叉表

> **学习目标**：能够解释「透视表与交叉表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 工具 | 用途 | 核心参数 |
| --- | --- | --- |
| `pd.crosstab(index, columns)` | 频数交叉表（计数） | `normalize=`（按行/列/全部求比例） |
| `df.pivot_table(...)` | 透视表（可聚合、可多值） | `index` `columns` `values` `aggfunc` `fill_value` `margins` |
```python
pd.crosstab(df["city"], df["channel"]) # 计数
df.pivot_table(index="city", columns="gender_group",
values="customer", aggfunc="sum") # 汇总
df.pivot_table(index=["city", "channel"],
values=["revenue", "unit_cost"],
aggfunc={"revenue": "mean", "unit_cost": "sum"}) # 多值多函数
```
> 一句话区分：`crosstab` 是"只数个数"的透视表，`pivot_table` 是"能算任何聚合"的交叉表。`pivot_table` 默认 `aggfunc="mean"`，不指定时求均值 —— 想要计数必须显式写 `aggfunc="count"`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「透视表与交叉表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
