---
article_id: kp-420fa80777d987b5
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 12
learning_objective: 理解并验证：与 sklearn 对照（验证两者的差异）
---

# 与 sklearn 对照（验证两者的差异）

> **学习目标**：能够解释「与 sklearn 对照（验证两者的差异）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

docs = ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 狗 喜欢 打架"]

vec = TfidfVectorizer(
token_pattern=r"(?u)\b\w+\b", # 中文分词后必须放宽，否则单字被丢弃
smooth_idf=True, # log((1+N)/(1+df)) + 1
sublinear_tf=False, # TF 用原始计数，与上一节手写版不同
norm="l2",
)
X = vec.fit_transform(docs)

print("词表:", vec.get_feature_names_out)
print("IDF :", dict(zip(vec.get_feature_names_out, vec.idf_.round(4))))
print("矩阵:\n", X.toarray.round(4))
print("稀疏结构: data=%d, indices=%d, indptr=%s"
% (X.data.size, X.indices.size, X.indptr))
```

注意手写版与 sklearn 的结果**不可能完全一致**，因为：手写版用了 `1 + log f` 的对数 TF 而 sklearn 默认用原始计数；两者对 IDF 的实现细节也略有出入。要严格对齐，把手写版的 TF 改回原始计数即可。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「与 sklearn 对照（验证两者的差异）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
