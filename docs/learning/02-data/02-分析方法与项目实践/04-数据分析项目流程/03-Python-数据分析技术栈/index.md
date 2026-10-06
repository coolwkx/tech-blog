---
article_id: kp-ee6f1110872ffdce
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-91025ff85275
learning_sourceId: 91025ff85275
learning_order: 2
learning_objective: 理解并验证：Python 数据分析技术栈
---

# Python 数据分析技术栈

> **学习目标**：能够解释「Python 数据分析技术栈」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：本目录 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) ～ [10-RFM用户价值分析实战](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md) 的全部内容；会安装软件、使用命令行与 Jupyter。
>
> **所属主题**：-数据分析项目流程 · 核心概念

## 本次只学这一点

| 库 / 工具 | 定位 | 对应章节 |
| --- | --- | --- |
| **NumPy** | 高性能数学库，提供 `ndarray`、广播、线性代数、随机数 | [05](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md) |
| **Pandas** | 结构化数据分析工具集，建立在 NumPy 之上；核心是 `Series`/`DataFrame` | [06](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)、[07](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md) |
| **Matplotlib** | 最常用的绘图库，可创建静态、动态、交互式图表 | [08](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md) |
| **Seaborn** | 建立在 Matplotlib 之上，集成 Pandas 数据结构，API 更简洁 | [08](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)（这里仅点名） |
| **scikit-learn** | 基于 Python 的机器学习工具，建立在 NumPy/SciPy/Matplotlib 上 | 后续阶段 |
| **Jupyter Notebook** | **不是库**，而是开源 Web 应用，可创建和共享代码、公式、图表与笔记 | 本章 1.5 |
| **MySQL** | 关系型数据库，实际开发中真正存数据的地方 | [03](../../../../../02-data/01-Linux与SQL/03-MySQL基础与SQL语法.md) |
| **PyMySQL / SQLAlchemy** | Python 连接与操作 MySQL 的驱动和 ORM 引擎 | [06](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md) |
| **Pyecharts** | 生成可交互图表（如 3D 柱形图） | [10](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md) |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Python 数据分析技术栈」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)
