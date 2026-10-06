---
article_id: kp-bc5b6f66c4444a18
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-33f370d2f18b
learning_sourceId: 33f370d2f18b
learning_order: 11
learning_objective: 理解并验证：手写 CART 回归树的最优切分点（验证 2.5 的表）
---

# 手写 CART 回归树的最优切分点（验证 2.5 的表）

> **学习目标**：能够解释「手写 CART 回归树的最优切分点（验证 2.5 的表）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率与信息论中"熵"的直观含义、对数运算 $\log_2$、pandas 的缺失值处理与 `get_dummies`（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：决策树 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""按平方损失最小化，找出单特征 CART 回归树的最优切分点"""
import numpy as np

x = np.arange(1, 11)
y = np.array([5.56, 5.70, 5.91, 6.40, 6.80, 7.05, 8.90, 8.70, 9.00, 9.05])

best = None
for s in np.arange(1.5, 10.0, 1.0):
    left, right = y[x < s], y[x >= s]
    c1, c2 = left.mean, right.mean
    m = ((left - c1) ** 2).sum + ((right - c2) ** 2).sum
    print(f"s={s:4.1f} c1={c1:7.4f} c2={c2:7.4f} m(s)={m:8.4f}")
    if best is None or m < best[1]:
        best = (s, m, c1, c2)

        print(f"\n最优切分点 s={best[0]}, m(s)={best[1]:.4f}, 左输出={best[2]:.4f}, 右输出={best[3]:.4f}")
        # 期望：s=6.5, m=1.9300, 左=6.2367, 右=8.9125
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/05-决策树.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写 CART 回归树的最优切分点（验证 2.5 的表）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/05-决策树.md)
