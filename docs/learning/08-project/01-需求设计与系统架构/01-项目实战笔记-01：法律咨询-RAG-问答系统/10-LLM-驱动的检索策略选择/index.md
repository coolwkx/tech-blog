---
article_id: kp-2fb6ebf574b42656
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 10
learning_objective: 理解并验证：LLM 驱动的检索策略选择
---

# LLM 驱动的检索策略选择

> **学习目标**：能够解释「LLM 驱动的检索策略选择」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```text
class StrategySelector:
 def select_strategy(self, query):
 # 提示词里给出四种策略的"描述 + 适用场景 + 正例"，并要求"直接返回策略名称"
 try:
 completion = self.client.chat.completions.create(
 model=conf.LLM_MODEL,
 messages=[{"role": "system", "content": "你是一个有用的助手。"},
 {"role": "user", "content": self.strategy_prompt.format(query=query)}],
 temperature=0.1, # 只要分类结果，不要创造性
 )
 return completion.choices[0].message.content or "直接检索"
 except Exception as e:
 logger.error(f"DashScope API 调用失败: {e}")
 return "直接检索" # 失败降级到最稳的策略
```

四种策略与 RAG 核心调度：

```python
def retrieve_and_merge(self, query, source_filter=None, strategy=None):
    strategy = strategy or self.strategy_selector.select_strategy(query)
    if strategy == "回溯问题检索":
        docs = self._retrieve_with_backtracking(query) # 化简后再检索
    elif strategy == "子查询检索":
        docs = self._retrieve_with_subqueries(query) # 拆解 + 各自检索 + 按内容去重
    elif strategy == "假设问题检索":
        docs = self._retrieve_with_hyde(query) # 生成假设答案再检索
    else:
        docs = self.vector_store.hybrid_search_with_rerank(
        query, k=conf.RETRIEVAL_K, source_filter=source_filter)
        return docs[:conf.CANDIDATE_M]

    def generate_answer(self, query, source_filter=None):
        if self.query_classifier.predict_category(query) == "通用知识":
            return self.llm(self.rag_prompt.format(context="", question=query,
        phone=conf.CUSTOMER_SERVICE_PHONE))
        docs = self.retrieve_and_merge(query, source_filter)
        context = "\n\n".join(d.page_content for d in docs) if docs else ""
        return self.llm(self.rag_prompt.format(context=context, question=query,
    phone=conf.CUSTOMER_SERVICE_PHONE))
```

子查询去重那一行曾被写错成基于对象地址去重，正确写法是基于内容：

```python
unique_docs = list({doc.page_content: doc for doc in all_docs}.values())
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LLM 驱动的检索策略选择」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
