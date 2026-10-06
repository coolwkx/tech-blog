---
article_id: kp-ce2854669842bbaf
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 15
learning_objective: 理解并验证：类别特征：one-hot、DictVectorizer 与哑变量陷阱
---

# 类别特征：one-hot、DictVectorizer 与哑变量陷阱

> **学习目标**：能够解释「类别特征：one-hot、DictVectorizer 与哑变量陷阱」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""类别特征三种常用处理方式"""
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

df = pd.DataFrame({
"Pclass": [1, 3, 2, 1, 3],
"Age": [22.0, 38.0, 26.0, 35.0, 28.0],
"Sex": ["female", "male", "male", "female", "male"],
"Survived": [1, 0, 0, 1, 0],
})

# ---- 方式 1：pandas get_dummies（最常用）----
X = pd.get_dummies(df[["Pclass", "Age", "Sex"]])
print("get_dummies 列名:", list(X.columns))
print(X.head)

# ---- 方式 2：DictVectorizer ----
vec = DictVectorizer(sparse=False)
X_dict = vec.fit_transform(df[["Pclass", "Age", "Sex"]].to_dict(orient="records"))
print("\nDictVectorizer 特征名:", vec.get_feature_names_out)
print(X_dict)

# ---- 方式 3：删掉基准列，避免哑变量陷阱 ----
# 类别取值 k 个 -> 只保留 k-1 个 0/1 列
X_safe = pd.get_dummies(df[["Pclass", "Sex"]], drop_first=True)
print("\ndrop_first 后列名:", list(X_safe.columns))

# 说明：树模型对共线不敏感，可以保留全部哑变量；
# 线性模型（含逻辑回归）与需要求逆的模型必须删一列。
clf = LogisticRegression(max_iter=1000)
clf.fit(pd.concat([X_safe, df[["Age"]]], axis=1), df["Survived"])
print("系数:", dict(zip(list(X_safe.columns) + ["Age"], clf.coef_[0].round(3))))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「类别特征：one-hot、DictVectorizer 与哑变量陷阱」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
