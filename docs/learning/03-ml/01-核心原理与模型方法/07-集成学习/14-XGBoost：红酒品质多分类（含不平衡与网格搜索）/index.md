---
article_id: kp-233136293177a43b
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 13
learning_objective: 理解并验证：XGBoost：红酒品质多分类（含不平衡与网格搜索）
---

# XGBoost：红酒品质多分类（含不平衡与网格搜索）

> **学习目标**：能够解释「XGBoost：红酒品质多分类（含不平衡与网格搜索）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""XGBoost 红酒品质多分类：含样本不均衡处理、分层交叉验证与网格搜索"""
from collections import Counter

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.utils import class_weight

def step1_split(src="红酒品质分类.csv"):
 """加载 + 划分，并把标签从 3~8 平移到 0~5"""
 data = pd.read_csv(src)
 x = data.iloc[:, :-1]
 y = data.iloc[:, -1] - 3 # 品质 3/4/5/6/7/8 -> 0/1/2/3/4/5
 print("标签分布:", Counter(y)) # 明显不均衡

 x_train, x_test, y_train, y_test = train_test_split(
 x, y, test_size=0.2, stratify=y, random_state=22 # stratify 保持类别比例
 )
 pd.concat([x_train, y_train], axis=1).to_csv("红酒品质分类-train.csv", index=False)
 pd.concat([x_test, y_test], axis=1).to_csv("红酒品质分类-test.csv", index=False)
 return x_train, y_train, x_test, y_test

def step2_train_basic(x_train, y_train, x_test, y_test):
 """基础训练"""
 estimator = xgb.XGBClassifier(
 n_estimators=100, objective="multi:softmax", eval_metric="merror",
 eta=0.1, random_state=22,
 )
 estimator.fit(x_train, y_train)
 print(classification_report(y_true=y_test, y_pred=estimator.predict(x_test)))
 joblib.dump(estimator, "mymodelxgboost.pth")

def step3_train_balanced(x_train, y_train, x_test, y_test):
 """样本不均衡：计算样本权重并传给 fit"""
 classes_weights = class_weight.compute_sample_weight(class_weight="balanced", y=y_train)
 estimator = xgb.XGBClassifier(
 n_estimators=100, objective="multi:softmax", eval_metric="merror",
 eta=0.1, random_state=22,
 )
 estimator.fit(x_train, y_train, sample_weight=classes_weights)
 print(classification_report(y_true=y_test, y_pred=estimator.predict(x_test)))

def step4_grid_search(x_train, y_train, x_test, y_test):
 """分层交叉验证 + 网格搜索"""
 spliter = StratifiedKFold(n_splits=5, shuffle=True, random_state=22)
 param_grid = {"max_depth": np.arange(3, 5, 1),
 "n_estimators": np.arange(50, 150, 50),
 "eta": np.arange(0.1, 1, 0.3)}
 estimator = xgb.XGBClassifier(
 n_estimators=100, objective="multi:softmax", eval_metric="merror",
 eta=0.1, random_state=22,
 )
 grid = GridSearchCV(estimator=estimator, param_grid=param_grid, cv=spliter, n_jobs=-1)
 grid.fit(x_train, y_train)
 y_pred = grid.predict(x_test)
 print(classification_report(y_true=y_test, y_pred=y_pred))
 print("best_estimator_:", grid.best_estimator_)
 print("best_params_ :", grid.best_params_)

if __name__ == "__main__":
 x_train, y_train, x_test, y_test = step1_split()
 step2_train_basic(x_train, y_train, x_test, y_test)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「XGBoost：红酒品质多分类（含不平衡与网格搜索）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
