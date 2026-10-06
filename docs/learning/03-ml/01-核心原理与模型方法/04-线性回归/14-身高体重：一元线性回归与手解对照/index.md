---
article_id: kp-327c19d39bb4efe9
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 13
learning_objective: 理解并验证：身高体重：一元线性回归与手解对照
---

# 身高体重：一元线性回归与手解对照

> **学习目标**：能够解释「身高体重：一元线性回归与手解对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""一元线性回归：身高 -> 体重，并与手算的解析解对照"""
import numpy as np
from sklearn.linear_model import LinearRegression

x_train = [[160], [166], [172], [174], [180]]
y_train = [56.3, 60.6, 65.1, 68.5, 75.0]

estimator = LinearRegression()
estimator.fit(x_train, y_train)
print("权重 coef_ :", estimator.coef_) # [0.92942177]
print("偏置 intercept_ :", estimator.intercept_) # -93.27346938775514
print("预测 176cm 体重 :", estimator.predict([[176]])) # [70.3047619]

# ---- 手算验证：解正规方程 ----
X = np.array(x_train, dtype=float).ravel()
y = np.array(y_train)
A = np.vstack([X, np.ones_like(X)]).T # 设计矩阵 [x, 1]
w = np.linalg.solve(A.T @ A, A.T @ y) # (X'X)^-1 X'y
print("手算 k, b :", w)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「身高体重：一元线性回归与手解对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
