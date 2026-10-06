---
article_id: kp-7d2cbc67afc4825a
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-4da3eec20eac
learning_sourceId: 4da3eec20eac
learning_order: 2
learning_objective: 理解并验证：常用数据类型
---

# 常用数据类型

> **学习目标**：能够解释「常用数据类型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会启动 MySQL（或用提供的虚拟机）、能用 DataGrip 或命令行连上数据库；理解"表 = 行 + 列"。
>
> **所属主题**：-MySQL基础与SQL语法 · 核心概念

## 本次只学这一点

| 类别 | 类型 | 说明 | 选型建议 |
| --- | --- | --- | --- |
| 数值 | `int` | 整数 | id、数量、年龄 |
| 数值 | `float` / `double` | 浮点数，有精度误差 | 一般统计值 |
| 数值 | `decimal(m,n)` | 定点数，精确 | **金额**必须用这个 |
| 字符串 | `varchar(n)` | 不定长，按实际长度占用 | 姓名、地址、编号（最常用） |
| 字符串 | `char(n)` | 定长，不足补空格 | 长度固定的编码，如性别、MD5 |
| 日期 | `date` / `datetime` | 年月日 / 年月日时分秒 | 生日 / 订单时间 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「常用数据类型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md)
