---
article_id: kp-b0c66b64dd8f1860
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 12
learning_objective: 理解并验证：用 sentence-transformers 做双塔语义相似度
---

# 用 sentence-transformers 做双塔语义相似度

> **学习目标**：能够解释「用 sentence-transformers 做双塔语义相似度」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install sentence-transformers
# 首次运行会联网下载模型；中文可用 'shibing624/text2vec-base-chinese'
# 或 'BAAI/bge-small-zh-v1.5'（检索任务通常需要在 query 前加指令前缀）
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

sentences = [
 "如何治疗感冒",
 "感冒了应该怎么办",
 "今天天气怎么样",
 "感冒药怎么吃",
]

# 注意：这些向量可以离线预计算并缓存，这是双塔的核心优势
embeddings = model.encode(sentences, normalize_embeddings=True) # 归一化！
print("向量形状:", embeddings.shape)

query = "发烧了吃什么药"
q_emb = model.encode(query, normalize_embeddings=True)

# 归一化后，点积等价于余弦相似度
scores = embeddings @ q_emb
for s, score in sorted(zip(sentences, scores), key=lambda x: -x[1]):
 print(f"{score:.4f} {s}")

# sentence-transformers 也提供了封装好的工具函数
print("\nTop-2:", util.semantic_search(q_emb, embeddings, top_k=2))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 sentence-transformers 做双塔语义相似度」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
