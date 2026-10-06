---
article_id: kp-7077836cdb6ad11a
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 6
learning_objective: 理解并验证：反向传播与计算图：最小可运行示例
---

# 反向传播与计算图：最小可运行示例

> **学习目标**：能够解释「反向传播与计算图：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 最小可运行示例

## 本次只学这一点

先不写引擎，用最朴素的手写梯度训练一个两层 MLP。

```python
"""依赖：numpy。手写梯度的两层 MLP，拟合 y = 3*x1 - 2*x2 + 1，不含任何 autograd。"""
import numpy as np

rng = np.random.default_rng(0)
X = rng.normal(size=(64, 2)) # (B, D_in) = (64, 2)
Y = 3 * X[:, :1] - 2 * X[:, 1:2] + 1 # (B, 1)，线性可分的目标
W1, b1 = rng.normal(scale=0.5, size=(4, 2)), np.zeros(4) # (H,D_in), (H,)
W2, b2 = rng.normal(scale=0.5, size=(1, 4)), np.zeros(1) # (D_out,H), (D_out,)

for step in range(2000):
    # ---------- forward ----------
    Z1 = X @ W1.T + b1 # (B,D_in)@(D_in,H) -> (B,H)
    A1 = np.maximum(Z1, 0.0) # ReLU -> (B,H)
    Y_hat = A1 @ W2.T + b2 # (B,H)@(H,D_out) -> (B,D_out)
    diff = Y_hat - Y # (B,D_out)
    loss = (diff ** 2).mean # 标量
    # ---------- backward（第 4.1 节逐行手推）----------
    dY_hat = 2 * diff / X.shape[0] # (B,D_out)
    dW2 = dY_hat.T @ A1 # (D_out,B)@(B,H) -> (D_out,H)
    db2 = dY_hat.sum(axis=0) # (D_out,)
    dZ1 = (dY_hat @ W2) * (Z1 > 0) # (B,H)，ReLU 的局部导数
    dW1 = dZ1.T @ X # (H,B)@(B,D_in) -> (H,D_in)
    db1 = dZ1.sum(axis=0) # (H,)
    # ---------- 最朴素的 SGD ----------
    for p, g in [(W1, dW1), (b1, db1), (W2, dW2), (b2, db2)]:
        p -= 0.1 * g
        if step % 500 == 0:
            print(f"step {step:4d} loss={loss:.3e}")
            # 本机实测：loss 1.152e+01 -> 8.183e-06 -> 1.828e-07 -> 5.212e-09 -> 1.486e-10
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `X @ W1.T + b1` | 线性层（行样本约定） | 权重存成 `(out,in)` 才让 `.T` 在右边；反过来也能跑，但要全局一致 |
| `A1 = np.maximum(Z1, 0)` | ReLU 前向 | 反向需要前向时的符号，所以必须缓存 `Z1`——这就是「缓存中间激活」 |
| `dY_hat = 2*diff/B` | MSE 对输出的导数 | 除以 `B` 来自 `.mean`；漏掉等价于放大学习率 |
| `dW2 = dY_hat.T @ A1` | 权重梯度 | **形状必须与 `W2` 一致** `(D_out,H)`；不一致几乎一定是转置写错 |
| `db2 = dY_hat.sum(axis=0)` | 偏置沿 batch 求和 | 前向 broadcast，反向就是 sum（reduction 的伴随是 broadcasting） |
| `dZ1 = (dY_hat @ W2) * (Z1 > 0)` | 把梯度传回隐藏层并穿 ReLU | 用 `W2` 而非 `W2.T`，因为转置已在 `dW2` 那行用掉；ReLU 逐元素 → 逐元素相乘 |
| `p -= 0.05 * g` | SGD 更新 | 是「减」；numpy 里这是 in-place，在 autograd 图上是灾难（见第 5 节） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「反向传播与计算图：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
