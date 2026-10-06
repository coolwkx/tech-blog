---
article_id: kp-ff971f1192959c93
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 14
learning_objective: 理解并验证：手写 XGBoost 的打分函数与增益（验证推导）
---

# 手写 XGBoost 的打分函数与增益（验证推导）

> **学习目标**：能够解释「手写 XGBoost 的打分函数与增益（验证推导）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""用平方损失验证：叶子最优权重 w* = -G/(H+lambda)，以及分裂增益 Gain"""
import numpy as np

def leaf_score(G, H, lam):
    """最优目标值 Obj* = -1/2 * G^2/(H+lam)"""
    return -0.5 * G ** 2 / (H + lam)

def xgb_split_gain(g, h, left_idx, lam=1.0, gamma=0.0):
    """g, h 为全体样本的一阶/二阶导；left_idx 为左子集下标"""
    G, H = g.sum, h.sum
    GL, HL = g[left_idx].sum, h[left_idx].sum
    GR, HR = G - GL, H - HL
    return (0.5 * (GL ** 2 / (HL + lam) + GR ** 2 / (HR + lam) - G ** 2 / (H + lam))
- gamma)

if __name__ == "__main__":
    # 平方损失 L = 1/2 (y - yhat)^2 时：g = yhat - y, h = 1
    y = np.array([5.56, 5.70, 5.91, 6.40, 6.80, 7.05, 8.90, 8.70, 9.00, 9.05])
    yhat = np.full_like(y, y.mean) # 初始预测为均值
    g = yhat - y # 一阶导
    h = np.ones_like(y) # 二阶导恒为 1

    print("g =", np.round(g, 4))
    print("最优叶子权重 w* =", round(-g.sum / (h.sum + 1.0), 4)) # 应为 0

    for s in [3.5, 6.5]:
        left = np.where(np.arange(1, 11) < s)[0]
        gain = xgb_split_gain(g, h, left, lam=1.0, gamma=0.0)
        print(f"以 s={s} 分裂的 Gain = {gain:.4f}")
        # 期望：s=6.5 的 Gain 大于 s=3.5（因为 m(6.5) 更小，损失下降更多）
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写 XGBoost 的打分函数与增益（验证推导）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
