---
article_id: kp-4fafadf998855570
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 0
learning_objective: 理解并验证：Series 与 DataFrame
---

# Series 与 DataFrame

> **学习目标**：能够解释「Series 与 DataFrame」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 对象 | 定义 | 关键属性 |
| --- | --- | --- |
| `Series` | 一维带标签数组 = ndarray + Index | `index` `values` `dtype` `name` |
| `DataFrame` | 二维表格 = 共享同一行索引的多个 Series | `index` `columns` `dtypes` `shape` `values` `T` |
| `Index` | 行/列的标签容器，**不可变**，可有名字 | `pd.Index`、`DatetimeIndex`、`MultiIndex` |
```python
s = pd.Series([1, 2, 3], index=["a", "b", "c"])
s["b"] # 按"标签"取 → 2
s.iloc[1] # 按"位置"取 → 2
s[s > 1] # 布尔筛选 → [2, 3]
```
**创建方式**：

| 数据 | Series | DataFrame |
| --- | --- | --- |
| 列表 | `pd.Series([1,2,3])` | `pd.DataFrame([[1,2],[3,4]])` |
| 字典 | `pd.Series({"a":1,"b":2})`（键→索引） | `pd.DataFrame({"a":[1,2],"b":[3,4]})`（键→列名） |
| 元组列表 | `pd.Series(("x","y"))` | `pd.DataFrame([(1,2),(3,4)], columns=["a","b"])` |
| ndarray | `pd.Series(arr, index=[...])` | `pd.DataFrame(arr, columns=[...], index=[...])` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Series 与 DataFrame」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
