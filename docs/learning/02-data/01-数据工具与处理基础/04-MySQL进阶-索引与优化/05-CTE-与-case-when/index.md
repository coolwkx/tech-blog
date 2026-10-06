---
article_id: kp-9b5fcc255c6bc101
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-f122af99c7af
learning_sourceId: f122af99c7af
learning_order: 4
learning_objective: 理解并验证：CTE 与 case when
---

# CTE 与 case when

> **学习目标**：能够解释「CTE 与 case when」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-MySQL基础与SQL语法](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
>
> **所属主题**：-MySQL进阶-索引与优化 · 核心概念

## 本次只学这一点

```sql
with 临时表名1 as (查询语句),
 临时表名2 as (查询语句)
select * from 临时表名1 ...;
```

CTE 把查询结果临时封装成一张表再查询，与"套表"（子查询写在 `from` 里）作用相同，但可读性更好且能链式定义多张临时表。`case when` 相当于 Python 的 `if`：

```sql
case when deptid=10 then '蜀国' when deptid=20 then '魏国' else '灭国' end as dept_name
-- 语法糖：同 1 字段且都是"等于"判断时可简写
case deptid when 10 then '蜀国' when 20 then '魏国' else '灭国' end as dept_name
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CTE 与 case when」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)
