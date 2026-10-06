---
article_id: kp-f112a8e8eed8fad8
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-f122af99c7af
learning_sourceId: f122af99c7af
learning_order: 0
learning_objective: 理解并验证：表关系与建表原则
---

# 表关系与建表原则

> **学习目标**：能够解释「表关系与建表原则」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-MySQL基础与SQL语法](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) 的 `select` 七段式、聚合函数、`group by`/`having`、主键与外键约束。
>
> **所属主题**：-MySQL进阶-索引与优化 · 核心概念

## 本次只学这一点

| 关系 | 业务举例 | 建表原则 |
| --- | --- | --- |
| 一对多 | 部门—员工、客户—订单、分类—商品 | 在**多的一方**加 1 列作外键，关联"1"的一方的主键 |
| 多对多 | 学生—选修课、订单—商品 | 新建**中间表**，至少 3 列（自身主键 + 两个外键列） |
| 一对一 | 人—身份证号、公司—注册地址 | 直接合并到一张表 |

外键两条铁律：① **外表的外键列不能出现主表主键列里没有的值**；② 外键与主键一样，本质是保证数据的完整性与安全性。

```sql
-- 建表时加外键
create table emp(id int primary key auto_increment, name varchar(10), salary int, dept_id int,
 foreign key(dept_id) references dept(id));
-- 建表后加外键（可自定义约束名）
alter table emp add constraint fk_01 foreign key(dept_id) references dept(id);
-- 删除外键：删的是"约束名"而不是列名，先用 show create table emp; 查真实名字
alter table emp drop foreign key fk_01;
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「表关系与建表原则」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/04-MySQL进阶-索引与优化.md)
