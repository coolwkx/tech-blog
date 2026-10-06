---
article_id: kp-691d4330760c8f2c
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 5
learning_objective: 理解并验证：为什么必须除以 $\sqrt{d_k}$
---

# 为什么必须除以 $\sqrt{d_k}$

> **学习目标**：能够解释「为什么必须除以 $\sqrt{d_k}$」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

**第一步：点积的方差等于 $d_k$。** 设 $q,k \in \mathbb{R}^{d_k}$ 各分量独立、均值 0、方差 1，则 $s = q\cdot k = \sum_{i=1}^{d_k} q_i k_i$，由独立性：

$$\mathbb{E}[s] = \sum_i \mathbb{E}[q_i]\mathbb{E}[k_i] = 0,\qquad
\operatorname{Var}(s) = \sum_{i=1}^{d_k}\operatorname{Var}(q_ik_i) = \sum_{i=1}^{d_k}\mathbb{E}[q_i^2]\mathbb{E}[k_i^2] = d_k$$

推导**不依赖高斯假设**，只需独立、零均值、单位方差。故标准差为 $\sqrt{d_k}$；除以 $\sqrt{d_k}$ 后 logit 方差恰好回到 1。

**第二步：logit 尺度变大则 softmax 饱和、梯度消失。** softmax 的 Jacobian 为 $J = \operatorname{diag}(p) - pp^\top$，其特征值之和

$$\operatorname{tr}(J) = \sum_i p_i(1-p_i) = 1 - \sum_i p_i^2$$

是**与上游梯度取值无关**的无量纲"梯度流通能力"指标：$p$ 均匀时 $\sum p_i^2 \to 1/n$、$\operatorname{tr}(J)\to1-1/n$ 取最大；$p$ 退化成 one-hot 时 $\sum p_i^2\to1$、$\operatorname{tr}(J)\to0$，梯度彻底消失。具体到数值：$d_k=64$ 时 $\sqrt{d_k}=8$，logit 标准差为 8、极差约 $\pm3\sigma=\pm24$，两个 logit 相差 24 意味着概率比 $e^{24}\approx2.6\times10^{10}$——softmax 事实上变成了 argmax。

**第三步：数值实验验证。**

```python
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x); return e / e.sum(axis=axis, keepdims=True)

    rng = np.random.default_rng(42)
    n, trials = 1024, 300

    print("A) Var(q.k), q_i,k_i ~ N(0,1) i.i.d.")
    for d in [16, 64, 256, 1024]:
        q = rng.standard_normal((20000, d)); k = rng.standard_normal((20000, d))
        s = (q * k).sum(1)
        print(f" d_k={d:5d} Var={s.var:8.2f} std={s.std:7.3f} sqrt(d_k)={np.sqrt(d):7.3f}")

        # tr(J) = 1 - sum(p^2) 是 softmax Jacobian 特征值之和，衡量"还能有多少梯度流过"
        print("B) 缩放对 softmax 饱和的影响")
        print(f" {'d_k':>5} {'scale':>11} {'logit_std':>10} {'max_p':>8} {'entropy':>8} {'tr(J)':>8}")
        for d in [16, 64, 128, 256, 1024]:
            for name, div in [("1", 1.0), ("1/sqrt(d_k)", np.sqrt(d))]:
                st, mp, en, tr = [], [], [], []
                for _ in range(trials):
                    z = (rng.standard_normal(d) @ rng.standard_normal((n, d)).T) / div
                    p = softmax(z)
                    st.append(z.std); mp.append(p.max)
                    en.append(-(p * np.log(p + 1e-300)).sum); tr.append(1 - (p ** 2).sum)
                    print(f" {d:5d} {name:>11} {np.mean(st):10.2f} {np.mean(mp):8.4f} "
                    f"{np.mean(en):8.3f} {np.mean(tr):8.4f}")
```

实测输出（$n=1024$，300 次试验平均）整理为两张表：

**表 A：点积方差随 $d_k$ 线性增长**

| $d_k$ | 实测 $\operatorname{Var}(q\cdot k)$ | 实测标准差 | $\sqrt{d_k}$ |
| --- | --- | --- | --- |
| 16 | 16.07 | 4.008 | 4.000 |
| 64 | 64.09 | 8.005 | 8.000 |
| 256 | 253.27 | 15.914 | 16.000 |
| 1024 | 1004.33 | 31.691 | 32.000 |

**表 B：缩放与否对 softmax 的影响**

| $d_k$ | scale | logit_std | max_p | entropy | $\operatorname{tr}(J)=1-\sum p^2$ |
| --- | --- | --- | --- | --- | --- |
| 16 | 1 | 3.89 | 0.3965 | 2.592 | 0.7537 |
| 64 | 1 | 7.89 | 0.6985 | 0.937 | 0.4122 |
| 256 | 1 | 16.01 | 0.8595 | 0.381 | 0.1994 |
| 1024 | 1 | 31.82 | 0.9193 | 0.200 | 0.1139 |
| 16 | $1/\sqrt{d_k}$ | 0.98 | 0.0164 | 6.436 | **0.9972** |
| 64 | $1/\sqrt{d_k}$ | 0.99 | 0.0152 | 6.441 | **0.9974** |
| 256 | $1/\sqrt{d_k}$ | 1.00 | 0.0161 | 6.435 | **0.9974** |
| 1024 | $1/\sqrt{d_k}$ | 1.00 | 0.0167 | 6.432 | **0.9974** |

不缩放时，$d_k$ 从 16 涨到 1024，$\operatorname{tr}(J)$ 从 0.754 掉到 0.114——**梯度流通能力损失约 85%**，且 $d_k$ 越大越糟，等于把 $d_k$ 变成了隐式的训练难度旋钮。除以 $\sqrt{d_k}$ 后，无论 $d_k$ 多大 logit_std 恒为 ~1.00、$\operatorname{tr}(J)$ 恒为 ~0.9974（上界 $1-1/1024=0.999023$），熵也逼近上限 $\ln 1024=6.931$。**缩放让 $d_k$ 变成对训练动态中性的超参数。**

**第四步：为什么不是除以 $d_k$？** 那会把 logit 方差压成 $1/d_k$：$d_k=256$ 时标准差仅 $1/16=0.0625$，输出几乎完全均匀（$p_i\approx1/n$），注意力退化成"对所有位置的 $V$ 求算术平均"，模型丧失选择能力——梯度不消失，但**信号被抹平了**，同样学不到东西。$\sqrt{d_k}$ 是唯一让 logits 方差保持 $O(1)$ 的指数。工程上等价写法是把缩放乘到 $Q$ 上（$Q/\sqrt{d_k}$），省掉每步除法。

> 这是理想化分析（假设各分量独立同分布）；真实模型里 q、k 方差会偏移，"语义匹配"的 q·k 还有正偏置。因此现代模型会叠加 **QK-Norm**（对 q、k 做 LayerNorm）进一步稳定 logits，属同一动机的工程加固。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么必须除以 $\sqrt{d_k}$」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
