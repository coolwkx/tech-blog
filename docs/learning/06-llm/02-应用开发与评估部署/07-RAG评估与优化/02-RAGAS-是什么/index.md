---
article_id: kp-5abae6b8ad302a2b
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-eeb0dcb17743
learning_sourceId: eeb0dcb17743
learning_order: 1
learning_objective: 理解并验证：RAGAS 是什么
---

# RAGAS 是什么

> **学习目标**：能够解释「RAGAS 是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：RAG 完整链路（见《09-RAG系统构建》）、LLM 调用与 Prompt 设计（见《04-提示词工程》）、embedding 与余弦相似度。
>
> **所属主题**：-RAG评估与优化 · 核心概念

## 本次只学这一点

**RAGAS (Retrieval Augmented Generation Assessment)**，一般称为 **Automated Evaluation of Retrieval Augmented Generation**，
即**检索增强生成的自动评估**。它是一个大模型评测框架，可以评估 RAG 的效果、帮助分析模型输出、了解模型在给定任务上的表现。
（GitHub: `explodinggradients/ragas`）

**最重要的设计取向**：最开始的 RAGAS 在评估数据集时**不必依赖人工标注的标准答案**，而是通过底层的大语言模型（LLM）来评估。
因此只需要一个带问题-答案对的评估数据集（QA 对）即可起步。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「RAGAS 是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)
