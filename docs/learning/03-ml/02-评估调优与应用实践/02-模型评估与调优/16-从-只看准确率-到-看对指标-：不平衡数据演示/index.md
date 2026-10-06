---
article_id: kp-21678c82df84afd8
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 15
learning_objective: 理解并验证：从"只看准确率"到"看对指标"：不平衡数据演示
---

# 从"只看准确率"到"看对指标"：不平衡数据演示

> **学习目标**：能够解释「从"只看准确率"到"看对指标"：不平衡数据演示」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""演示：类别不平衡时 Accuracy 会骗人，必须看 F1 / AUC"""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, f1_score,
precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split

# 造一个 1:20 的不平衡数据集
X, y = make_classification(n_samples=4000, n_features=12, n_informative=6,
weights=[0.95, 0.05], flip_y=0.01, random_state=22)
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.3, random_state=22, stratify=y
)
print("测试集正例比例: %.3f" % y_test.mean)

# 1. 永远预测多数类 —— "作弊"基线
dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
yp = dummy.predict(X_test)
print("\n[作弊基线] Accuracy=%.4f Precision=%.4f Recall=%.4f F1=%.4f"
% (accuracy_score(y_test, yp), precision_score(y_test, yp, zero_division=0),
recall_score(y_test, yp, zero_division=0), f1_score(y_test, yp, zero_division=0)))

# 2. 普通逻辑回归
lr = LogisticRegression(max_iter=5000).fit(X_train, y_train)
yp = lr.predict(X_test)
print("[普通LR ] Accuracy=%.4f Precision=%.4f Recall=%.4f F1=%.4f AUC=%.4f"
% (accuracy_score(y_test, yp), precision_score(y_test, yp, zero_division=0),
recall_score(y_test, yp, zero_division=0), f1_score(y_test, yp, zero_division=0),
roc_auc_score(y_test, lr.predict_proba(X_test)[:, 1])))

# 3. 加权逻辑回归
lr_bal = LogisticRegression(max_iter=5000, class_weight="balanced").fit(X_train, y_train)
yp = lr_bal.predict(X_test)
print("[加权LR ] Accuracy=%.4f Precision=%.4f Recall=%.4f F1=%.4f AUC=%.4f"
% (accuracy_score(y_test, yp), precision_score(y_test, yp, zero_division=0),
recall_score(y_test, yp, zero_division=0), f1_score(y_test, yp, zero_division=0),
roc_auc_score(y_test, lr_bal.predict_proba(X_test)[:, 1])))
print("\n分类报告（加权 LR）：\n", classification_report(y_test, yp, digits=4))
# 结论：作弊基线 Accuracy 很高（≈0.95）但 F1=0；
# 加权后 Accuracy 可能略降，但 Recall/F1 显著提升 —— 这才是有价值的模型。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从"只看准确率"到"看对指标"：不平衡数据演示」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
