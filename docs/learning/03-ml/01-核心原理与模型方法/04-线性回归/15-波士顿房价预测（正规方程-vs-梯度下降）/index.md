---
article_id: kp-58dc9029dae72d61
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 14
learning_objective: 理解并验证：波士顿房价预测（正规方程 vs 梯度下降）
---

# 波士顿房价预测（正规方程 vs 梯度下降）

> **学习目标**：能够解释「波士顿房价预测（正规方程 vs 梯度下降）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 可运行示例

## 本次只学这一点

> `sklearn.datasets.load_boston` 在 scikit-learn 1.2 起已被移除（伦理争议），学习笔记也给出了替代方案——直接从原始地址读取。下面使用**离线可复现**的 California Housing 数据集，流程完全一致。

```python
# -*- coding: utf-8 -*-
"""回归案例：标准化 -> 正规方程 / SGD -> MSE、RMSE、MAE 评估"""
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
root_mean_squared_error)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. 加载数据（若网络不可用，可换成 pandas 读取本地 csv）
data = fetch_california_housing()
X, y = data.data, data.target

# 2. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=22
)

# 3. 特征工程：标准化（回归中不同特征量纲不一致会影响结果）
transfer = StandardScaler()
X_train = transfer.fit_transform(X_train)
X_test = transfer.transform(X_test)


def evaluate(name, model):
 y_pred = model.predict(X_test)
 print(f"--- {name} ---")
 print("MSE :", mean_squared_error(y_test, y_pred))
 print("RMSE:", root_mean_squared_error(y_test, y_pred))
 print("MAE :", mean_absolute_error(y_test, y_pred))


 # 4a. 正规方程
 lr = LinearRegression(fit_intercept=True)
 lr.fit(X_train, y_train)
 print("coef_ 前 5 项:", lr.coef_[:5], " intercept_:", lr.intercept_)
 evaluate("LinearRegression（正规方程）", lr)

 # 4b. 随机梯度下降
 sgd = SGDRegressor(fit_intercept=True, learning_rate="constant", eta0=0.01,
 max_iter=1000, random_state=22)
 sgd.fit(X_train, y_train)
 evaluate("SGDRegressor（梯度下降）", sgd)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「波士顿房价预测（正规方程 vs 梯度下降）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
