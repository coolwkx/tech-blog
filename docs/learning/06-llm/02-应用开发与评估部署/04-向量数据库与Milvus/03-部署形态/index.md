---
article_id: kp-33569679909ecc61
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-d0c337577532
learning_sourceId: d0c337577532
learning_order: 2
learning_objective: 理解并验证：部署形态
---

# 部署形态

> **学习目标**：能够解释「部署形态」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础、embedding 与余弦相似度的直觉、关系型数据库基本概念（库/表/行/列/主键）。
>
> **所属主题**：-向量数据库与Milvus · 核心概念

## 本次只学这一点

| 形态 | 连接方式 | 适用场景 |
|---|---|---|
| Milvus Lite | `MilvusClient(uri="milvus_demo.db")` | 本地开发、单机小数据量（随 `pymilvus` 一起安装） |
| Standalone | `MilvusClient(uri="http://localhost:19530")` | 单机服务，需先启动 Milvus 后台服务 |
| 分布式（Docker/K8s） | 连接集群地址 | 生产环境大规模数据 |

**关键区分**：`uri` 是**文件路径**则代表本地数据库文件；`uri` 是**链接地址**则代表 Milvus 服务，
需要先开启 Milvus 后台服务。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「部署形态」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)
