---
article_id: kp-5ac2fe905dad5abf
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 13
learning_objective: 理解并验证：混淆矩阵、P/R/F1 与 ROC 的一体化演示
---

# 混淆矩阵、P/R/F1 与 ROC 的一体化演示

> **学习目标**：能够解释「混淆矩阵、P/R/F1 与 ROC 的一体化演示」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""用课程的两模型例子，把混淆矩阵到 AUC 一次性算清"""
import numpy as np
import pandas as pd
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
recall_score, roc_auc_score, roc_curve)

y_true = ["恶性"] * 6 + ["良性"] * 4
y_pred_A = ["恶性"] * 3 + ["良性"] * 3 + ["良性"] * 4
y_pred_B = ["恶性"] * 9 + ["良性"] * 1

labels = ["恶性", "良性"]
for name, y_pred in [("模型A", y_pred_A), ("模型B", y_pred_B)]:
 cm = confusion_matrix(y_true, y_pred, labels=labels)
 df = pd.DataFrame(cm, index=["真实-" + l for l in labels],
 columns=["预测-" + l for l in labels])
 acc = (cm[0, 0] + cm[1, 1]) / cm.sum()
 print(f"===== {name} =====")
 print(df)
 print("准确率 :", round(acc, 4))
 print("精确率 :", round(precision_score(y_true, y_pred, pos_label="恶性"), 4))
 print("召回率 :", round(recall_score(y_true, y_pred, pos_label="恶性"), 4))
 print("F1 :", round(f1_score(y_true, y_pred, pos_label="恶性"), 4))
 print()

 # ---- 手工绘制 ROC 曲线（课程广告点击案例）----
 y_true_click = np.array([1, 0, 1, 0, 0, 0])
 y_score_click = np.array([0.9, 0.7, 0.8, 0.6, 0.5, 0.4])
 fpr, tpr, thresholds = roc_curve(y_true_click, y_score_click)
 print("阈值 :", thresholds)
 print("FPR :", fpr)
 print("TPR :", tpr)
 print("AUC :", roc_auc_score(y_true_click, y_score_click))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「混淆矩阵、P/R/F1 与 ROC 的一体化演示」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
