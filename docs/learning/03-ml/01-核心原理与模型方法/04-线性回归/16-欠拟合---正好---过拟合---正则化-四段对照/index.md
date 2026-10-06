---
article_id: kp-de4025d9eae926f3
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 15
learning_objective: 理解并验证：欠拟合 / 正好 / 过拟合 / 正则化 四段对照
---

# 欠拟合 / 正好 / 过拟合 / 正则化 四段对照

> **学习目标**：能够解释「欠拟合 / 正好 / 过拟合 / 正则化 四段对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""用同一个数据集演示：欠拟合 -> 正好拟合 -> 过拟合 -> L1/L2 正则化"""
import numpy as np
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error

# 1. 造数据：真实关系是二次的
np.random.seed(666)
x = np.random.uniform(-3, 3, size=100)
y = 0.5 * x ** 2 + x + 2 + np.random.normal(0, 1, size=100)
X = x.reshape(-1, 1)
X2 = np.hstack([X, X ** 2]) # 2 个特征
X10 = np.hstack([X ** k for k in range(1, 11)]) # 10 个特征


def report(name, model, Xd):
 model.fit(Xd, y)
 mse = mean_squared_error(y, model.predict(Xd))
 coef = np.round(model.coef_, 4)
 print(f"{name:26s} MSE={mse:8.4f} coef_={coef}")


 report("① 欠拟合(仅 x)", LinearRegression(), X)
 report("② 正好拟合(x, x^2)", LinearRegression(), X2)
 report("③ 过拟合(x..x^10)", LinearRegression(), X10)
 report("④ L1 正则化 Lasso(a=0.1)", Lasso(alpha=0.1), X10)
 report("⑤ L2 正则化 Ridge(a=10)", Ridge(alpha=10), X10)
```

**预期现象**：
- ① 的 MSE 最大（约 3.07），曲线是一条直线；
- ②③ 的 MSE 明显下降，③ 略低于 ②，但③ 的系数很大且曲线剧烈波动；
- ④ Lasso 会把一部分高次项系数**精确压成 0**；
- ⑤ Ridge 把高次项系数**压得很小但不为 0**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「欠拟合 / 正好 / 过拟合 / 正则化 四段对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
