---
article_id: kp-cb0cf1576f153ce7
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 2
learning_objective: 理解并验证：聚合函数与 agg 的四种写法
---

# 聚合函数与 agg 的四种写法

> **学习目标**：能够解释「聚合函数与 agg 的四种写法」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 核心概念

## 本次只学这一点

| 函数 | 含义 | 与 `count` 的差别 |
| --- | --- | --- |
| `count` | 非空值个数 | **不统计 NaN** |
| `size` | 元素个数 | **统计 NaN**（统计的是行数） |
| `sum` / `mean` / `median` | 求和 / 均值 / 中位数 | 中位数不受极值影响 |
| `max` / `min` | 最大 / 最小 | 也可用于日期、字符串 |
| `std` / `var` | 标准差 / 方差 | 方差开根号即标准差 |
| `nunique` | 去重后个数 | 常用来数"有多少个不同客户" |

```python
gb.agg('sum') # ① 所有列同一个函数
gb.agg(['sum', 'mean', 'max']) # ② 所有列多个函数（MultiIndex 列）
gb.agg({'revenue': 'mean', 'unit_cost': 'sum'}) # ③ 不同列不同函数（最常用）
gb.agg(平均销售额=('revenue', 'mean')) # ④ 命名聚合，可自定义结果列名
```

`as_index` 的作用：`df.groupby('city', as_index=False)` 把分组键作为**普通列**返回，等价于 `groupby(...).reset_index`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「聚合函数与 agg 的四种写法」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
