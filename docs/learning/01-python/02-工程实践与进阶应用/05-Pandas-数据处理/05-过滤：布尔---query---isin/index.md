---
article_id: kp-1fe7e3859c24f3e7
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 4
learning_objective: 理解并验证：过滤：布尔 / query / isin
---

# 过滤：布尔 / query / isin

> **学习目标**：能够解释「过滤：布尔 / query / isin」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 写法 | 说明 |
| --- | --- |
| `df[df.open > 23]` | 布尔 Series 过滤 |
| `df[(df.a >= 1) & (df.b <= 2)]` | 复合条件必须用 `&` `\|` `~`，**每个条件都要加括号** |
| `df.query("open >= 23 and open <= 24")` | 字符串表达式，可读性最好 |
| `df.query("country in ['中国','美国']")` | `query` 里支持 `in` |
| `df[df.open.isin([23.80, 25.60])]` | 是否属于某个集合 |
| `df.between(23, 24)` | 闭区间判断 |

**常见错误**：用 `and` / `or` / `not` 连接布尔 Series 会抛 `ValueError: The truth value of a Series is ambiguous`。Python 的 `and` 要求结果是单个布尔值，而 Series 是"一串布尔值"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「过滤：布尔 / query / isin」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
