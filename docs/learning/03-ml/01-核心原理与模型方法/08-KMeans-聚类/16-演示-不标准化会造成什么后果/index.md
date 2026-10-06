---
article_id: kp-ca938ef79767f801
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 15
learning_objective: 理解并验证：演示"不标准化会造成什么后果"
---

# 演示"不标准化会造成什么后果"

> **学习目标**：能够解释「演示"不标准化会造成什么后果"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""KMeans 之前不标准化：聚类被大量纲特征单独支配"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
A = np.concatenate([rng.normal(0, 1, 100), rng.normal(1000, 1, 100)])
B = np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 1, 100)])
X = np.c_[A, B]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
lab_raw = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
axes[0].scatter(A, B, c=lab_raw, s=20)
axes[0].set_title("不标准化：聚类只被大量纲特征 A 支配")

Xs = StandardScaler().fit_transform(X)
lab_std = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(Xs)
axes[1].scatter(A, B, c=lab_std, s=20)
axes[1].set_title("标准化后：两个特征共同影响聚类")
plt.show()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「演示"不标准化会造成什么后果"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
