---
article_id: kp-fee379a780cdfcfb
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 13
learning_objective: 理解并验证：网格搜索：随机森林调参全流程
---

# 网格搜索：随机森林调参全流程

> **学习目标**：能够解释「网格搜索：随机森林调参全流程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""GridSearchCV 完整流程：只在训练集上搜，测试集只评一次"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

# 以泰坦尼克号为例（把数据换成你自己的 csv 即可）
titan = pd.read_csv("train.csv")
x = titan[["Pclass", "Age", "Sex"]].copy
y = titan["Survived"]
x["Age"] = x["Age"].fillna(x["Age"].mean)
x = pd.get_dummies(x)

x_train, x_test, y_train, y_test = train_test_split(
x, y, test_size=0.2, random_state=22, stratify=y
)

# 1. 定义参数网格
param_grid = {
"n_estimators": [40, 50, 60, 70],
"max_depth": [2, 4, 6, 8, 10],
"min_samples_leaf": [1, 3, 5],
}

# 2. 实例化网格搜索（分类用分层折）
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=22)
grid = GridSearchCV(
estimator=RandomForestClassifier(random_state=9),
param_grid=param_grid,
cv=cv,
scoring="f1", # 不平衡数据别用 accuracy
n_jobs=-1,
return_train_score=True, # 便于诊断过拟合
)
grid.fit(x_train, y_train)

# 3. 结果解读
print("最优参数 :", grid.best_params_)
print("CV 最高平均得分:", round(grid.best_score_, 4))
print("测试集 F1 :", round(grid.score(x_test, y_test), 4))
print("最优模型 :", grid.best_estimator_)

results = pd.DataFrame(grid.cv_results_)
cols = ["param_n_estimators", "param_max_depth", "param_min_samples_leaf",
"mean_train_score", "mean_test_score", "std_test_score", "rank_test_score"]
print("\n各组参数结果（前 8 行）：")
print(results[cols].sort_values("rank_test_score").head(8).to_string(index=False))

# 4. 过拟合诊断：训练分数远高于验证分数 -> 过拟合
best = results.sort_values("rank_test_score").iloc[0]
print(f"\n最优组：train={best['mean_train_score']:.4f} "
f"valid={best['mean_test_score']:.4f} "
f"gap={best['mean_train_score'] - best['mean_test_score']:.4f}")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「网格搜索：随机森林调参全流程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
