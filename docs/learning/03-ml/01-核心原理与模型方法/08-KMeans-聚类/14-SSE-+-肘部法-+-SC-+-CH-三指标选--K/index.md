---
article_id: kp-22cbca9240b38acd
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 13
learning_objective: 理解并验证：SSE + 肘部法 + SC + CH 三指标选 $K$
---

# SSE + 肘部法 + SC + CH 三指标选 $K$

> **学习目标**：能够解释「SSE + 肘部法 + SC + CH 三指标选 $K$」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""用三种指标共同确定最佳 K"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import calinski_harabasz_score, silhouette_score

# 1. 造数据：1000 样本、2 特征、4 个真实簇
x, y = make_blobs(n_samples=1000, n_features=2,
 centers=[[-1, -1], [0, 0], [1, 1], [2, 2]],
 cluster_std=[0.4, 0.2, 0.2, 0.2], random_state=22)

plt.figure(figsize=(6, 5))
plt.scatter(x[:, 0], x[:, 1], marker="o", s=10)
plt.title("原始数据（无标签）")
plt.show()

ks = list(range(2, 11))
sse_list, sc_list, ch_list = [], [], []

for k in ks:
 km = KMeans(n_clusters=k, n_init=10, max_iter=100, random_state=0)
 labels = km.fit_predict(x)
 sse_list.append(km.inertia_)
 sc_list.append(silhouette_score(x, labels))
 ch_list.append(calinski_harabasz_score(x, labels))

# ---- SSE 肘部法（k 从 1 开始更能看出拐点）----
sse_all = []
for k in range(1, 11):
 sse_all.append(KMeans(n_clusters=k, n_init=10, random_state=0).fit(x).inertia_)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
axes[0].plot(range(1, 11), sse_all, "or-")
axes[0].set_title("肘部法：SSE vs K")
axes[0].set_xlabel("K")
axes[0].set_ylabel("SSE")
axes[0].grid(True)

axes[1].plot(ks, sc_list, "ob-")
axes[1].set_title("轮廓系数 SC vs K（越大越好）")
axes[1].set_xlabel("K")
axes[1].set_ylabel("SC")
axes[1].grid(True)

axes[2].plot(ks, ch_list, "og-")
axes[2].set_title("CH 指数 vs K（越大越好）")
axes[2].set_xlabel("K")
axes[2].set_ylabel("CH")
axes[2].grid(True)
plt.tight_layout()
plt.show()

print("最佳 K（SC 最大）:", ks[int(np.argmax(sc_list))])
print("最佳 K（CH 最大）:", ks[int(np.argmax(ch_list))])
# 三个指标通常一致指向 K=4，与造数据时的 4 个真实中心吻合
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「SSE + 肘部法 + SC + CH 三指标选 $K$」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
