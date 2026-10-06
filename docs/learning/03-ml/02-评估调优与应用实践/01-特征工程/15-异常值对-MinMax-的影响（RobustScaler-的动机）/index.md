---
article_id: kp-7eb71eb2208b467f
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 14
learning_objective: 理解并验证：异常值对 MinMax 的影响（RobustScaler 的动机）
---

# 异常值对 MinMax 的影响（RobustScaler 的动机）

> **学习目标**：能够解释「异常值对 MinMax 的影响（RobustScaler 的动机）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""演示：一个异常点如何摧毁 MinMax 的缩放效果"""
import numpy as np
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

normal = np.array([[1], [2], [3], [4], [5]], dtype=float)
with_outlier = np.array([[1], [2], [3], [4], [5], [1000]], dtype=float)

for name, data in [("无异常点", normal), ("含异常点 1000", with_outlier)]:
 mm = MinMaxScaler().fit_transform(data).ravel()
 ss = StandardScaler().fit_transform(data).ravel()
 rb = RobustScaler().fit_transform(data).ravel()
 print(f"\n=== {name} ===")
 print("MinMax :", np.round(mm, 4))
 print("Standard :", np.round(ss, 4))
 print("Robust(中位/ IQR):", np.round(rb, 4))
 # 结论：加一个异常点后，MinMax 把正常点全挤到 0.001~0.004 的极小范围（信息几乎丢失）；
 # Standard 受影响但轻一些；Robust 用中位数与 IQR，基本不受影响。
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「异常值对 MinMax 的影响（RobustScaler 的动机）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
