---
article_id: kp-3e2a13400ef93c2a
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-0cc0dae06e45
learning_sourceId: 0cc0dae06e45
learning_order: 2
learning_objective: 理解并验证：方差与标准差的定义
---

# 方差与标准差的定义

> **学习目标**：能够解释「方差与标准差的定义」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`axis`、`np.nan`、聚合函数）；[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（`DataFrame`/`Series`、缺失值）；[08-数据可视化- matplotlib与seaborn](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)（直方图看分布）。
>
> **所属主题**：-统计分析基础 · 核心概念

## 本次只学这一点

总体方差（分母为 n）：

$$\sigma^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2, \qquad \sigma = \sqrt{\sigma^2}$$

样本方差（分母为 n−1，即 Bessel 校正）：

$$s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$$

| 术语 | 分母 | 谁在用 | 为什么 |
| --- | --- | --- | --- |
| 总体方差 / 标准差 | `n` | NumPy 的 `np.var` / `np.std`（默认 `ddof=0`） | 数据就是全体 |
| 样本方差 / 标准差 | `n-1` | Pandas 的 `s.var` / `s.std`（默认 `ddof=1`） | 用样本估计总体时，除以 n−1 才是**无偏估计** |

> 这是 NumPy 与 Pandas 一个**容易踩的差异**：同一列数据，`np.std(arr)` 与 `pd.Series(arr).std` 的结果**不一样**。要统一，用 `np.std(arr, ddof=1)` 或 `s.std(ddof=0)`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「方差与标准差的定义」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)
