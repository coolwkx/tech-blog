---
article_id: kp-cd841e80ce1902cf
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 4
learning_objective: 理解并验证：Prompt 模板设计：一个类管所有模板
---

# Prompt 模板设计：一个类管所有模板

> **学习目标**：能够解释「Prompt 模板设计：一个类管所有模板」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 关键机制

## 本次只学这一点

`RAGPrompts` 用 `@staticmethod` 集中提供四个模板：

| 模板 | 输入变量 | 作用 |
|---|---|---|
| `rag_prompt` | `context`、`question`、`phone` | 核心回答模板；有上下文就基于上下文答，没有就直接用知识答；**答案来自检索文档时要说明**；无法回答时兜底「信息不足，请联系人工客服，电话：{phone}」 |
| `hyde_prompt` | `query` | 生成假设答案，供 HyDE 策略使用 |
| `subquery_prompt` | `query` | 把复杂查询分解为多个子查询（**每行一个**） |
| `backtracking_prompt` | `query` | 把复杂查询简化为一个更基础的问题 |

三个设计要点值得记住：
① **兜底话术内置在模板里**（带客服电话），避免模型在信息不足时编造答案；
② **要求说明来源**（「如果答案来源于检索到的文档，请在回答中说明」），提升可追溯性；
③ **子查询模板规定「每行一个」**，让输出可直接 `split("\n")` 解析。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Prompt 模板设计：一个类管所有模板」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
