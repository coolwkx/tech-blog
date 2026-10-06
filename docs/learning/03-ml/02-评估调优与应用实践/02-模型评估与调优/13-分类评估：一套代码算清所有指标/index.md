---
article_id: kp-e6ac9f56a43768b3
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 12
learning_objective: 理解并验证：分类评估：一套代码算清所有指标
---

# 分类评估：一套代码算清所有指标

> **学习目标**：能够解释「分类评估：一套代码算清所有指标」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""分类评估：混淆矩阵 -> P/R/F1 -> ROC/AUC -> classification_report"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (auc, classification_report, confusion_matrix,
f1_score, precision_score, recall_score,
roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

data = load_breast_cancer()
X, y = data.data, data.target # 0=malignant, 1=benign
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=22, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

clf = LogisticRegression(max_iter=5000, class_weight="balanced")
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
y_score = clf.predict_proba(X_test)[:, 1] # 正例（label=1）的概率

# 1. 混淆矩阵
cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
print(pd.DataFrame(cm,
index=["真实-恶性(0)", "真实-良性(1)"],
columns=["预测-恶性(0)", "预测-良性(1)"]))
TN, FP, FN, TP = cm.ravel
print(f"TP={TP} FN={FN} FP={FP} TN={TN}")
print(f"手算 Accuracy={(TP+TN)/cm.sum:.4f} Precision={TP/(TP+FP):.4f} "
f"Recall={TP/(TP+FN):.4f} F1={2*TP/(2*TP+FP+FN):.4f} "
f"FPR={FP/(FP+TN):.4f}")

# 2. sklearn API 对照（注意 pos_label 必须显式指定）
print("\nsklearn Precision=%.4f Recall=%.4f F1=%.4f" % (
precision_score(y_test, y_pred, pos_label=1),
recall_score(y_test, y_pred, pos_label=1),
f1_score(y_test, y_pred, pos_label=1)))
print("AUC = %.4f" % roc_auc_score(y_test, y_score))
print("\n分类评估报告：\n", classification_report(y_test, y_pred,
target_names=["malignant", "benign"]))

# 3. ROC 曲线
fpr, tpr, thr = roc_curve(y_test, y_score)
plt.figure(figsize=(6, 6))
plt.plot(fpr, tpr, label="ROC (AUC = %.3f)" % auc(fpr, tpr))
plt.plot([0, 1], [0, 1], "k--", label="random guess (AUC=0.5)")
plt.scatter([0], [1], c="red", marker="*", s=150, label="ideal (0,1)")
plt.xlabel("FPR"); plt.ylabel("TPR"); plt.legend; plt.grid(True)
plt.title("ROC curve")
plt.show()

# 4. 分层交叉验证：比单次留出更稳的估计
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=22)
scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="f1")
print("5 折分层 CV F1:", np.round(scores, 4), "均值=%.4f 标准差=%.4f"
% (scores.mean, scores.std))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「分类评估：一套代码算清所有指标」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
