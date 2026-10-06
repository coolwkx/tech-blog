---
article_id: kp-84ff05d7d4b46d16
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 13
learning_objective: 理解并验证：用 NumPy 从零实现缩放点积注意力与多头注意力
---

# 用 NumPy 从零实现缩放点积注意力与多头注意力

> **学习目标**：能够解释「用 NumPy 从零实现缩放点积注意力与多头注意力」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 可运行示例

## 本次只学这一点

```python
import numpy as np

np.random.seed(0)


def softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True)) # 减最大值，防止溢出
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """Q: (..., n_q, d_k) K: (..., n_k, d_k) V: (..., n_k, d_v)"""
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-2, -1) / np.sqrt(d_k) # (..., n_q, n_k)
    if mask is not None:
        scores = np.where(mask, scores, -1e9) # 屏蔽位置给极小值
        return softmax(scores, axis=-1) @ V, scores


    def multi_head_attention(X, n_heads, mask=None):
        """X: (n, d_model) -> 输出 (n, d_model)"""
        n, d_model = X.shape
        assert d_model % n_heads == 0, "d_model 必须能被 n_heads 整除"
        d_k = d_model // n_heads

        W = np.random.randn(d_model, 3 * d_model) * 0.02 # 可学习投影的替身
        QKV = X @ W # (n, 3*d_model)
        Q, K, V = np.split(QKV, 3, axis=-1)

        def split(t): # (n, d_model) -> (n_heads, n, d_k)
            return t.reshape(n, n_heads, d_k).transpose(1, 0, 2)

        Q, K, V = split(Q), split(K), split(V)
        out, scores = scaled_dot_product_attention(Q, K, V, mask) # (n_heads, n, d_k)
        out = out.transpose(1, 0, 2).reshape(n, d_model) # 拼接多头
        return out, scores


    n, d_model, n_heads = 4, 8, 2
    X = np.random.randn(n, d_model)
    causal = np.tril(np.ones((n, n), dtype=bool)) # 位置 i 只能看到 j <= i
    out, scores = multi_head_attention(X, n_heads, mask=causal)

    print("输入 X 形状 :", X.shape)
    print("注意力分数形状 :", scores.shape, "= (n_heads, n_q, n_k)")
    print("输出形状 :", out.shape)
    print("第 0 个头的分数矩阵 :\n", np.round(scores[0], 3))
```

**要观察的三件事**：① `scores` 的形状是 `(n_heads, n_q, n_k)`，说明每个头各自有一张注意力矩阵；
② 因果 mask 下，第 $i$ 行只在 $j\le i$ 的位置有权重；③ 去掉 `/ np.sqrt(d_k)` 后分数绝对值会明显变大，
softmax 输出会更「尖锐」甚至饱和——这就是缩放的作用。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 NumPy 从零实现缩放点积注意力与多头注意力」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
