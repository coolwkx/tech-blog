---
article_id: kp-afeec63e217c4159
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 14
learning_objective: 理解并验证：稀疏矩阵与特征裁剪的工程实践
---

# 稀疏矩阵与特征裁剪的工程实践

> **学习目标**：能够解释「稀疏矩阵与特征裁剪的工程实践」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install scikit-learn scipy
from sklearn.feature_extraction.text import TfidfVectorizer

# 用内联小语料模拟 180000 条新闻的场景
docs = ["湖人 队 赢得 总冠军", "美联储 宣布 加息", "高考 改革 方案 公布",
"湖人 战胜 凯尔特人", "央行 调整 利率", "教育部 发布 通知"] * 300

vec = TfidfVectorizer(
max_features=50000, # 只保留最高频的 5 万个词
min_df=2, # 出现在少于 2 篇文档中的词直接丢弃
max_df=0.9, # 出现在超过 90% 文档中的词视为停用词
ngram_range=(1, 2), # 加入 bi-gram，部分恢复词序
sublinear_tf=True, # 词频差异大，用 1+log(f)
token_pattern=r"(?u)\b\w+\b",
)
X = vec.fit_transform(docs)
print("矩阵形状:", X.shape)
print("稠密存储需要: %.2f GB" % (X.shape[0] * X.shape[1] * 8 / 1024 ** 3))
print("稀疏实际占用: %.2f MB" % ((X.data.nbytes + X.indices.nbytes + X.indptr.nbytes) / 1024 ** 2))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「稀疏矩阵与特征裁剪的工程实践」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
