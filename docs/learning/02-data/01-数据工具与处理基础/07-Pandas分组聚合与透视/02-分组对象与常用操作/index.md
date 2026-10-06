---
article_id: kp-da29a00bd941ca8c
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 1
learning_objective: 理解并验证：分组对象与常用操作
---

# 分组对象与常用操作

> **学习目标**：能够解释「分组对象与常用操作」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 核心概念

## 本次只学这一点

| 操作 | API | 说明 |
| --- | --- | --- |
| 按一列分组 | `df.groupby('列')` | 返回 `DataFrameGroupBy`，**惰性求值**，不立即计算 |
| 按多列分组 | `df.groupby(['列1','列2'])` | 结果以 MultiIndex 组织 |
| 只取某列 | `df.groupby('列')['目标列']` | 返回 `SeriesGroupBy`，只对该列计算 |
| 组内第一条/最后一条 | `gb.first` / `gb.last` | 取每组第一行、最后一行 |
| 取指定组 | `gb.get_group('组名')` / `gb.get_group(('A','B'))` | 多字段分组时传元组 |
| 分组聚合 | `gb.agg(...)` / `gb.sum` / `gb.mean` | 见 1.3 |
| 分组过滤 | `gb.filter(lambda s: 条件)` | **保留满足条件的整组行**，行数不一定变 |
| 分组转换 | `gb.transform(f)` | 返回**与原表等长**的结果，常用于组内填充/标准化 |
| 分组应用 | `gb.apply(f)` | 最通用可返回任意形状，但**最慢** |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分组对象与常用操作」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
