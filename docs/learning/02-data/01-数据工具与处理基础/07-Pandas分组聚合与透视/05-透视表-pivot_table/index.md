---
article_id: kp-ad462cc463696461
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-7b8856bc8b6a
learning_sourceId: 7b8856bc8b6a
learning_order: 4
learning_objective: 理解并验证：透视表 pivot_table
---

# 透视表 pivot_table

> **学习目标**：能够解释「透视表 pivot_table」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-Pandas数据清洗](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) 的聚合函数与 `np.where`。
>
> **所属主题**：-Pandas分组聚合与透视 · 核心概念

## 本次只学这一点

把原 DataFrame 的列**分别作为行索引和列索引**，再对指定列应用聚合函数。

```python
df.pivot_table(values=None, index=None, columns=None, aggfunc='mean',
fill_value=None, margins=False)
```

| 参数 | 作用 |
| --- | --- |
| `index` / `columns` | 行方向键 / 列方向键（把该列不同取值展开成多列） |
| `values` / `aggfunc` | 要聚合的数值列 / 聚合函数（默认 `'mean'`，可传列表或字典） |
| `fill_value` | 填补缺失的交叉格 |
| `margins=True` | 增加总计行列 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「透视表 pivot_table」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)
