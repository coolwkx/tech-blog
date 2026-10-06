---
article_id: kp-5baa7fbe8e67112e
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 13
learning_objective: 理解并验证：归一化 vs 标准化：数值对照
---

# 归一化 vs 标准化：数值对照

> **学习目标**：能够解释「归一化 vs 标准化：数值对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""手动实现 MinMax 与 Z-Score，并与 sklearn 结果对照"""
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

x = np.array([[90, 2, 10, 40], [60, 4, 15, 45], [75, 3, 13, 46]], dtype=float)
print("原始数据:\n", x)

# ---- 手写归一化 ----
minmax = (x - x.min(axis=0)) / (x.max(axis=0) - x.min(axis=0))
print("\n手写 MinMax:\n", np.round(minmax, 4))

# ---- 手写标准化 ----
mu, sigma = x.mean(axis=0), x.std(axis=0) # ddof=0，与 sklearn 一致
zscore = (x - mu) / sigma
print("\n手写 Z-Score:\n", np.round(zscore, 4))

# ---- sklearn 对照 ----
mm = MinMaxScaler
print("\nsklearn MinMax:\n", np.round(mm.fit_transform(x), 4))

ss = StandardScaler
print("sklearn StandardScaler:\n", np.round(ss.fit_transform(x), 4))
print("\nmean_ =", np.round(ss.mean_, 4))
print("var_ =", np.round(ss.var_, 4))
print("scale_=", np.round(ss.scale_, 4))

# ---- 反变换 ----
print("\n反变换回原值:\n", np.round(ss.inverse_transform(ss.transform(x)), 4))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「归一化 vs 标准化：数值对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
