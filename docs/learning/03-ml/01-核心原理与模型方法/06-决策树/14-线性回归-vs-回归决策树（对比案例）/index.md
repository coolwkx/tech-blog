---
article_id: kp-433494bd037e2c91
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-33f370d2f18b
learning_sourceId: 33f370d2f18b
learning_order: 13
learning_objective: 理解并验证：线性回归 vs 回归决策树（对比案例）
---

# 线性回归 vs 回归决策树（对比案例）

> **学习目标**：能够解释「线性回归 vs 回归决策树（对比案例）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率与信息论中"熵"的直观含义、对数运算 $\log_2$、pandas 的缺失值处理与 `get_dummies`（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：决策树 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""对比线性回归与回归决策树的拟合形态"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

x = np.array(list(range(1, 11))).reshape(-1, 1)
y = np.array([5.56, 5.70, 5.91, 6.40, 6.80, 7.05, 8.90, 8.70, 9.00, 9.05])

model1 = DecisionTreeRegressor(max_depth=1, random_state=0)
model2 = DecisionTreeRegressor(max_depth=3, random_state=0)
model3 = LinearRegression()
for m in (model1, model2, model3):
 m.fit(x, y)

 x_test = np.arange(0.0, 10.0, 0.01).reshape(-1, 1)
 plt.figure(figsize=(10, 6), dpi=100)
 plt.scatter(x, y, label="data")
 plt.plot(x_test, model1.predict(x_test), label="max_depth=1")
 plt.plot(x_test, model2.predict(x_test), label="max_depth=3")
 plt.plot(x_test, model3.predict(x_test), label="linear")
 plt.xlabel("data")
 plt.ylabel("target")
 plt.title("DecisionTreeRegressor vs LinearRegression")
 plt.legend()
 plt.show()
 # 结论：线性回归是一条直线；决策树是分段常数（阶梯状）曲线。
 # 深度 1 明显欠拟合；深度 3 拟合很好但已经出现"跳变"，再加深就会过拟合。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/05-决策树.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「线性回归 vs 回归决策树（对比案例）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/05-决策树.md)
