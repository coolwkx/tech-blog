---
article_id: kp-fb98ed8db63cbebb
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 12
learning_objective: 理解并验证：KNN 回归：验证"取邻居均值"这一条
---

# KNN 回归：验证"取邻居均值"这一条

> **学习目标**：能够解释「KNN 回归：验证"取邻居均值"这一条」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""KNN 回归：预测值 = 最近 K 个邻居目标值的平均"""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

X = [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]]
y = [0.1, 0.2, 0.3, 0.4]

model = KNeighborsRegressor(n_neighbors=3)
model.fit(X, y)

q = [[4, 4, 5]]
print("预测值:", model.predict(q)) # 0.3（0.2/0.3/0.4 的均值）

# 手工验证：q 到 4 个训练点的距离（欧氏）
q_arr = np.array(q[0])
for xi, yi in zip(X, y):
 print(f"点 {xi} 距离 {np.linalg.norm(np.array(xi) - q_arr):.4f} 目标值 {yi}")
 # 最近的 3 个距离为 1.7321/1.7321/3.4641 -> 目标值 0.2, 0.3, 0.4 -> 平均 0.3
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「KNN 回归：验证"取邻居均值"这一条」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
