---
article_id: kp-b923e63d49c05042
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 11
learning_objective: 理解并验证：回归指标：手算与 API 对照，看清 MAE/RMSE 的差异
---

# 回归指标：手算与 API 对照，看清 MAE/RMSE 的差异

> **学习目标**：能够解释「回归指标：手算与 API 对照，看清 MAE/RMSE 的差异」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""回归指标：MAE / MSE / RMSE / R2 的手算与 API 对照"""
import numpy as np
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
root_mean_squared_error)

y_true = np.array([3.0, -0.5, 2.0, 7.0])
y_pred = np.array([2.5, 0.0, 2.0, 8.0])

mae = np.mean(np.abs(y_true - y_pred))
mse = np.mean((y_true - y_pred) ** 2)
rmse = np.sqrt(mse)

print(f"手算 MAE={mae:.4f} MSE={mse:.4f} RMSE={rmse:.4f}")
print(f"sklearn MAE={mean_absolute_error(y_true, y_pred):.4f} "
f"MSE={mean_squared_error(y_true, y_pred):.4f} "
f"RMSE={root_mean_squared_error(y_true, y_pred):.4f} "
f"R2={r2_score(y_true, y_pred):.4f}")

print("\n--- RMSE 对大误差的放大效应 ---")
for errs in ([1, 1, 1, 1], [1, 3, 0, 0], [1, 20, 0, 0]):
 e = np.array(errs, dtype=float)
 print(f"误差 {errs}: MAE={np.abs(e).mean:6.3f} RMSE={np.sqrt((e**2).mean):6.3f} "
 f"RMSE/MAE={np.sqrt((e**2).mean)/np.abs(e).mean:.3f}")
 # 误差越不均匀，RMSE 与 MAE 的比值越大
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「回归指标：手算与 API 对照，看清 MAE/RMSE 的差异」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
