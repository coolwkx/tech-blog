---
article_id: kp-a8431d6372f45068
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-6f07590fb31d
learning_sourceId: 6f07590fb31d
learning_order: 9
learning_objective: 理解并验证：物流行业 RAG 项目：最小可运行版
---

# 物流行业 RAG 项目：最小可运行版

> **学习目标**：能够解释「物流行业 RAG 项目：最小可运行版」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：LangChain 六大组件（见《08-LangChain基础》）、Milvus 与向量检索（见《07-向量数据库与Milvus》）、embedding 与相似度。
>
> **所属主题**：-RAG系统构建 · 关键机制

## 本次只学这一点

第五章的物流项目是一个「去掉所有花活」的最小实现，非常适合作为第一个练手项目：

| 步骤 | 做法 |
|---|---|
| 建库 | `PyMuPDFLoader("物流信息.pdf")` → `RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=20)` → `OllamaEmbeddings(model="mxbai-embed-large")` → `FAISS.from_documents(...)` 并 `save_local("./faiss/wuliu")` |
| 问答 | 加载 FAISS → `similarity_search(question, k=2)` → 拼接 `context` → `PromptTemplate` 组装 → `Ollama(model="qwen2.5:7b").invoke` |
| Web | `streamlit` + `ConversationalRetrievalChain.from_llm(llm=..., retriever=db.as_retriever)` |

它的 Prompt 模板极简但把关键约束写清楚了：

```text
基于以下已知信息，简洁和专业的来回答用户的问题。不允许在答案中添加编造成分。
已知内容: {context}
问题: {question}
```

**「不允许在答案中添加编造成分」这句话是 RAG Prompt 的必备约束**——它把模型从「自由发挥」切换为「依据材料作答」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「物流行业 RAG 项目：最小可运行版」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/09-RAG系统构建.md)
