---
article_id: kp-3e03aaf8fd0f8c3d
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 5
learning_objective: 理解并验证：crosstab vs pivot_table vs groupby
---

# crosstab vs pivot_table vs groupby

> **学习目标**：能够解释「crosstab vs pivot_table vs groupby」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 核心概念

## 本次只学这一点

| 维度 | `groupby.agg` | `pd.crosstab` | `df.pivot_table` |
| --- | --- | --- | --- |
| 输出形态 | 一维/多级索引汇总表 | **二维**频数表（行×列） | **二维**聚合表（行×列） |
| 聚合对象 | 任意列 | 默认数**频数**；给 `values` 后可聚合 | 必须是**数值列** |
| 默认函数 | 需显式指定 | 计数 | `mean` |
| 适合场景 | 多层分组统计 | 两个分类字段的交叉分布 | 行列两个维度下的指标汇总 |
| 结果等价于 | — | `groupby.size.unstack` | `groupby.agg.unstack` |

一句话选择：**要"每组的指标"用 groupby，要"两个分类字段的交叉分布"用 crosstab，要"行维度 × 列维度下的数值汇总"用 pivot_table。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「crosstab vs pivot_table vs groupby」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
