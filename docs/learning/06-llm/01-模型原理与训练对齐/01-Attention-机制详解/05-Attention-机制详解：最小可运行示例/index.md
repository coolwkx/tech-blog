---
article_id: kp-8bd9481b74beccc7
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 4
learning_objective: 理解并验证：Attention 机制详解：最小可运行示例
---

# Attention 机制详解：最小可运行示例

> **学习目标**：能够解释「Attention 机制详解：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 最小可运行示例

## 本次只学这一点

```python
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True) # 减最大值：数学等价，数值救命
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-1, -2) / np.sqrt(d_k) # [.., n, n] 相关度
    if mask is not None: # True=保留, False=屏蔽
        scores = np.where(mask, scores, -np.inf)
        weights = softmax(scores, axis=-1) # [.., n, n] 每行和=1
        return weights @ V, weights # [.., n, d_k], [.., n, n]

    rng = np.random.default_rng(0)
    Q, K, V = (rng.standard_normal((2, 4, 8)) for _ in range(3))
    out, w = attention(Q, K, V)
    print(out.shape, w.shape, w.sum(-1))
```

输出 `(2, 4, 8) (2, 4, 4)`，且 `w.sum(-1)` 全为 1。

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `x - x.max(...)` | softmax 防溢出 | 不是近似而是恒等变换（分子分母同乘 $e^{-m}$）；不减最大值会出现 `exp(89)=inf`（float32）导致 `nan` |
| `Q @ K.swapaxes(-1,-2)` | 算所有位置对的相关度 | 用 `swapaxes` 而非 `.T`，才能同时支持 3D/4D 批量输入 |
| `/ np.sqrt(d_k)` | 缩放，把 logit 方差控制在 1 | 除的是 $\sqrt{d_k}$ 不是 $d_k$，原因见 4.1 |
| `np.where(mask, scores, -inf)` | 掩码：不许看的位置打成 $-\infty$ | 必须在 softmax **之前**；放在之后等于破坏归一化 |
| `softmax(..., -1)` | 在**最后一维（key 维）**归一化 | 归一化轴是 key 轴，不是 query 轴 |
| `weights @ V` | 加权聚合 | 权重乘的是 $V$，不是 $K$ |
| 返回 `weights` | 便于调试 | 生产代码别返回，否则 $n^2$ 矩阵一直占显存 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Attention 机制详解：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
