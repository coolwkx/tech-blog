---
article_id: kp-9db149843af7b77f
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 1
learning_objective: 理解并验证：Pandas 数据类型
---

# Pandas 数据类型

> **学习目标**：能够解释「Pandas 数据类型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 核心概念

## 本次只学这一点

| Pandas 类型 | 说明 | 对应 Python 类型 |
| --- | --- | --- |
| `object` | 字符串 / 混合类型 | `str` |
| `int64` / `float64` | 整数 / 浮点数 | `int` / `float` |
| `datetime64[ns]` | 日期时间 | `datetime` |
| `timedelta64[ns]` | 时间差 | `timedelta` |
| `category` | 分类类型，**内存更小、运算更快** | 无原生类型 |
| `bool` / `NaN` | 布尔 / 空值 | `bool` / `None` |

查看方式：`s.dtypes`、`df.dtypes`、`df.info`（`Series` 没有 `info`）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Pandas 数据类型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
