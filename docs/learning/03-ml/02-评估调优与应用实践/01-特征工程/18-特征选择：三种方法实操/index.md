---
article_id: kp-fe4f6cca1bab5b9e
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 17
learning_objective: 理解并验证：特征选择：三种方法实操
---

# 特征选择：三种方法实操

> **学习目标**：能够解释「特征选择：三种方法实操」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""特征选择：方差过滤 / 相关系数 / 树模型重要性 / L1 稀疏"""
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = data.target

# ---- 方法 1：方差过滤（剔除几乎不变的常量特征）----
vt = VarianceThreshold(threshold=0.1)
X_vt = vt.fit_transform(X)
print(f"方差过滤: {X.shape[1]} -> {X_vt.shape[1]} 列")

# ---- 方法 2：相关系数过滤（剔除与标签几乎无关的特征）----
corr = X.apply(lambda col: np.corrcoef(col, y)[0, 1])
corr_abs = corr.abs.sort_values(ascending=False)
print("\n与标签相关性最高的 10 个特征：")
print(corr_abs.head(10).round(4))
print("\n相关性最低的 5 个特征（候选删除）：")
print(corr_abs.tail(5).round(4))

# ---- 方法 3：树模型特征重要性 ----
rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X, y)
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n随机森林特征重要性 Top10：")
print(imp.head(10).round(4))
print("\n重要性接近 0 的特征（候选删除）：")
print(imp[imp < 0.005].round(4))

# ---- 方法 4：L1 正则化产生稀疏解（嵌入式特征选择）----
Xs = StandardScaler.fit_transform(X)
lr = LogisticRegression(penalty="l1", solver="liblinear", C=0.1, max_iter=5000)
lr.fit(Xs, y)
n_zero = int((np.abs(lr.coef_[0]) < 1e-8).sum)
print(f"\nL1 正则（C=0.1）：{n_zero}/{X.shape[1]} 个特征系数被压成 0")
print("非零特征:", list(np.array(X.columns)[np.abs(lr.coef_[0]) > 1e-8]))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「特征选择：三种方法实操」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
