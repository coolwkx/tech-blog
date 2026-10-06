---
article_id: kp-f71d433a3b765037
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-f122af99c7af
learning_sourceId: f122af99c7af
learning_order: 5
learning_objective: 理解并验证：延伸补充（本主题展开）
---

# 延伸补充（本主题展开）

> **学习目标**：能够解释「延伸补充（本主题展开）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-MySQL基础与SQL语法](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
>
> **所属主题**：-MySQL进阶-索引与优化 · 可运行示例

## 本次只学这一点

> 只在 `limit 起始索引` 和练习题注释里出现过"索引/优化"字样，**并未系统讲解索引原理**。以下仅作进阶入门。

```sql
show index from emp; -- 查看索引
create index idx_emp_deptid on emp(dept_id); -- 普通索引
create unique index uk_emp_name on emp(name); -- 唯一索引
create index idx_emp_dept_salary on emp(dept_id, salary);-- 复合索引
explain select * from emp where dept_id = 2; -- 执行计划
```

| 概念 | 说明 |
| --- | --- |
| 索引本质 | 排好序的辅助结构（InnoDB 用 **B+ 树**），用空间换查询时间 |
| 聚簇索引 | InnoDB **主键索引即聚簇索引**，叶子节点直接存整行数据，所以主键要短、要自增 |
| 二级索引 | 叶子节点存主键值，查非索引列需**回表** |
| 最左前缀 | 复合索引 `(dept_id, salary)` 可用于 `where dept_id=?` 或两者同时，但**单独 `where salary=?` 用不上** |
| `explain` 关键列 | `type`（`ref` 优于 `index` 优于 `ALL`）、`key`、`rows`、`Extra` |
| 索引失效常见写法 | 索引列上做运算或套函数、前导 `%` 的 `like '%香'`、隐式类型转换、`or` 连接非索引列 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「延伸补充（本主题展开）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)
