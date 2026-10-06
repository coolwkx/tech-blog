---
article_id: kp-e199240525a8cc59
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 0
learning_objective: 理解并验证：两个核心数据结构
---

# 两个核心数据结构

> **学习目标**：能够解释「两个核心数据结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 核心概念

## 本次只学这一点

Pandas 是最流行的**结构化数据**工具集，用于数据清洗、处理与分析；底层基于 NumPy（快）、有专门的缺失值 API、分组聚合能力强。适用于"数据量大到 Excel 卡顿但仍是单机数据"的场合，以及数据仓库 ETL 中的清洗环节。

| 对象 | 维度 | 组成 | 类比 |
| --- | --- | --- | --- |
| `Series`（s 对象） | 一维 | `values`（`ndarray`）+ `index`（索引标签） | Excel 的**一列** |
| `DataFrame`（df 对象） | 二维 | 行索引 `index`（axis=0）+ 列索引 `columns`（axis=1） | Excel 的**一张表** |

层级关系：`DataFrame` → 多个 `Series` → 每个 `Series` 分"索引列"（索引名、索引值、索引下标）与"数据列"（列名、列值）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两个核心数据结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
