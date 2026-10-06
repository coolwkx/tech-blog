---
article_id: kp-06ce9999ebaa4e75
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 6
learning_objective: 理解并验证：数据合并：concat vs merge
---

# 数据合并：concat vs merge

> **学习目标**：能够解释「数据合并：concat vs merge」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 维度 | `pd.concat` | `pd.merge` |
| --- | --- | --- |
| 定位 | **拼接**（stack） | **连接**（join，类似 SQL JOIN） |
| 对象数量 | 可一次拼多个 | **一次只能两个** |
| 对齐依据 | `axis=0` 按**列名**；`axis=1` 按**行索引** | 按**关联键**（`on` / `left_on` / `right_on`） |
| 默认连接方式 | `join="outer"`（并集，缺失填 NaN） | `how="inner"`（交集） |
| 索引处理 | `ignore_index=True` 重置索引 | 结果索引默认重置 |

| `how` | 保留的键 | SQL 对应 |
| --- | --- | --- |
| `inner` | 两边都有的键 | `INNER JOIN` |
| `left` | 左表全部键 + 右表匹配到的 | `LEFT JOIN` |
| `right` | 右表全部键 + 左表匹配到的 | `RIGHT JOIN` |
| `outer` | 两边的键的并集 | `FULL OUTER JOIN` |
```python
pd.concat([left, right], ignore_index=True) # 纵向拼接（行增加）
pd.concat([left, right], axis=1) # 横向拼接（列增加，按行索引对齐）
pd.merge(left, right, how="left", on="key1")
pd.merge(l2, r2, left_on="k1", right_on="k1") # 左右键名不同
pd.merge(l3, r3, on="k", suffixes=("_x", "_y")) # 同名非键列加后缀
```
> **"合并后行数变多了"是正常的**：只要关联键在一侧有重复值，就会产生笛卡尔式的多对多匹配。合并后一定要用 `shape` / `value_counts` 检查行数变化，这是数据管道里最常见的隐性 bug。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据合并：concat vs merge」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
