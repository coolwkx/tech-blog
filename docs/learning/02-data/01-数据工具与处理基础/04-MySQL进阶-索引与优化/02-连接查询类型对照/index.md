---
article_id: kp-adfe4547ed276e5d
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-f122af99c7af
learning_sourceId: f122af99c7af
learning_order: 1
learning_objective: 理解并验证：连接查询类型对照
---

# 连接查询类型对照

> **学习目标**：能够解释「连接查询类型对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-MySQL基础与SQL语法](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
>
> **所属主题**：-MySQL进阶-索引与优化 · 核心概念

## 本次只学这一点

| 类型 | 写法 | 结果集 | 说明 |
| --- | --- | --- | --- |
| 交叉查询 | `from 表A, 表B` | A 条数 × B 条数 | 笛卡尔积，**一般不用** |
| 显式内连接 | `from A inner join B on 关联条件` | 两表**交集** | `inner` 可省略；推荐显式写法 |
| 隐式内连接 | `from A, B where 关联条件` | 交集 | 老写法，条件混在 where 里可读性差 |
| 左外连接 | `from A left [outer] join B on 条件` | **左表全集** + 交集 | 右表没匹配上为 null；**推荐掌握这一种** |
| 右外连接 | `from A right [outer] join B on 条件` | **右表全集** + 交集 | 交换表序后与左外连接等价 |

> `A left join B` ≡ `B right join A`。日常统一用**左外连接**，把"必须保全数据的主表"放左边，思路最清楚。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「连接查询类型对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)
