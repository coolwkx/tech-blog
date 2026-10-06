---
article_id: kp-a3e1e8323b70eb31
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-0cc0dae06e45
learning_sourceId: 0cc0dae06e45
learning_order: 4
learning_objective: 理解并验证：axis 的语义（NumPy 与 Pandas 的差异）
---

# axis 的语义（NumPy 与 Pandas 的差异）

> **学习目标**：能够解释「axis 的语义（NumPy 与 Pandas 的差异）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`axis`、`np.nan`、聚合函数）；[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（`DataFrame`/`Series`、缺失值）；[08-数据可视化- matplotlib与seaborn](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)（直方图看分布）。
>
> **所属主题**：-统计分析基础 · 核心概念

## 本次只学这一点

| 场景 | NumPy | Pandas |
| --- | --- | --- |
| 沿列统计（每列一个结果，跨行） | `axis=0` | `axis=0`（**默认**） |
| 沿行统计（每行一个结果，跨列） | `axis=1` | `axis=1` |
| 全部元素统计 | 不传 `axis` | 不传 `axis` |

记忆法：**`axis` 指定的是"被塌缩掉的轴"**。`axis=0` 让行维消失 → 结果长度 = 列数；`axis=1` 让列维消失 → 结果长度 = 行数。

Pandas 还支持字符串写法：`axis='rows'` 等价 `axis=0`，`axis='columns'` 等价 `axis=1`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「axis 的语义（NumPy 与 Pandas 的差异）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/09-统计分析基础.md)
