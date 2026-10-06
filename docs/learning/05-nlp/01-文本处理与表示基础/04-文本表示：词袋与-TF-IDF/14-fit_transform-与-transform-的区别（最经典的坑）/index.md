---
article_id: kp-264d5abea058966f
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 13
learning_objective: 理解并验证：fit_transform 与 transform 的区别（最经典的坑）
---

# fit_transform 与 transform 的区别（最经典的坑）

> **学习目标**：能够解释「fit_transform 与 transform 的区别（最经典的坑）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 可运行示例

## 本次只学这一点

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

train = ["这个酒店位置很好 干净", "服务很好 推荐", "早餐不好 房间差", "服务不到位 隔音差"]
y = [1, 1, 0, 0]
test = ["位置很好 服务不错", "房间差 服务不到位"]

vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")

# 训练集: fit + transform 一步完成，会学习词表与 IDF
X_train = vec.fit_transform(train)

# 测试集: 只能 transform，复用训练时学到的词表与 IDF
X_test = vec.transform(test)

clf = LogisticRegression(max_iter=1000).fit(X_train, y)
print("预测:", clf.predict(X_test))

# 查看对分类贡献最大的词，便于做错误分析
import numpy as np
names = np.array(vec.get_feature_names_out)
for cls, coef in zip(clf.classes_, clf.coef_):
 top = names[np.argsort(coef)[-5:]][::-1]
 print(f"类别 {cls} 的正向关键词: {list(top)}")
```

如果对测试集也调用 `fit_transform`，会**重新学习一套词表和 IDF**，导致：
训练/测试特征空间维度可能不同（直接报维度不匹配），或维度碰巧相同但列的含义错位，模型给出的预测是垃圾。这是一个不会报错、只会静默变差的最危险错误。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「fit_transform 与 transform 的区别（最经典的坑）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
