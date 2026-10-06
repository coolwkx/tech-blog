---
article_id: kp-6700f4e38bd6895c
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-0cc0dae06e45
learning_sourceId: 0cc0dae06e45
learning_order: 1
learning_objective: 理解并验证：统计量速查表
---

# 统计量速查表

> **学习目标**：能够解释「统计量速查表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`axis`、`np.nan`、聚合函数）；[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（`DataFrame`/`Series`、缺失值）；[08-数据可视化- matplotlib与seaborn](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)（直方图看分布）。
>
> **所属主题**：-统计分析基础 · 核心概念

## 本次只学这一点

| 统计量 | NumPy | Pandas | 含义与要点 |
| --- | --- | --- | --- |
| 个数 | `np.size(a)` | `s.count` / `s.size` | `count` **不计 NaN**；`size` 计所有元素 |
| 求和 | `np.sum(a, axis)` | `s.sum` | — |
| 均值 | `np.mean(a, axis)` | `s.mean` | 对离群值**敏感** |
| 中位数 | `np.median(a, axis)` | `s.median` | 排序后中间的数；偶数个取中间两数平均；对离群值**稳健** |
| 众数 | — | `s.mode` | 出现次数最多的值，可能返回多个 |
| 最大/最小 | `np.max` / `np.min` | `s.max` / `s.min` | 也可用于日期、字符串 |
| 极差 | `np.ptp(a)` | `s.max - s.min` | 最大值减最小值，最粗糙的离散度量 |
| 方差 | `np.var(a, axis)` | `s.var` | 各值与均值之差的**平方和的平均**；值总是非负；单位是原单位的**平方** |
| 标准差 | `np.std(a, axis)` | `s.std` | 方差的算术平方根；**与原数据同量纲**，所以更常用于解释 |
| 最大/最小位置 | `np.argmax` / `np.argmin` | `s.idxmax` / `s.idxmin` | NumPy 返回**下标**，Pandas 返回**索引标签** |
| 分位数 | `np.percentile(a, q)` | `s.quantile(q)` | 如 `q=0.25` 即下四分位数 |
| 绝对值/乘积 | `np.abs` / — | `s.abs` / `s.prod` | — |
| 累计统计 | `np.cumsum` / `np.cumprod` | `s.cumsum` / `s.cummax` / `s.cummin` / `s.cumprod` | 返回与输入等长的序列，"前 1/2/…/n 个的累计结果" |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计量速查表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)
