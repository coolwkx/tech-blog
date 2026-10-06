---
article_id: kp-51c637f2cc5d6d25
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 11
learning_objective: 理解并验证：手写 TF-IDF（含平滑与 L2 归一化）
---

# 手写 TF-IDF（含平滑与 L2 归一化）

> **学习目标**：能够解释「手写 TF-IDF（含平滑与 L2 归一化）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install numpy
import math
from collections import Counter
import numpy as np

docs = ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 狗 喜欢 打架"]
docs_tokens = [d.split() for d in docs]

# 1) 建立词表
vocab = sorted({w for doc in docs_tokens for w in doc})
word2id = {w: i for i, w in enumerate(vocab)}
N, V = len(docs_tokens), len(vocab)

# 2) 文档频率 DF
df = Counter
for doc in docs_tokens:
    df.update(set(doc))

    # 3) 平滑 IDF: log((1+N)/(1+df)) + 1
    idf = {w: math.log((1 + N) / (1 + df[w])) + 1 for w in vocab}

    # 4) TF-IDF（TF 用对数变体 1+log f）+ L2 归一化
    matrix = np.zeros((N, V))
    for i, doc in enumerate(docs_tokens):
        tf = Counter(doc)
        for w, f in tf.items():
            matrix[i, word2id[w]] = (1 + math.log(f)) * idf[w]
            norm = np.linalg.norm(matrix[i])
            if norm > 0:
                matrix[i] /= norm

                print("词表:", vocab)
                for w in vocab:
                    print(f" IDF({w}) = {idf[w]:.4f}")
                    print("\nTF-IDF 矩阵:\n", np.round(matrix, 4))

                    # 5) 用余弦相似度做检索（归一化后点积即余弦）
                    query = "猫 鱼".split()
                    q = np.zeros(V)
                    for w in query:
                        if w in word2id:
                            q[word2id[w]] = 1.0 * idf[w]
                            q /= np.linalg.norm(q)
                            print("\n与查询的相似度:", np.round(matrix @ q, 4))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写 TF-IDF（含平滑与 L2 归一化）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
