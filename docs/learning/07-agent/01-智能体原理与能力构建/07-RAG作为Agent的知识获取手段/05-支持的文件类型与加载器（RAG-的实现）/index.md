---
article_id: kp-96d67505bbd5677a
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 4
learning_objective: 理解并验证：支持的文件类型与加载器（RAG 的实现）
---

# 支持的文件类型与加载器（RAG 的实现）

> **学习目标**：能够解释「支持的文件类型与加载器（RAG 的实现）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 核心概念

## 本次只学这一点

```text
document_loaders = {
 ".txt": TextLoader,
 ".pdf": OCRPDFLoader, # 基于 paddleOCR，处理扫描件与表格
 ".docx": OCRDOCLoader,
 ".ppt": OCRPPTLoader,
 ".pptx": OCRPPTLoader,
 ".jpg": OCRIMGLoader,
 ".png": OCRIMGLoader,
 ".md": UnstructuredMarkdownLoader,
}
```

加载时同时注入四条元数据：`source`（学科类别，从目录名推导，如 `ai_data` → `ai`）、`file_path`、`timestamp`（`datetime.now().isoformat()`）、以及后续切分阶段补充的 `parent_id` / `parent_content` / `id`。**元数据是检索过滤与溯源的基础**，例如 `filter_expr = f"source == '{source_filter}'"` 就依赖 `source` 字段实现按学科过滤。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「支持的文件类型与加载器（RAG 的实现）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
