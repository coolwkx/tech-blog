---
article_id: kp-9faaf48778f44aba
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-d0c337577532
learning_sourceId: d0c337577532
learning_order: 3
learning_objective: 理解并验证：Field Schema 与 Collection Schema 的可配置项
---

# Field Schema 与 Collection Schema 的可配置项

> **学习目标**：能够解释「Field Schema 与 Collection Schema 的可配置项」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
>
> **所属主题**：-向量数据库与Milvus · 关键机制

## 本次只学这一点

**Field Schema（字段的逻辑定义）**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `name` | String（必填） | 要创建的集合中的字段名称 |
| `dtype` | 必填 | 字段的数据类型，如 `INT64`、`VARCHAR`、`FLOAT_VECTOR`、`SPARSE_FLOAT_VECTOR` |
| `is_primary` | Boolean | 是否为主键字段（**一个集合仅支持一个主键字段**） |
| `auto_id` | Boolean | 主键字段必填，是否启用自动 ID |
| `max_length` | Integer | `VARCHAR` 字段允许插入的最大长度，范围 `[1, 65535]` |
| `dim` | Integer | 向量维度，范围 `[1, 32768]` |
| `is_partition_key` | Boolean | 该字段是否为分区键 |
| `description` | String | 字段描述（选填） |

**Collection Schema（集合的逻辑定义）**：

| 属性 | 类型 | 说明 |
|---|---|---|
| `field` | 必填 | 集合中要创建的字段 |
| `description` | String | 集合描述（选填） |
| `partition_key_field` | String | 设计用作分区键的字段名（选填） |
| `enable_dynamic_field` | Boolean | 是否启用动态模式 |

**两个重要限制**：① 一个 Collection **最多支持 4 个向量 Field**；
② 定义 Schema 前必须先定义 Field Schema。

**动态字段（`enable_dynamic_field=True`）**：允许插入未定义的字段，这些字段以 JSON 格式存储在名为
`$meta` 的特殊字段中。注意它只对**创建时开启该选项的集合**生效。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Field Schema 与 Collection Schema 的可配置项」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)
