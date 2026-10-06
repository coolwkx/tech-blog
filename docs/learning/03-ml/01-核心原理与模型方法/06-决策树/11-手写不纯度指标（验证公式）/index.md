---
article_id: kp-e19eaacd29ef771b
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-33f370d2f18b
learning_sourceId: 33f370d2f18b
learning_order: 10
learning_objective: 理解并验证：手写不纯度指标（验证公式）
---

# 手写不纯度指标（验证公式）

> **学习目标**：能够解释「手写不纯度指标（验证公式）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率与信息论中"熵"的直观含义、对数运算 $\log_2$、pandas 的缺失值处理与 `get_dummies`（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：决策树 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""手算信息熵、条件熵、信息增益、信息增益率、基尼指数"""
import numpy as np

def entropy(counts):
 """counts: 各类别的样本数列表"""
 counts = np.asarray(counts, dtype=float)
 p = counts / counts.sum
 p = p[p > 0] # 0*log0 约定为 0
 return float(-(p * np.log2(p)).sum)

def gini(counts):
 counts = np.asarray(counts, dtype=float)
 p = counts / counts.sum
 return float(1 - (p ** 2).sum)

def info_gain(parent, splits):
 """parent: 父节点各类别计数; splits: [子节点计数列表, ...]"""
 n = sum(parent)
 cond = sum(sum(s) / n * entropy(s) for s in splits)
 return entropy(parent) - cond, cond

def gain_ratio(parent, splits):
 """信息增益率 = 信息增益 / 特征内在信息 IV"""
 n = sum(parent)
 g, _ = info_gain(parent, splits)
 iv = entropy([sum(s) for s in splits]) # 特征取值的分布熵
 return g / iv if iv > 0 else 0.0

if __name__ == "__main__":
 print("=== 信息熵三个经典例 ===")
 print("H(1/3,1/3,1/3) =", round(entropy([1, 1, 1]), 4)) # 1.5849 (nats)
 print("H(1,2,7)/10 =", round(entropy([1, 2, 7]), 4)) # 1.1568
 print("H(1,0,0) =", round(entropy([1, 0, 0]), 4)) # 0.0

 print("\n=== 6 样本例：特征 a 的信息增益与增益率 ===")
 parent = [3, 3] # 3 个 A、3 个 B
 print("H(D) =", round(entropy(parent), 4)) # 1.0
 print("H(D|a) =", round(info_gain(parent, [[3, 1], [0, 2]])[1], 4)) # 0.5409
 g_a = info_gain(parent, [[3, 1], [0, 2]])[0]
 print("g(D,a) =", round(g_a, 4), " GainRatio(a) =", round(gain_ratio(parent, [[3, 1], [0, 2]]), 4))
 g_b = info_gain(parent, [[1, 0]] * 6)[0]
 print("g(D,b) =", round(g_b, 4), " GainRatio(b) =", round(gain_ratio(parent, [[1, 0]] * 6), 4))

 print("\n=== 客户流失例：15 样本（5 正 / 10 负）===")
 print("H(D) =", round(entropy([5, 10]), 4)) # 0.9183

 print("\n=== 贷款数据：基尼指数 ===")
 print("Gini(3/10, 7/10 加权后) 是否有房 =",
 round(3 / 10 * gini([3, 0]) + 7 / 10 * gini([4, 3]), 4)) # 0.3429
 print("Gini 婚姻(maried|其他) =",
 round(4 / 10 * gini([4, 0]) + 6 / 10 * gini([3, 3]), 4)) # 0.3
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/05-决策树.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写不纯度指标（验证公式）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/05-决策树.md)
