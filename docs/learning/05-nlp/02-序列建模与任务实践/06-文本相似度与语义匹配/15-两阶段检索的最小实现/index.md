---
article_id: kp-5d0ff435f1b02538
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 14
learning_objective: 理解并验证：两阶段检索的最小实现
---

# 两阶段检索的最小实现

> **学习目标**：能够解释「两阶段检索的最小实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install sentence-transformers
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

bi = SentenceTransformer("BAAI/bge-small-zh-v1.5")
cross = CrossEncoder("BAAI/bge-reranker-base")

corpus = [
 "感冒了应该怎么办", "感冒药怎么吃", "今天天气怎么样",
 "发烧的处理方法", "如何预防流感", "什么是自然语言处理",
 "心血管疾病的常见症状", "高血压患者饮食注意",
]
corpus_emb = bi.encode(corpus, normalize_embeddings=True) # 离线预计算

query = "发烧了吃什么药"

# 阶段一：双塔召回 Top-4（毫秒级）
top_k = 4
scores = corpus_emb @ bi.encode(query, normalize_embeddings=True)
recall_idx = np.argsort(-scores)[:top_k]
recalled = [corpus[i] for i in recall_idx]

# 阶段二：Cross-Encoder 精排召回的候选
pairs = [[query, c] for c in recalled]
rerank_scores = cross.predict(pairs)

print("召回阶段（双塔）:")
for i in recall_idx:
 print(f" {scores[i]:.4f} {corpus[i]}")
print("\n精排阶段（Cross-Encoder）:")
for c, s in sorted(zip(recalled, rerank_scores), key=lambda x: -x[1]):
 print(f" {s:+.4f} {c}")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两阶段检索的最小实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
