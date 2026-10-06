---
article_id: kp-d425864af3be3dfb
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 2
learning_objective: 理解并验证：关键配置项一览（来自 config.ini）
---

# 关键配置项一览（来自 config.ini）

> **学习目标**：能够解释「关键配置项一览（来自 config.ini）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 核心概念

## 本次只学这一点

| 分类 | 配置项 | 默认值 | 作用 |
|---|---|---|---|
| 检索 | `parent_chunk_size` | 1200 | 父块大小 |
| 检索 | `child_chunk_size` | 300 | 子块大小 |
| 检索 | `chunk_overlap` | 50 | 相邻块重叠 |
| 检索 | `retrieval_k` | 5 | 检索返回条数 |
| 检索 | `candidate_m` | 2 | 最终作为上下文的条数 |
| Milvus | `host` / `port` | localhost / 19530 | 向量库地址 |
| Milvus | `database_name` / `collection_name` | / rag_final | 库与集合 |
| LLM | `model` | qwen-plus | 生成模型 |
| LLM | `dashscope_api_key` / `base_url` | — | OpenAI 兼容端点 |
| 应用 | `valid_sources` | `["ai","java","test","ops","bigdata"]` | 有效学科来源（用于过滤） |
| 应用 | `customer_service_phone` | 12345678 | 兜底人工客服电话 |
| 日志 | `log_file` | logs/app.log | 日志路径 |

**读表要点**：`retrieval_k`（召回）与 `candidate_m`（精选）是两个不同阶段的量——
召回阶段宁多勿漏，精选阶段宁精勿滥。这是 RAG 调优最常用的两个旋钮。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键配置项一览（来自 config.ini）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
