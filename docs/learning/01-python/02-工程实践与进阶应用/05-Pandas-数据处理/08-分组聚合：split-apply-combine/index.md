---
article_id: kp-6d6cc8cbe8b0c8d5
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 7
learning_objective: 理解并验证：分组聚合：split-apply-combine
---

# 分组聚合：split-apply-combine

> **学习目标**：能够解释「分组聚合：split-apply-combine」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

```python
df.groupby(["city", "channel"]).agg({"revenue": "mean", "unit_cost": "sum"})
```
三阶段：**拆分**（按键分组）→ **应用**（每组做计算）→ **合并**（拼回结果表）。

| 方法 | 作用 | 返回形状 |
| --- | --- | --- |
| `gb.sum` / `.mean` / `.count` | 常用聚合 | 每组一行 |
| `gb.agg({列: 函数})` | 不同列用不同函数 | 每组一行 |
| `gb.agg(["sum", "mean"])` | 同列多函数 | 多层列索引 |
| `gb.first` / `.last` | 每组首/末行 | 每组一行 |
| `gb.get_group("上海")` | 取某一组的原始数据 | 原始行数 |
| `gb.filter(lambda x: 条件)` | **按组筛选，返回原始明细行** | 满足条件的全部分组 |
| `gb.transform("mean")` | **返回与原表等长**的结果，用于新增列 | 与输入等长 |
| `gb.apply(func)` | 最灵活，逐组传入 DataFrame | 视返回值而定 |
```python
# filter：保留"组均值 > 200"的所有原始行（等价于 SQL 的 having 子查询）
df.groupby("city").filter(lambda x: x["revenue"].mean > 200)

# transform：把组均值当作新列加回原表（做组内占比、组内中心化）
df["city_mean"] = df.groupby("city")["revenue"].transform("mean")
df["share"] = df["revenue"] / df.groupby("city")["revenue"].transform("sum")
```
**`agg` / `transform` / `apply` 的区别**（最常考）：

| 方法 | 输入 | 输出 | 典型用途 |
| --- | --- | --- | --- |
| `agg` | 每列一个 Series | **每组一行** | 汇总统计 |
| `transform` | 每列一个 Series | **与原表等长** | 新增派生列 |
| `apply` | 每组一个 DataFrame/Series | 任意 | 复杂自定义逻辑 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分组聚合：split-apply-combine」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
