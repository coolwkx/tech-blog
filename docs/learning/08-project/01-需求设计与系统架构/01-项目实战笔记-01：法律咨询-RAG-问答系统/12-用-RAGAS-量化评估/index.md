---
article_id: kp-cf63e614d29cbcc8
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-e94c0577cb2f
learning_sourceId: e94c0577cb2f
learning_order: 12
learning_objective: 理解并验证：用 RAGAS 量化评估
---

# 用 RAGAS 量化评估

> **学习目标**：能够解释「用 RAGAS 量化评估」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 工程化基础、向量检索原理（Embedding / 余弦相似度 / ANN）、LangChain 的 Document 与 TextSplitter 抽象、FastAPI 基础、MySQL 与 Redis 基本操作。
>
> **所属主题**：项目实战笔记 01：法律咨询 RAG 问答系统 · 核心实现

## 本次只学这一点

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from datasets import Dataset

data = json.load(open("rag_evaluation_dataset.json", encoding="utf-8"))
dataset = Dataset.from_dict({
"question": [d["question"] for d in data],
"answer": [d["answer"] for d in data],
"contexts": [d["context"] for d in data], # 必须是 list
"ground_truth": [d["ground_truth"] for d in data],
})

result = evaluate(dataset=dataset,
metrics=[faithfulness, answer_relevancy, context_relevancy, context_recall],
llm=ChatOpenAI(model="gpt-4", openai_api_key=KEY),
embeddings=OpenAIEmbeddings(openai_api_key=KEY))
pd.DataFrame([result]).to_csv("ragas_evaluation_results.csv", index=False)
```

四个指标的语义要分清：`context_relevancy / context_recall` 诊断**检索**，`faithfulness / answer_relevancy` 诊断**生成**。调检索策略时只盯前两个，调 Prompt 时只盯后两个——否则改完不知道是哪一步变好的。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 RAGAS 量化评估」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/01-问答与RAG系统/01-项目-法律咨询RAG问答系统.md)
