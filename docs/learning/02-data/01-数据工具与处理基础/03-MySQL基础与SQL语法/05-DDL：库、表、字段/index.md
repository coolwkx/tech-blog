---
article_id: kp-d63b38b3691762e9
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-4da3eec20eac
learning_sourceId: 4da3eec20eac
learning_order: 4
learning_objective: 理解并验证：DDL：库、表、字段
---

# DDL：库、表、字段

> **学习目标**：能够解释「DDL：库、表、字段」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
>
> **所属主题**：-MySQL基础与SQL语法 · 核心概念

## 本次只学这一点

| 对象 | 操作 | 语法 |
| --- | --- | --- |
| 库 | 查看全部 / 创建 | `show databases;` / `create database [if not exists] 库名 charset 'utf8';` |
| 库 | 看码表 / 改码表 | `show create database 库名;` / `alter database 库名 charset 'utf8';` |
| 库 | 删除 / 切换 / 看当前 | `drop database 库名;` / `use 库名;` / `select database;` |
| 表 | 查看全部 / 结构 | `show tables;` / `desc 表名;` |
| 表 | 创建 | `create table [if not exists] 表名(字段 类型 [约束], ...);` |
| 表 | 改表名 / 删除 | `alter table 旧名 rename 新名;`（或 `rename table 旧名 to 新名;`） / `drop table 表名;` |
| 字段 | 新增 | `alter table 表名 add 字段 类型 [约束];` |
| 字段 | 只改类型/约束 | `alter table 表名 modify 字段 新类型 [新约束];` |
| 字段 | 改列名+类型+约束 | `alter table 表名 change 旧字段 新字段 新类型 [新约束];` |
| 字段 | 删除 | `alter table 表名 drop 字段;` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「DDL：库、表、字段」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)
