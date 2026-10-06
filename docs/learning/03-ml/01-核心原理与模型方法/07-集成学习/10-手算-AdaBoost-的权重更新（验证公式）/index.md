---
article_id: kp-ce452911593534ba
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 9
learning_objective: 理解并验证：手算 AdaBoost 的权重更新（验证公式）
---

# 手算 AdaBoost 的权重更新（验证公式）

> **学习目标**：能够解释「手算 AdaBoost 的权重更新（验证公式）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""手算 AdaBoost 第 1、2 轮的模型权重与样本权重"""
import numpy as np

def adaboost_round(weights, mis_idx):
 """weights: 当前样本权重; mis_idx: 本轮分类错误的样本下标"""
 eps = weights[mis_idx].sum
 alpha = 0.5 * np.log((1 - eps) / eps)
 new_w = weights * np.exp(-alpha) # 分对的变小
 new_w[mis_idx] = weights[mis_idx] * np.exp(alpha) # 分错的变大
 Z = new_w.sum
 return eps, alpha, new_w / Z, Z

if __name__ == "__main__":
 n = 10
 w = np.full(n, 1.0 / n)
 print("初始权重:", w)

 # 第 1 轮：以 2.5 分裂，错 3 个样本（下标 6,7,8 即第 7、8、9 个）
 eps1, a1, w, Z1 = adaboost_round(w, [6, 7, 8])
 print(f"\n第1轮: eps={eps1:.4f} alpha={a1:.4f} Z={Z1:.4f}")
 print(" 分对样本权重:", round(w[0], 5), " 分错样本权重:", round(w[6], 5))
 # 期望 eps=0.3, alpha=0.4236, 分对 0.07143, 分错 0.16667

 # 第 2 轮：以 8.5 分裂，加权错误率 = 0.07143*3（错下标 3,4,5）
 eps2, a2, w, Z2 = adaboost_round(w, [3, 4, 5])
 print(f"\n第2轮: eps={eps2:.4f} alpha={a2:.4f} Z={Z2:.4f}")
 # 期望 eps≈0.2143, alpha≈0.6496
 print("\n第3轮（给出）: eps=0.1820, alpha=0.7514")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手算 AdaBoost 的权重更新（验证公式）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
