---
article_id: kp-70da5b0045052f49
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 11
learning_objective: 理解并验证：手写 sigmoid 与损失函数（验证推导）
---

# 手写 sigmoid 与损失函数（验证推导）

> **学习目标**：能够解释「手写 sigmoid 与损失函数（验证推导）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""手写 sigmoid、交叉熵损失，验证 2.1~2.4 的推导"""
import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def log_loss(y, p):
    """交叉熵损失（对数似然损失的均值形式）"""
    eps = 1e-12 # 防止 log(0)
    p = np.clip(p, eps, 1 - eps)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))


if __name__ == "__main__":
    # 1. sigmoid 关键取值
    for z in [-5, -1, 0, 1, 5]:
        print(f"sigma({z:2d}) = {sigmoid(z):.6f}")
        print("sigma(-z) + sigma(z) =", sigmoid(-1.3) + sigmoid(1.3)) # 1.0

        # 2. 验证导数公式 sigma' = sigma(1-sigma)（数值微分对照）
        z0, h = 0.7, 1e-6
        num = (sigmoid(z0 + h) - sigmoid(z0 - h)) / (2 * h)
        ana = sigmoid(z0) * (1 - sigmoid(z0))
        print(f"数值导数={num:.8f} 解析导数={ana:.8f}")

        # 3. 损失函数行为：y=1 时 p 越大损失越小
        y1 = np.array([1.0, 1.0, 1.0])
        print("y=1, p=[0.1,0.5,0.9] -> loss =",
        [round(log_loss(y1[i:i + 1], np.array([p])), 4)
        for i, p in enumerate([0.1, 0.5, 0.9])])
        # y=0 时 p 越小损失越小
        y0 = np.array([0.0, 0.0, 0.0])
        print("y=0, p=[0.1,0.5,0.9] -> loss =",
        [round(log_loss(y0[i:i + 1], np.array([p])), 4)
        for i, p in enumerate([0.1, 0.5, 0.9])])

        # 4. 课程示例的逐样本损失（真实 y=[1,0,1]，预测 p=[0.4,0.6,0.41]）
        y = np.array([1.0, 0.0, 1.0])
        p = np.array([0.4, 0.6, 0.41])
        per_sample = -(y * np.log(p) + (1 - y) * np.log(1 - p))
        print("逐样本损失:", np.round(per_sample, 4), " 总计:", round(per_sample.sum(), 4))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写 sigmoid 与损失函数（验证推导）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
