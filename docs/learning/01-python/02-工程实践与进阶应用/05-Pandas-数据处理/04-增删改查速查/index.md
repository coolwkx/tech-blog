---
article_id: kp-436c55fcdc0e112f
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 3
learning_objective: 理解并验证：增删改查速查
---

# 增删改查速查

> **学习目标**：能够解释「增删改查速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 目的 | 方法 | 是否改原数据 |
| --- | --- | --- |
| 新增/覆盖列 | `df["new"] = df["a"] * 2` | ✅ 原地 |
| 新增列（链式友好） | `df.assign(new=df["a"] * 2)` | ❌ 返回新对象 |
| 删除行/列 | `df.drop(index=[...])` / `df.drop(columns=[...])` / `df.drop("col", axis=1)` | ❌ 默认返回新对象 |
| 原地删除 | `del df["col"]` | ✅ |
| 改列名/索引名 | `df.rename(columns={...}, index={...})` | ❌（加 `inplace=True` 则原地） |
| 改索引 | `df.set_index("col")` / `df.reset_index` | ❌ |
| 替换值 | `df.replace({旧: 新})` / `s.replace(old, new)` | ❌ |
| 排序 | `df.sort_values(by, ascending=)` / `df.sort_index` | ❌ |
| 排名 | `df.rank(method="dense")` | ❌ |
| 去重 | `df.drop_duplicates(subset=, keep=)` | ❌ |
| 查前/后 n 行 | `df.head(n)` / `df.tail(n)` | ❌ |
```python
df.sort_values(["open", "high"], ascending=[True, False]) # 多列不同方向
df.rank(ascending=False, method="dense") # 等价 SQL 的 DENSE_RANK
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「增删改查速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
