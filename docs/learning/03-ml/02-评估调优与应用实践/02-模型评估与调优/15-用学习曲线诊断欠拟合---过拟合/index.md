---
article_id: kp-22ea8bf0ecf2dfcd
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 14
learning_objective: 理解并验证：用学习曲线诊断欠拟合 / 过拟合
---

# 用学习曲线诊断欠拟合 / 过拟合

> **学习目标**：能够解释「用学习曲线诊断欠拟合 / 过拟合」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""learning_curve：看训练误差与验证误差随训练样本量的变化"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=22)

models = {
"逻辑回归（简单，可能欠拟合）": make_pipeline(StandardScaler,
LogisticRegression(max_iter=5000)),
"完全生长的决策树（可能过拟合）": DecisionTreeClassifier(random_state=0),
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, (name, model) in zip(axes, models.items()):
 train_sizes, train_scores, valid_scores = learning_curve(
 model, X, y, cv=cv, scoring="accuracy",
 train_sizes=np.linspace(0.1, 1.0, 8), n_jobs=-1
 )
 ax.plot(train_sizes, train_scores.mean(axis=1), "o-", label="训练集得分")
 ax.plot(train_sizes, valid_scores.mean(axis=1), "s-", label="验证集得分")
 ax.set_xlabel("训练样本数"); ax.set_ylabel("accuracy")
 ax.set_title(name); ax.legend; ax.grid(True)
 plt.tight_layout
 plt.show()

 # 诊断口诀：
 # 训练低 + 验证低 + 差距小 -> 欠拟合（加特征/加复杂度）
 # 训练高 + 验证低 + 差距大 -> 过拟合（加数据/正则化/降复杂度）
 # 训练高 + 验证高 + 差距小 -> 良好
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用学习曲线诊断欠拟合 / 过拟合」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
