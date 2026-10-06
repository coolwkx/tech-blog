---
article_id: kp-04a060e83f4f96e2
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 16
learning_objective: 理解并验证：多项式特征 + 正则化：特征组合的正确姿势
---

# 多项式特征 + 正则化：特征组合的正确姿势

> **学习目标**：能够解释「多项式特征 + 正则化：特征组合的正确姿势」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""特征组合：加多项式项提升拟合能力，用正则化控制过拟合"""
import numpy as np
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures

np.random.seed(666)
x = np.random.uniform(-3, 3, size=100)
y = 0.5 * x ** 2 + x + 2 + np.random.normal(0, 1, size=100)
X = x.reshape(-1, 1)

print("【只用 1 维特征】")
m = LinearRegression.fit(X, y)
print("MSE = %.4f（欠拟合）" % mean_squared_error(y, m.predict(X)))

print("\n【手工 hstack 加二次项】（做法）")
X2 = np.hstack([X, X ** 2])
m2 = LinearRegression.fit(X2, y)
print("MSE = %.4f（合理拟合）" % mean_squared_error(y, m2.predict(X2)))

print("\n【PolynomialFeatures(degree=10) + 不同正则化】")
poly = PolynomialFeatures(degree=10, include_bias=False)
X10 = poly.fit_transform(X)
for name, model in [("无正则 LinearRegression", LinearRegression),
("L1 Lasso(alpha=0.1)", Lasso(alpha=0.1, max_iter=10000)),
("L2 Ridge(alpha=1)", Ridge(alpha=1))]:
 model.fit(X10, y)
 coef = np.round(model.coef_, 4)
 n_zero = int((np.abs(coef) < 1e-8).sum)
 print(f"{name:26s} MSE={mean_squared_error(y, model.predict(X10)):7.4f} "
 f"零系数个数={n_zero}/10")
 # 结论：无正则时训练 MSE 最小但曲线剧烈抖动（过拟合）；
 # Lasso 把一部分高次项系数精确压成 0（特征选择）；
 # Ridge 把高次项系数压得很小但不为 0（平滑收缩）。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多项式特征 + 正则化：特征组合的正确姿势」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
