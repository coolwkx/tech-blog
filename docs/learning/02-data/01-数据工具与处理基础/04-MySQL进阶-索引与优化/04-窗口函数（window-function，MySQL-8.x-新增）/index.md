---
article_id: kp-e3833e79fdf1256f
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-f122af99c7af
learning_sourceId: f122af99c7af
learning_order: 3
learning_objective: 理解并验证：窗口函数（window function，MySQL 8.x 新增）
---

# 窗口函数（window function，MySQL 8.x 新增）

> **学习目标**：能够解释「窗口函数（window function，MySQL 8.x 新增）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-MySQL基础与SQL语法](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
>
> **所属主题**：-MySQL进阶-索引与优化 · 核心概念

## 本次只学这一点

用于对**局部范围（窗口）**内的数据做操作，**不改变行数**——"给表新增 1 列"。

```sql
函数 over(partition by 分组字段 order by 排序字段)
```

| 类别 | 函数 | 说明 |
| --- | --- | --- |
| 排序类 | `row_number` | 纯行号，与数值无关，从 1 连续递增 |
| 排序类 | `rank` | 稀疏排名，并列同名次但**跳号** |
| 排序类 | `dense_rank` | 密集排名，并列同名次且**不跳号** |
| 排序类 | `ntile(n)` | 组内平均分 n 桶，常用于数据抽样 |
| 聚合类 | `count/sum/avg/max/min` | 配 `over` 得"组内总计"，可再算占比 |
| 其他类 | `lag(字段,n)` / `lead(字段,n)` | 取组内当前行的前 n / 后 n 行 |
| 其他类 | `first_value` / `last_value` | 组内第一行 / 最后一行 |

数据 `100, 90, 90, 60` 三个排名函数的差异：

| 数据 | `row_number` | `rank` | `dense_rank` |
| --- | --- | --- | --- |
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 60 | 4 | 4 | 3 |

两条最容易踩的规则：`over` 里**不写** `partition by` → 统计**全表**，写了 → 统计**组内**；**不写** `order by` → 统计**组内所有行**，写了 → 统计**组内第一行到当前行**（累计语义）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「窗口函数（window function，MySQL 8.x 新增）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)
