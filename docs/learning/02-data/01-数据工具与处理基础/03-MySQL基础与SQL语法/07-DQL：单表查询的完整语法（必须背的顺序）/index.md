---
article_id: kp-91d9818960d397fb
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-4da3eec20eac
learning_sourceId: 4da3eec20eac
learning_order: 6
learning_objective: 理解并验证：DQL：单表查询的完整语法（必须背的顺序）
---

# DQL：单表查询的完整语法（必须背的顺序）

> **学习目标**：能够解释「DQL：单表查询的完整语法（必须背的顺序）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
>
> **所属主题**：-MySQL基础与SQL语法 · 核心概念

## 本次只学这一点

```sql
select [distinct] 列1 as 别名, 列2, ...
from 表名
where 组前筛选
group by 分组字段
having 组后筛选
order by 排序字段 [asc | desc]
limit 起始索引, 数据条数;
```

| 子句 | 作用 | 关键点 |
| --- | --- | --- |
| `select` | 选列、起别名、算表达式 | `as` 可省略；`distinct` 去重 |
| `from` | 指定表 | 表也可起别名 |
| `where` | **组前**筛选 | 分组前过滤行；**不能跟聚合函数** |
| `group by` | 分组 | 查询列**只能出现分组字段和聚合函数** |
| `having` | **组后**筛选 | 分组后过滤组；**可以跟聚合函数** |
| `order by` | 排序 | 默认 `asc` 升序，可多字段排序 |
| `limit` | 分页 | `limit 起始索引, 条数`，索引从 0 开始 |

**条件查询速查**

| 场景 | 写法 | 示例 |
| --- | --- | --- |
| 比较 | `=`, `!=`, `<>`, `>`, `>=`, `<`, `<=` | `where price > 60` |
| 逻辑 | `and`, `or`, `not` | `where price >= 200 and price <= 800` |
| 连续区间 | `between 值1 and 值2` | `where price between 200 and 800`（**包左包右**） |
| 固定值集合 | `in (值1, 值2)` | `where price in (200, 800)` |
| 模糊匹配 | `like`：`_` 任意 1 字符，`%` 任意多字符（可为 0） | `where pname like '香%'`、`like '_想%'` |
| 判空 | `is null` / `is not null` | `where category_id is null` |

**聚合函数**（多进一出）：`count` 统计个数（`count(列)` 只统计**非空值**）、`sum` 求和、`max`/`min` 最大最小、`avg` 平均值（分母是非空值个数）。

**分页参数计算公式**

| 参数 | 公式 |
| --- | --- |
| 数据总条数 | `select count(*) from 表;` |
| 第 n 页的起始索引 | `(n - 1) * 每页条数` |
| 总页数 | `(总条数 + 每页条数 - 1) // 每页条数`（向上取整） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「DQL：单表查询的完整语法（必须背的顺序）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)
