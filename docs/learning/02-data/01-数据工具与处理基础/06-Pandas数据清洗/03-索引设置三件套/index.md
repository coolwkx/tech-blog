---
article_id: kp-04af0fffb4faac0d
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 2
learning_objective: 理解并验证：索引设置三件套
---

# 索引设置三件套

> **学习目标**：能够解释「索引设置三件套」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 核心概念

## 本次只学这一点

| 方法 | 作用 | 关键参数 |
| --- | --- | --- |
| `df.index = 新列表` | 整体替换行索引 | 必须**等长整体替换**，不能只改其中一个 |
| `df.set_index(keys, drop=True)` | 用某列（或多列）作为新索引 | `drop=True` 该列不再保留为普通列；传列表得 MultiIndex |
| `df.reset_index(drop=False)` | 索引还原为普通列，生成新自增下标 | `drop=True` 则直接丢弃原索引 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「索引设置三件套」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
