---
article_id: kp-424144ade9bb3b3a
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 7
learning_objective: 理解并验证：Multi-Head Attention
---

# Multi-Head Attention

> **学习目标**：能够解释「Multi-Head Attention」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

单个头只输出一个加权平均，表达力有限；多头**在多个低维子空间并行做注意力，再拼接融合**：

$$\text{head}_i = \text{Attention}(QW_Q^{(i)}, KW_K^{(i)}, VW_V^{(i)}),\qquad \text{MHA} = \text{Concat}(\text{head}_1,\dots,\text{head}_h)W_O$$

其中 $W_Q^{(i)} \in \mathbb{R}^{d_{model}\times d_{head}}$，$d_{head} = d_{model}/h$。实现上不真的存 $h$ 个小矩阵，而是用一个大矩阵算完再 reshape 拆头——数学等价，但能吃满 GEMM 吞吐。

**多头为什么有效**：不同头学到不同的关系模式，经验上会出现"前一个词头"（attend 到 $t-1$）、"句法头"（主谓/动宾）、"指代头"（代词到先行词）、"分隔符头"（关注 `[SEP]`）。单个头被 $d_{head}$ 限死，只能表达一种相似度；$h$ 个头等于给了模型 $h$ 组不同的"提问方式"。

**$d_{model} = h\times d_{head}$ 是工程约定而非数学约束**——拆头是从一个大投影里切出来的，所以必须整除。常见配置：

| 模型 | $d_{model}$ | $h$ | $d_{head}$ | 备注 |
| --- | --- | --- | --- | --- |
| Transformer base (2017) | 512 | 8 | 64 | 经典配置 |
| GPT-3 175B | 12288 | 96 | 128 | $d_{head}$ 固定 128 |
| LLaMA-2 7B | 4096 | 32 | 128 | 全 MHA（32 个 KV 头） |
| LLaMA-2 70B | 8192 | 64 | 128 | GQA，只有 8 个 KV 头 |

$d_{head}$ 通常固定在 64~128：太小则低维点积噪声大、且注意力矩阵显存随 $h$ 线性增长；太大则头数不足、子空间多样性下降。

**numpy 实现（含因果掩码）**：

```python
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x); return e / e.sum(axis=axis, keepdims=True)

    class MultiHeadSelfAttention:
        def __init__(self, d_model, num_heads, rng):
            assert d_model % num_heads == 0, "d_model 必须能被 num_heads 整除"
            self.h, self.d_head = num_heads, d_model // num_heads
            s = 1.0 / np.sqrt(d_model) # 简化的初始化
            self.Wq, self.Wk, self.Wv, self.Wo = (
            rng.standard_normal((d_model, d_model)) * s for _ in range(4))

            def _split_heads(self, x): # [B,n,d] -> [B,h,n,d_head]
                B, n, _ = x.shape
                return x.reshape(B, n, self.h, self.d_head).transpose(0, 2, 1, 3)

            def _merge_heads(self, x): # [B,h,n,d_head] -> [B,n,d]
                B, h, n, d_head = x.shape
                return x.transpose(0, 2, 1, 3).reshape(B, n, h * d_head)

            def forward(self, x, causal=True):
                B, n, _ = x.shape
                Q, K, V = (self._split_heads(x @ W) for W in (self.Wq, self.Wk, self.Wv))
                scores = Q @ K.swapaxes(-1, -2) / np.sqrt(self.d_head) # [B,h,n,n]
                if causal:
                    allow = np.tril(np.ones((n, n), dtype=bool)) # 下三角(含对角)可见
                    scores = np.where(allow, scores, -np.inf)
                    weights = softmax(scores, axis=-1)
                    return self._merge_heads(weights @ V) @ self.Wo, weights

                rng = np.random.default_rng(0)
                B, n, d_model, h = 2, 6, 16, 4
                x = rng.standard_normal((B, n, d_model))
                mha = MultiHeadSelfAttention(d_model, h, rng)
                y, w = mha.forward(x, causal=True)
                print("out", y.shape, "weights", w.shape)
                print("上三角全为 0:", np.allclose(np.triu(w[0, 0], k=1), 0.0))
```

输出 `out (2, 6, 16) weights (2, 4, 6, 6)` 与 `上三角全为 0: True`。注意 `weights` 形状是 `[B,h,n,n]`——**每个头都有自己独立的注意力矩阵**，算显存时最容易漏掉这一点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Multi-Head Attention」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
