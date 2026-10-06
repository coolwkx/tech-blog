---
article_id: kp-d1abfe28835c17df
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-d0c337577532
learning_sourceId: d0c337577532
learning_order: 1
learning_objective: 理解并验证：Milvus 与关系型数据库的概念映射
---

# Milvus 与关系型数据库的概念映射

> **学习目标**：能够解释「Milvus 与关系型数据库的概念映射」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
>
> **所属主题**：-向量数据库与Milvus · 核心概念

## 本次只学这一点

| Milvus | 关系数据库 | 描述 |
|---|---|---|
| Collection | 表（Table） | 集合，相当于关系数据库中的表，用于组织数据 |
| Field | 列（Column） | 字段，Field Schema 相当于表中的列 |
| Entity | 行（Row） | 实体，Collection 中共享同一 Schema 的数据记录 |
| Primary Key | 主键 | 在 Field Schema 中标记 `is_primary` |
| Partition | （无直接对应） | 分区，用于把数据切成子集以加速检索 |
| Database | 数据库 | 一个 Milvus 集群最多支持 **64 个数据库**，可为用户分配权限管理集合 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Milvus 与关系型数据库的概念映射」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)
