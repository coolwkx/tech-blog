---
article_id: kp-cb63ac1602070d5e
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-eeb0dcb17743
learning_sourceId: eeb0dcb17743
learning_order: 6
learning_objective: 理解并验证：-RAG评估与优化：可运行示例
---

# -RAG评估与优化：可运行示例

> **学习目标**：能够解释「-RAG评估与优化：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：RAG 完整链路（见《09-RAG系统构建》）、LLM 调用与 Prompt 设计（见《04-提示词工程》）、embedding 与余弦相似度。
>
> **所属主题**：-RAG评估与优化 · 可运行示例

## 本次只学这一点

```python
# 依赖：pip install ragas datasets langchain-openai pandas
import json, os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy, context_recall
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

with open("rag_evaluation_dataset.json", encoding="utf-8") as f:
 data = json.load(f) # [{"question","answer","context":[...],"ground_truth"}, ...]

dataset = Dataset.from_dict({
 "question": [d["question"] for d in data],
 "answer": [d["answer"] for d in data],
 "contexts": [d["context"] for d in data], # 必须是 list，即使只有一条
 "ground_truth": [d["ground_truth"] for d in data],
})

# 可换成 DashScope / 本地 Ollama 的 OpenAI 兼容端点
llm = ChatOpenAI(model="gpt-4", api_key=os.environ["OPENAI_API_KEY"])
embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

result = evaluate(dataset=dataset,
 metrics=[faithfulness, answer_relevancy, context_relevancy, context_recall],
 llm=llm, embeddings=embeddings)
print(result)
pd.DataFrame([result]).to_csv("ragas_evaluation_results.csv", index=False) # 多次运行横向对比
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-RAG评估与优化：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/07-检索增强RAG/10-RAG评估与优化.md)
