---
article_id: kp-7b887c66d1dfb158
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-4da3eec20eac
learning_sourceId: 4da3eec20eac
learning_order: 5
learning_objective: 理解并验证：DML：增、删、改
---

# DML：增、删、改

> **学习目标**：能够解释「DML：增、删、改」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
>
> **所属主题**：-MySQL基础与SQL语法 · 核心概念

## 本次只学这一点

| 操作 | 语法 | 说明 |
| --- | --- | --- |
| 增 | `insert into 表名(列1,列2) values(值1,值2);` | 列与值的**个数、类型、顺序必须一致** |
| 增 | `insert into 表名 values(值1,...);` | 省略列名 = 全列名，必须给全 |
| 增 | `insert into 表名 values(null, 值2, ...);` | 主键自增列写 `null`，由数据库分配 |
| 增 | `insert into 表名 values(...),(...),(...);` | 一次插入多行 |
| 改 | `update 表名 set 列1=值1 where 条件;` | **不加 where 会改全表** |
| 删 | `delete from 表名 where 条件;` | **不加 where 会删全表** |

| 维度 | `delete from 表名` | `truncate table 表名` |
| --- | --- | --- |
| 语句类别 | DML | DDL |
| 事务回滚 | 可以 | 一般不可以 |
| 删除范围 | 可带 where 删部分，也可删全部 | 只能整表清空 |
| 自增 id | **不重置** | **重置** |
| 本质 | 逐行删除记录 | 摧毁表再重建同结构的空表 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「DML：增、删、改」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)
