---
article_id: kp-97a70df26d1a5f8f
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 11
learning_objective: 理解并验证：编辑距离、Jaccard、TF-IDF 余弦（纯 Python / numpy）
---

# 编辑距离、Jaccard、TF-IDF 余弦（纯 Python / numpy）

> **学习目标**：能够解释「编辑距离、Jaccard、TF-IDF 余弦（纯 Python / numpy）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install numpy
import numpy as np
from collections import Counter

def edit_distance(a: str, b: str) -> int:
    """Levenshtein 编辑距离，滚动数组优化空间到 O(min(m,n))"""
    if len(a) < len(b):
        a, b = b, a
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, start=1):
            cur = [i] + [0] * len(b)
            for j, cb in enumerate(b, start=1):
                cost = 0 if ca == cb else 1
                cur[j] = min(prev[j] + 1, # 删除
                cur[j - 1] + 1, # 插入
                prev[j - 1] + cost) # 替换
                prev = cur
                return prev[-1]

            def jaccard(a: str, b: str) -> float:
                """按字符集合计算 Jaccard 相似度（中文可换成分词后的词集合）"""
                sa, sb = set(a), set(b)
                return len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0

            def tfidf_cosine(docs):
                """手写 TF-IDF + 余弦相似度矩阵"""
                tokenized = [d.split() for d in docs]
                vocab = sorted({w for d in tokenized for w in d})
                word2id = {w: i for i, w in enumerate(vocab)}
                N, V = len(docs), len(vocab)

                # 平滑 IDF
                df = Counter(w for d in tokenized for w in set(d))
                idf = np.array([np.log((1 + N) / (1 + df[w])) + 1 for w in vocab])

                M = np.zeros((N, V))
                for i, d in enumerate(tokenized):
                    tf = Counter(d)
                    for w, f in tf.items():
                        M[i, word2id[w]] = f * idf[word2id[w]]
                        # L2 归一化后，点积即为余弦相似度
                        n = np.linalg.norm(M[i])
                        if n > 0:
                            M[i] /= n
                            return M @ M.T

                        pairs = [("自然语言处理", "自然语言处理技术"),
                        ("自然语言处理", "计算机视觉"),
                        ("kitten", "sitting")]
                        for a, b in pairs:
                            print(f"{a!r:<12} vs {b!r:<14} 编辑距离={edit_distance(a, b):<3} "
                            f"Jaccard={jaccard(a, b):.3f}")

                            docs = ["自然 语言 处理 技术", "计算机 视觉 技术", "自然 语言 处理 与 人工智能"]
                            sim = tfidf_cosine(docs)
                            print("\nTF-IDF 余弦相似度矩阵:\n", np.round(sim, 4))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「编辑距离、Jaccard、TF-IDF 余弦（纯 Python / numpy）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
