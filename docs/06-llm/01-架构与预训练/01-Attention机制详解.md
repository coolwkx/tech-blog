# Attention 机制详解

> **一句话总结**：Attention 用「查询-键-值」的软寻址取代循环结构，把序列建模的最长路径从 $O(n)$ 压到 $O(1)$，代价是 $O(n^2)$ 的时间与显存——理解这个代价如何在长上下文和推理解码中被放大，是理解整个大模型工程的地基。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](README.md)。
>
> **学完能做到**：1) 从方差出发推导 $\sqrt{d_k}$ 的来历，并用数值实验证明不缩放会让 softmax 饱和、梯度消失；2) 手写 numpy 版缩放点积注意力与带因果掩码的多头注意力，说清每一步的形状流转；3) 独立估算任意模型、任意上下文长度与 batch 下的 KV cache 显存，并说明 MQA/GQA/FlashAttention 各自省的是什么。

---

## 1. 为什么需要它

### 1.1 RNN 的两个瓶颈

Attention 之前序列建模的主流是 RNN/LSTM，它有三个结构性缺陷：

- **串行计算**：$h_t = f(h_{t-1}, x_t)$，第 $t$ 步必须等第 $t-1$ 步，时间维无法并行，GPU 大量空转；反向传播路径长度 $O(n)$，长序列上梯度连乘 $n$ 次，消失/爆炸几乎必然。
- **固定长度瓶颈**：无论序列多长，整段历史都被压进固定维度的 $h_t \in \mathbb{R}^d$。这是有损压缩——第 3 个 token 的细节和第 500 个 token 的内容挤在同一个向量里，还要穿过几百次非线性变换才能读回。
- **位置与内容耦合**：顺序和内容混在同一隐状态中，无法显式建模"第 5 个词与第 200 个词的关系"。

### 1.2 注意力是一种「可学习的软寻址」

读序列本质上是"给定当前需求，去历史里取相关信息"，即一次**寻址**：**Query** 是"我现在想要什么"，**Key** 是"每条历史信息对外宣称自己是什么"，**Value** 是"它真正携带的内容"。

硬寻址（argmax 选一个位置）不可导，无法用梯度下降学习。Attention 的破局点是**用 softmax 把 argmax 松弛成加权平均**：不再"选一个"，而是"按相关度加权地全取一遍"。处处可导，寻址策略就能端到端训练。代价随之埋下：既然要和**每一个**位置算相关度，就需要 $n \times n$ 的相关度矩阵。

### 1.3 三种序列层的复杂度对比

这正是原论文 Table 1 的核心：

| 层类型 | 每层复杂度 | 顺序操作数 | 最长路径长度 |
| --- | --- | --- | --- |
| 自注意力 Self-Attention | $O(n^2 \cdot d)$ | $O(1)$ | $O(1)$ |
| 循环 Recurrent | $O(n \cdot d^2)$ | $O(n)$ | $O(n)$ |
| 卷积 Convolutional | $O(k \cdot n \cdot d^2)$ | $O(1)$ | $O(\log_k n)$ |

自注意力用 $O(n^2)$ 时间换来 $O(1)$ 路径长度与完全并行，**当 $n < d$ 时它甚至比 RNN 更便宜**——这是 Transformer 在 2017 年能赢的算术基础；而 $n$ 从 512 涨到 20 万时 $n^2$ 涨了 15 万倍，这就是长上下文成为当今主要矛盾的原因。

---

## 2. 核心思想

一句话：**用两次矩阵乘法换取全序列的两两交互。**

$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

$QK^\top$ 得到相关度打分，softmax 把它变成每行和为 1 的分布，再乘 $V$ 就是按概率取值的加权平均。

### 2.1 Q/K/V 与多头拆分的形状流转

```text
x : [B, n, d_model] B=batch, n=序列长度, d_model=隐藏维度
 |-- x@Wq -> Q : [B,n,d_model] --|
 |-- x@Wk -> K : [B,n,d_model] --| 三者同源 => "自"注意力
 |-- x@Wv -> V : [B,n,d_model] --|
 | reshape(B,n,h,d_head).transpose(0,2,1,3) 拆头
 v
 Q,K,V : [B, h, n, d_head] h = 头数, d_head = d_model / h
 | scores = Q @ K^T / sqrt(d_head)
 v
 scores : [B, h, n, n] 每个头一张 n×n 相关度矩阵
 | causal mask: 下三角(含对角)保留, 右上角置 -inf
 v
 P = softmax(scores, axis=-1) : [B, h, n, n] 每行和 = 1
 | ctx = P @ V
 v
 ctx : [B, h, n, d_head]
 | transpose(0,2,1,3).reshape(B, n, h*d_head) 拼头, h*d_head == d_model
 v
 ctx : [B, n, d_model] --@Wo--> out : [B, n, d_model] 输出投影融合各头
```

**记住三个形状就能读懂所有注意力代码**：

| 张量 | 形状 | 含义 |
| --- | --- | --- |
| $Q,K,V$ | `[B, h, n, d_head]` | 拆头后，每个头独立算注意力 |
| scores / $P$ | `[B, h, n, n]` | 每个头一张 $n\times n$ 矩阵，**显存杀手** |
| out | `[B, n, d_model]` | 拼接并投影回输入维度，可残差相加 |

---

## 3. 最小可运行示例

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

---

## 4. 深入机制

### 4.1 为什么必须除以 $\sqrt{d_k}$

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

### 4.2 Q/K/V 的语义与来源

$Q = XW_Q,\ K = XW_K,\ V = XW_V$，其中 $X \in \mathbb{R}^{n\times d_{model}}$，三个权重矩阵均为 $d_{model}\times d_{model}$。$W_Q,W_K$ 决定"什么算相关"，定义了一个可学习的**双线性相似度** $x_i^\top W_QW_K^\top x_j$；$W_V$ 决定"被关注后传递什么"。**相关度与传递内容的解耦**正是 Attention 强于"用相似度直接加权原始输入"之处——可以高相关但不传递信息，也可以低相关但传递关键信息。

**"自"注意力**指 $Q,K,V$ 全部来自同一个 $X$，序列自己关注自己；对比 **cross-attention**：$Q$ 来自解码器（或文本），$K,V$ 来自编码器输出（或图像），此时 $n_q \neq n_k$。

| 类型 | Q 来源 | K/V 来源 | scores 形状 | 典型场景 |
| --- | --- | --- | --- | --- |
| self-attention | $X$ | $X$ | $[B,h,n,n]$ | GPT/LLaMA 每一层 |
| cross-attention | 解码器状态 | 编码器输出 | $[B,h,n_q,n_k]$ | 翻译、Stable Diffusion 文本条件 |
| causal self-attention | $X$ | $X$（加掩码） | $[B,h,n,n]$，上三角置 $-\infty$ | 自回归语言模型 |

### 4.3 Multi-Head Attention

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

### 4.4 掩码：padding mask 与 causal mask

两种掩码目的不同，机制相同：**在 softmax 之前把不许看的位置的 logit 置为 $-\infty$，使 $e^{-\infty}=0$**。

| 维度 | padding mask | causal mask |
| --- | --- | --- |
| 目的 | 忽略补齐的无效 token | 防止看到未来 token（自回归） |
| 形状 | `[B, 1, 1, n]`（key 维） | `[1, 1, n, n]`（下三角） |
| 内容 | 真实 token 位 True，`<pad>` 位 False | 位置 $j \le i$ 为 True，其余 False |
| 随样本变化 | 是（每个样本 padding 位置不同） | 否（与数据无关，全局固定） |
| 用在哪 | 训练 + batch 推理（左侧 padding） | 只用在做 next-token prediction 的解码器 |
| 能否广播合并 | 可以：`mask = causal & padding`，形状 `[B,1,n,n]` | 同左 |

**$-\infty$ 的作用与数值稳定性**：(1) 过 softmax 后**精确等于 0**（$e^{-\infty}=0$），不是"很小的数"；用 `-1e9` 这类有限大负数会残留 $10^{-9}$ 级权重，语义上是近似。(2) 减最大值技巧让 $-\infty$ 也安全：$-\infty-m=-\infty$，$e^{-\infty}=0$，不会出 `nan`。(3) **真正的坑是整行全被屏蔽**——padding 与 causal 组合不当会让某行全为 $-\infty$，softmax 变成 $0/0=$ `nan`，并通过反向传播污染整个 batch。(4) **fp16 下不要用 `-1e9`**：它超出 fp16 上限 65504 会溢出成 `-inf`，而 `-inf-(-\inf)=$ `nan`；安全下界是 `torch.finfo(torch.float16).min = -65504.0`。

### 4.5 复杂度分析

设单层、batch $B$、序列长 $n$、隐藏维 $d$（$d_{model}$）、头数 $h$、$d_{head}=d/h$；约定一次乘加算 2 FLOPs。

| 组件 | 时间（FLOPs） | 中间显存 | 参数量 |
| --- | --- | --- | --- |
| $QK^\top$ | $2n^2d$ | $B\cdot h\cdot n^2$ 元素 | 0 |
| softmax | $\approx 5n^2hB$ | 原地（可复用） | 0 |
| $PV$ | $2n^2d$ | — | 0 |
| **注意力核心合计** | $\mathbf{4n^2d}=O(n^2d)$ | $\mathbf{O(Bhn^2)}$，**正比于 $n^2$** | 0 |
| QKVO 投影 | $8nd^2=O(nd^2)$ | $O(Bnd)$ | $4d^2$ |
| FFN（SwiGLU，$d_{ff}\approx\frac{8}{3}d$） | $\approx 16nd^2$ | $O(Bnd_{ff})$ | $3d\,d_{ff}$ |

四个关键结论：

1. **时间 $O(n^2d)$**：注意力核心与 $n^2$ 成正比，与 $d$ 线性。
2. **显存 $O(n^2)$**：指注意力矩阵本身，$B\times h\times n\times n$ 个元素。7B（$L=32,h=32$，fp16）在 $n=4096$ 时**单层** scores 就是 $32\times4096^2\times2=1\ \text{GiB}$。标准实现要显式写出它（写回 HBM、读回来 softmax、再写回），这正是 FlashAttention 要解决的问题。
3. **参数量 $4d^2$**：Q/K/V/O 四个 $d\times d$ 矩阵。7B 的注意力参数 $32\times4\times4096^2=2.15\times10^9$，约占 1/3（其余主要是 FFN）。
4. **存在交叉点**：令 $4n^2d=8nd^2$ 得 $n=2d$。7B 的 $d=4096$，即 **$n\approx8192$ 时注意力核心 FLOPs 追平四个投影之和**。

**长上下文为什么代价爆炸**（7B：$L=32$，$d=4096$，$d_{ff}=11008$，$N\approx6.5\times10^9$）：

| 序列长度 $n$ | 注意力核心 FLOPs（32 层） | 前向总 FLOPs | 注意力占比 |
| --- | --- | --- | --- |
| 4096 | $8.8\times10^{12}$ | $6.2\times10^{13}$ | 14% |
| 8192 | $3.5\times10^{13}$ | $1.4\times10^{14}$ | 25% |
| 32768 | $5.6\times10^{14}$ | $9.9\times10^{14}$ | **57%** |

计算过程（$n=32768$）：单层注意力核心 $4n^2d=4\times32768^2\times4096=1.76\times10^{13}$，乘 32 层得 $5.6\times10^{14}$；线性部分（投影 + FFN）$=2Nn=2\times6.5\times10^9\times32768=4.3\times10^{14}$；合计 $9.9\times10^{14}$。

$n$ 从 4096 到 32768 只涨了 8 倍，注意力 FLOPs 却涨了 **64 倍**，占比从 14% 升到 57%。**这就是长上下文的第一性成本来源**：不是模型变大，而是 $n^2$ 项开始主导。

### 4.6 KV Cache

**推理解码与训练是两种完全不同的负载。** 自回归生成第 $t$ 个 token 时，需要当前 token 的 $q_t$ 与所有历史 token 的 $k_{1..t},v_{1..t}$ 做注意力。关键观察：

> 第 $t$ 步的 $K,V$ 中，前 $t-1$ 个位置的值**与上一步算出的完全相同**。

因为因果掩码保证位置 $j$ 的 $k_j,v_j$ 只依赖 $x_{1..j}$，不会因后面新增 token 而改变，所以**只需缓存 K 和 V，逐步追加**。

**为什么不缓存 Q？** $q_t$ 只用于当前这一步、用完即弃，下一步需要的是由新 token 生成的 $q_{t+1}$。Q 是一次性查询，K/V 是可复用数据库。

| 方案 | 第 $t$ 步成本 | 累计成本 | 说明 |
| --- | --- | --- | --- |
| 无 cache | $O(t^2d)$ | $\sum_{t=1}^{n}O(t^2d)=O(n^3d)$ | 每步重算整个前缀的注意力 |
| 有 cache | $O(nd+d^2)$ | $\sum_{t=1}^{n}O(nd)=O(n^2d)$ | 只算新 $q$ 与全部历史 $k$ 的点积 |

指数从 3 降到 2：$n=4096$ 时无 cache 的累计注意力计算量约为有 cache 的 $n/3\approx1365$ 倍。**KV cache 不是优化技巧，而是可用性的前提。**

代价是显存。**KV cache 显存公式**：

$$\text{bytes} = 2 \times L \times H_{kv} \times d_{head} \times n \times B \times \text{dtype\_bytes}$$

系数 $2$ 是 K 和 V 各一份；$L$ 是层数（每层都有自己的 K/V）；$H_{kv}$ 是 K/V 头数（MHA 时等于 $h$，GQA/MQA 更小）；$H_{kv}\times d_{head}$ 即 KV 投影维度，MHA 时等于 $d_{model}$；$n$ 为已缓存长度；$B$ 为并发 batch。

**7B 模型具体估算**（LLaMA-2-7B 配置：$L=32$，$h=32$，$d_{head}=128$，$d_{model}=4096$，fp16 即 2 bytes）。单 token、单序列：

$$2 \times 32 \times 32 \times 128 \times 1 \times 1 \times 2 = 524{,}288\ \text{bytes} = 512\ \text{KiB} = 0.5\ \text{MiB/token}$$

| 场景 | 计算过程 | KV cache |
| --- | --- | --- |
| $n=4096$, $B=1$ | $524288\times4096$ | **2 GiB** |
| $n=4096$, $B=16$ | $524288\times4096\times16$ | **32 GiB** |
| $n=8192$, $B=16$ | $524288\times8192\times16$ | 64 GiB |
| $n=32768$, $B=1$ | $524288\times32768$ | **16 GiB** |
| $n=131072$, $B=1$ | $524288\times131072$ | 64 GiB |
| $n=4096$, $B=16$（GQA，$H_{kv}=8$） | $524288/4\times4096\times16$ | **8 GiB** |

对照：7B 模型 fp16 权重 $7\times10^9\times2=14\times10^9\ \text{bytes}=13.04\ \text{GiB}$。

**结论**：$n=4096$、并发 16 时 KV cache（32 GiB）是权重（13.04 GiB）的 **2.5 倍**。这就是"**并发数 $\times$ 上下文长度**的乘积才是真正的容量约束"——80GB 的 A100 装下 7B 权重后剩约 67 GiB，$n=4096$ 时理论上只能并发约 33 路。**KV cache 而非权重，才是推理服务吞吐的上限。**

```python
import numpy as np

def softmax(x, axis=-1):
 x = x - x.max(axis=axis, keepdims=True)
 e = np.exp(x); return e / e.sum(axis=axis, keepdims=True)

def kv_bytes(L, H_kv, d_head, n, B=1, dtype_bytes=2):
 """KV cache 显存（字节）。MHA 时 H_kv = 注意力头数；GQA/MQA 时更小。"""
 return 2 * L * H_kv * d_head * n * B * dtype_bytes

def human(x):
 return f"{x/1024**3:.2f} GiB" if x >= 1024**3 else f"{x/1024**2:.1f} MiB"

L, H, d_head = 32, 32, 128 # LLaMA-2-7B 风格
print("单 token (MHA):", human(kv_bytes(L, H, d_head, 1))) # 0.5 MiB
for nn, bs in [(4096, 1), (4096, 16), (8192, 16), (32768, 1), (131072, 1)]:
 print(f" n={nn:6d} B={bs:3d} -> {human(kv_bytes(L, H, d_head, nn, bs))}")
print("单 token (GQA 8 个 KV 头):", human(kv_bytes(L, 8, d_head, 1)), # 128 KiB
 "| 7B 权重 fp16:", human(7e9 * 2)) # 13.04 GiB

# 验证：用 cache 增量计算 与 拿到全部历史后一次算，结果逐位相同
rng = np.random.default_rng(0)
K, V = rng.standard_normal((4, 8)), rng.standard_normal((4, 8))
q_t = rng.standard_normal(8) # 第 4 个位置的 query
full = softmax(q_t @ K.T / np.sqrt(8)) @ V # 一次性全量
Kc, Vc = np.vstack([K[:3], K[3]]), np.vstack([V[:3], V[3]]) # 缓存前 3 步 + append
inc = softmax(q_t @ Kc.T / np.sqrt(8)) @ Vc # 走 cache
print("cache vs full max diff:", np.abs(full - inc).max) # 0.0
```

`max diff: 0.0`——**逐位完全相同，不是近似**。这解释了为什么 KV cache 可以无条件开启（除了显存）。

**prefill 与 decode 的不对称**：

| 阶段 | 并行度 | 瓶颈 | 注意力成本 |
| --- | --- | --- | --- |
| Prefill（处理 prompt） | 高（$n$ 个 token 并行） | 算力 compute-bound | $O(n^2d)$，$n^2$ 项主导 |
| Decode（逐 token 生成） | 极低（每步 1 个 token） | 显存带宽 memory-bound | $O(nd)$ 读 cache，几乎不占总时间 |

decode 每步是"小矩阵 × 大权重"，算力大量闲置，时间几乎全花在把权重和 KV cache 从 HBM 搬进 SRAM。由此得两个工程结论：**提吞吐要增大 batch 来摊薄权重搬运；降延迟要减少每 token 搬运的字节数——这正是量化与 GQA 的价值。**

### 4.7 现代变体

**MQA / GQA（省 KV cache 显存）**

- **MQA (Multi-Query Attention)**：所有 $h$ 个查询头**共享一组** K/V（$H_{kv}=1$），7B 上 KV cache 缩小 32 倍（0.5 MiB/token 降到 16 KiB/token），但质量有损、训练不够稳。
- **GQA (Grouped-Query Attention)**：折中方案，把 $h$ 个查询头分成 $G$ 组，每组共享一组 K/V（$H_{kv}=G$）。LLaMA-2 70B 用 $h=64$、$H_{kv}=8$，缩小 8 倍；还能对已有 MHA 检查点做 mean-pooling 改造，只需约 5% 额外预训练算力。

| 方案 | $H_{kv}$（7B 类比） | 单 token KV cache | 相对 MHA | 质量 |
| --- | --- | --- | --- | --- |
| MHA | 32 | 512 KiB | 1× | 最好 |
| GQA（$G=8$） | 8 | 128 KiB | 1/4 | 接近 MHA |
| MQA | 1 | 16 KiB | 1/32 | 有损，但可接受 |

GQA **只减小 KV 头数，不减少计算量**：查询头仍是 $h$ 个，注意力 FLOPs 不变，省的是显存和显存带宽——恰好命中 decode 的瓶颈。

**滑动窗口 / 稀疏注意力（省 $n^2$）**

- **Sliding Window Attention**：每个位置只看前 $w$ 个 token（Mistral 用 $w=4096$）；层叠后有效感受野为 $L\times w$，但每层成本降到 $O(nw)$。掩码即把 causal 下三角截断成一条带宽 $w$ 的带。
- **稀疏/块稀疏**：Longformer 的"局部窗口 + 少量全局 token"、BigBird 的"局部 + 随机 + 全局"，把 $O(n^2)$ 降到 $O(n)$ 或 $O(n\sqrt{n})$。
- 代价：改变模型表达力，需从头训练、继续预训练或精心设计稀疏模式。

**FlashAttention（不改数学，只改 IO）**

标准实现要把 $n\times n$ 的 scores 写进 HBM、读出来 softmax、写回、再读出来乘 $V$，时间大量浪费在显存搬运而非浮点运算上；7B、$n=4096$、fp16 时单层 scores 就有 1 GiB，而 GPU 每 SM 的 SRAM 只有几百 KB。

FlashAttention 的做法是**分块 + online softmax**：把 $Q$ 切成 $B_r$ 块、$K,V$ 切成 $B_c$ 块，在 SRAM 内逐块计算并累加，永不完整写出 $n\times n$ 矩阵。分块下要正确归一化，需在线维护运行最大值 $m$ 与运行和 $\ell$：

$$m^{new} = \max(m^{old}, \max_j s_j),\qquad
\ell^{new} = e^{m^{old}-m^{new}}\ell^{old} + \sum_j e^{s_j-m^{new}}$$

$$O^{new} = \frac{e^{m^{old}-m^{new}}\ell^{old}O^{old} + \sum_j e^{s_j-m^{new}}v_j}{\ell^{new}}$$

1. **数学上完全等价**，不是近似；输出每位与朴素实现一致（浮点误差 1e-6 量级以内）。
2. **FLOPs 没有减少**（仍是 $O(n^2d)$），省的是 HBM 访存次数，从 $O(n^2)$ 降到接近 $O(n^2/M)$（$M$ 为 SRAM 容量）。在低算术强度的注意力上，这直接换来 2~4 倍实测加速。
3. **显存从 $O(n^2)$ 降到 $O(n)$**，这才让长上下文训练成为可能。

**RoPE 相对位置编码**

注意力本身是**置换等变**的：打乱输入序列，输出只是跟着打乱，模型完全不知道顺序，所以必须注入位置信息。

RoPE 对 $q,k$ 的每一对维度施加**与位置相关的旋转**：把 $d_{head}$ 维分成 $d_{head}/2$ 个二维平面，位置 $m$ 处第 $i$ 个平面的旋转角为 $\theta_i = m\cdot10000^{-2i/d_{head}}$：

$$R_m = \bigoplus_i \begin{pmatrix} \cos(m\theta_i) & -\sin(m\theta_i) \\ \sin(m\theta_i) & \cos(m\theta_i) \end{pmatrix}$$

妙处在于旋转的**相对性**：旋转矩阵正交，故 $\langle R_m q,\ R_n k\rangle = \langle q,\ R_{n-m}k\rangle$，点积只依赖相对距离 $n-m$。位置信息以相对形式自然进入注意力分数，且不增加参数量。这是 LLaMA、Qwen、DeepSeek 系列的基础设施。其他方案：正弦绝对位置编码（原论文，加到输入上，外推差）、可学习位置 embedding（GPT-2，受限于训练长度）、ALiBi（在 scores 上按距离减线性偏置，外推好）、以及多种 RoPE 外推改造（位置插值、NTK-aware scaling、YaRN）。

### 4.8 PyTorch 对照实现

生产代码不要手写，用融合好的算子：

```python
# 依赖: pip install torch (本机验证于 torch 2.11.0+cpu)
import torch
import torch.nn.functional as F

torch.manual_seed(0)
B, h, n, d_head = 2, 4, 6, 8
q = torch.randn(B, h, n, d_head, dtype=torch.float64)
k = torch.randn(B, h, n, d_head, dtype=torch.float64)
v = torch.randn(B, h, n, d_head, dtype=torch.float64)

# 一行搞定：融合实现，自动选 flash / memory-efficient / math 后端
out = F.scaled_dot_product_attention(q, k, v, is_causal=True)

# 手写参照：显式构造因果掩码，验证等价
mask = torch.triu(torch.full((n, n), float("-inf"), dtype=torch.float64), diagonal=1)
p = torch.softmax(q @ k.transpose(-1, -2) / (d_head ** 0.5) + mask, dim=-1)
manual = p @ v

print((out - manual).abs.max.item) # 6.66e-16，仅浮点误差
```

- 输入形状是 **`[B, h, n, d_head]`**，不是 `[B, n, d_model]`；拆头要自己做。
- `is_causal=True` 由算子内部生成掩码，比在外面构造 `[n,n]` 掩码**更省显存**（朴素实现要额外分配 $n^2$ 掩码张量，长序列下本身就很贵）。
- `attn_mask` 与 `is_causal` 可同时传，语义是**叠加**，混用容易出错，建议分开测。
- 用 `torch.nn.attention.sdpa_kernel` 上下文管理器可强制指定后端，用于对比数值与性能。

---

## 5. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| 忘记除以 $\sqrt{d_k}$ | 训练不收敛、loss 卡住，权重近似 one-hot | $d_k$ 大时 logit 方差为 $d_k$，softmax 饱和，$\operatorname{tr}(J)\to0$ | 除以 $\sqrt{d_k}$（或把 $Q$ 预先缩放） |
| 除成 $d_k$ | 能训但效果差，权重几乎均匀 | logit 方差被压到 $1/d_k$，退化为对 $V$ 的算术平均 | 只除 $\sqrt{d_k}$ |
| softmax 前不减最大值 | 出现 `inf`/`nan`，loss 变 `nan` | `exp` 在 float32 下 $x>88.72$、float64 下 $x>709.78$ 溢出 | 先减每行最大值（恒等变换） |
| 归一化轴搞错 | 列和为 1 而非行和为 1，输出尺度被放大 | 应在 **key 维**（最后一维）归一化 | `softmax(scores, axis=-1)` |
| 掩码放在 softmax 之后 | 权重和不为 1，输出尺度改变 | 后置掩码破坏归一化 | 掩码必须在 softmax **之前** |
| 整行被 mask 满 | 输出 `nan`，污染整个 batch 的反向传播 | 该行全 $-\infty$，softmax 为 $0/0$ | 保证每行至少一个可见位，或对全屏蔽行补 0 |
| fp16 里用 `-1e9` 当掩码 | 掩码位变 `-inf`，相减出 `nan` | fp16 上限 65504，`-1e9` 溢出 | 用 `torch.finfo(dtype).min`（fp16 为 `-65504.0`） |
| 右侧 padding 配 causal mask | 生成时输出乱码/漂移 | 右侧 padding 落入部分位置的可见区 | 左 padding，或合并 padding 与 causal mask |
| 推理时忘了 KV cache | 长序列生成慢到不可用 | 每步重算前缀，累计 $O(n^3d)$ | 缓存 K/V，逐步 append |
| 估算显存漏算 KV cache | OOM，并发数远低于预期 | 只算权重，忽略随 $n\times B$ 增长的项 | 用 $2LH_{kv}d_{head}nB\cdot\text{bytes}$ 预估 |
| 估算时漏乘头数 $h$ | 显存估算小了几十倍 | 每个头有独立的 $n\times n$ 矩阵 | 中间显存是 $O(Bhn^2)$ |
| 混淆 `reshape` 与 `transpose` 顺序 | 拆头后语义错乱，但形状正确、不报错 | 必须先 reshape 成 `[B,n,h,d_head]` 再 transpose | `x.reshape(B,n,h,d).transpose(0,2,1,3)` |
| `d_model % h != 0` | 报错或静默截断 | 拆头要求整除 | 显式断言；保证 $d_{model}=h\times d_{head}$ |

---

## 6. 面试问答

**Q1：为什么缩放因子是 $\sqrt{d_k}$，而不是 $d_k$ 或其他值？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

从方差出发。设 $q,k$ 各分量独立、零均值、单位方差，则

$$\operatorname{Var}(s)=\sum_{i=1}^{d_k}\operatorname{Var}(q_ik_i)=\sum_{i=1}^{d_k}\mathbb{E}[q_i^2]\mathbb{E}[k_i^2]=d_k$$

故 $s$ 的标准差为 $\sqrt{d_k}$；除以 $\sqrt{d_k}$ 后 logit 方差回到 1，softmax 处于梯度良好区间。

**不缩放会怎样**：$d_k=256$ 时 logit 标准差是 16，$\operatorname{tr}(J)=1-\sum p_i^2$ 从理论最大 0.999 掉到实测 0.1994（$n=1024$），梯度流通能力损失约 80%；$d_k=1024$ 时只剩 0.1139。分布接近 one-hot，梯度消失。

**为什么不除 $d_k$**：那会把 logit 方差压成 $1/d_k$，$d_k=256$ 时标准差仅 0.0625，输出接近均匀（$p_i\approx1/n$），注意力退化成对所有 $V$ 的算术平均，模型失去选择能力——梯度不消失，但信号被抹平。

**补充**：推导不依赖高斯性；缩放可乘到 $Q$ 上（等价且省一次除法）；这是理想化分析，真实模型 q/k 方差有偏移，所以现代模型会再加 QK-Norm。

</details>

**Q2：注意力权重能当作模型可解释性的证据吗？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

**不能直接当作证据，这是一个有真实争议的问题。**

反对意见（"Attention is not Explanation"）有三类论据：(1) 不同注意力分布可得到相同输出（$V$ 的线性组合有多种权重组合方式），权重不是输出的唯一原因；(2) 可人为替换注意力权重而模型行为几乎不变，说明模型并不"依赖"该分布；(3) 后续层会重新混合信息，第 1 层权重与最终预测之间因果链极长。

支持意见（"Attention is not not Explanation"）：多数情况下注意力分布确实与梯度归因、leave-one-out 高度相关，作为**弱证据**和**调试工具**有价值，完全否定也属过度。

**实践建议**：把注意力权重当"探索性线索"而非"结论"。要做归因，用更可靠的方法交叉验证——**attention rollout**（各层注意力矩阵连乘，考虑残差信息流）、**梯度归因**（input × gradient / integrated gradients）、**激活 patching 等因果干预**（替换某位置激活看输出是否改变，这是唯一能建立因果的方向）。另外多头研究表明大量头可被剪掉而不影响性能，进一步说明"某个头关注了某处"不等于"模型因此得出该结论"。

</details>

**Q3：FlashAttention 为什么能加速，却不改变结果？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

因为它优化的是**显存 IO**，不是数学。

**问题**：朴素注意力要把 $n\times n$ 的 scores 写回 HBM，再读出来 softmax、写回、再读出来乘 $V$，访存是 $O(n^2)$ 量级；而 GPU 的 SRAM（每 SM 几百 KB）远小于该矩阵（7B、$n=4096$、fp16 时单层 1 GiB）。注意力算术强度低，时间几乎全耗在搬运上。

**做法**：把 $Q$ 分块（$B_r$）、$K/V$ 分块（$B_c$），在 SRAM 内逐块完成 `Q_block @ K_block^T -> softmax -> @ V_block`，$n\times n$ 矩阵分块处理完就丢，永不完整驻留 HBM。

**难点是 softmax**：它需要全行的最大值与指数和才能归一化，但分块时看不到整行。解法是 **online softmax**：维护运行最大值 $m$ 和运行和 $\ell$，每处理一个新块就修正历史累积（$m^{new}=\max(m^{old},\max_j s_j)$，$\ell^{new}=e^{m^{old}-m^{new}}\ell^{old}+\sum_j e^{s_j-m^{new}}$，输出按 $1/\ell^{new}$ 归一化）。这个递推是**精确恒等式**，只是重新结合了加法与乘法，所以输出与朴素实现逐位一致到浮点误差级别（我实测 `torch` 的 `scaled_dot_product_attention` 与手写显式掩码实现最大差 6.66e-16）。

**加速来源**：HBM 访问从 $O(n^2)$ 降到接近 $O(n^2/M)$，实测 2~4 倍；**FLOPs 一点没少**，仍是 $O(n^2d)$。附带收益是显存从 $O(n^2)$ 降到 $O(n)$，让长上下文训得起来；反向传播时也省掉了重算或存储 $n^2$ 中间量的开销。

</details>

**Q4：推理时为什么只缓存 K、V 而不缓存 Q？GQA 省的是什么？**

<details markdown="1">
<summary markdown="1">参考答案</summary>

**只缓存 K/V 的原因**：因果掩码下位置 $j$ 的 $k_j,v_j$ 只依赖 $x_{1..j}$，一旦算出**永不改变**，可跨解码步复用；而 $q_t$ 是"当前 token 的提问"，只服务当前这一步，下一步需要全新的 $q_{t+1}$，缓存它没有收益。Q 是一次性查询，K/V 是可复用的键值数据库。

**收益**：无 cache 时第 $t$ 步要重算长度 $t$ 的前缀，成本 $O(t^2d)$，累计 $O(n^3d)$；有 cache 时每步只需 $q_t$ 与全部历史 $k$ 做点积，$O(nd)$，累计 $O(n^2d)$。$n=4096$ 时相差约 $n/3\approx1365$ 倍。

**GQA 省的是显存，不是计算量。** KV cache 显存为 $2LH_{kv}d_{head}nB\cdot\text{bytes}$，只有 $H_{kv}$ 可压缩：MHA（$H_{kv}=32$）0.5 MiB/token；GQA（$G=8$）128 KiB/token，省 4 倍；MQA（$H_{kv}=1$）16 KiB/token，省 32 倍。查询头仍是 32 个，注意力 FLOPs 完全不变。这恰好命中 decode 的痛点——decode 是 **memory-bound** 的，瓶颈是每步把权重和 KV cache 从 HBM 搬进 SRAM，减少搬运字节数就直接降低单 token 延迟、提升可并发路数。这也解释了为什么实际部署中"并发数 × 上下文长度"才是容量约束：7B 在 $n=4096$、并发 16 时 KV cache 是 32 GiB，而权重只有 13.04 GiB。

</details>

---

## 7. 自测题

1. 取 $d_k=512$，$q,k$ 各分量独立且服从标准正态分布。(a) 未缩放时 logit 的标准差是多少？(b) 缩放后是多少？(c) 用 $\operatorname{tr}(J)=1-\sum p_i^2$ 定性说明两种情况下的梯度流通能力差别。
2. 一个 7B 模型：$L=32$，$h=32$，$d_{head}=128$，fp16 推理，服务端以 $n=8192$、并发 $B=8$ 运行。(a) 写出 KV cache 显存公式并代入计算；(b) 若改用 $H_{kv}=8$ 的 GQA，结果是多少？
3. padding mask 和 causal mask 的形状分别是 `[B,1,1,n]` 和 `[1,1,n,n]`。能否合并成一个张量？合并后形状是什么，为什么可以广播？
4. 某模型 $d_{model}=4096$，原本 $h=32$、$d_{head}=128$，若改成 $h=64$：(a) $d_{head}$ 变成多少？(b) 注意力矩阵显存如何变化？(c) 参数量是否变化？(d) 缩放因子变成多少？
5. 解释为什么无 KV cache 的自回归解码累计复杂度是 $O(n^3d)$ 而非 $O(n^2d)$，给出求和推导；再说明有 cache 后为何 $O(nd)$ 的注意力部分往往不是 decode 的主要耗时项。

<details markdown="1">
<summary markdown="1">参考答案</summary>

**1.** (a) $\operatorname{Var}(s)=\sum_{i=1}^{512}\operatorname{Var}(q_ik_i)=512$，标准差 $=\sqrt{512}\approx22.63$。(b) 除以 $\sqrt{512}\approx22.63$ 后标准差为 1。(c) 未缩放时 logit 极差约 $\pm3\sigma\approx\pm68$，任意两 logit 差 68 意味着概率比 $e^{68}$，softmax 近似 one-hot，$\sum p_i^2\to1$、$\operatorname{tr}(J)\to0$，梯度消失；缩放后 $\operatorname{tr}(J)$ 稳定在约 0.997（$n=1024$ 时上界 $1-1/1024=0.999$），梯度通畅。

**2.** (a) $\text{bytes}=2LH_{kv}d_{head}nB\cdot\text{bytes}=2\times32\times32\times128\times8192\times8\times2$。单 token 单序列：$2\times32\times32\times128\times2=524{,}288\ \text{bytes}=512\ \text{KiB}$；再乘 $nB=8192\times8=65{,}536$：$524{,}288\times65{,}536=3.436\times10^{10}\ \text{bytes}=\mathbf{32\ GiB}$。(b) GQA 把 $H_{kv}$ 从 32 降到 8，缩小 4 倍，得 **8 GiB**（对照：权重仅 13.04 GiB）。

**3.** 可以合并。padding mask 在 key 维广播、causal mask 在 $n\times n$ 上定义，逻辑与得到形状 `[B,1,n,n]`。能广播的原因：padding mask 的 query 维和倒数第二维都是 1（每个 query 面对同一套"哪些 key 有效"），causal mask 的 batch 维和 head 维都是 1（所有样本所有头共用同一套因果结构）。实现上通常直接 `masked_fill` 两次，或用 `combined = causal | padding`（`True` 表示屏蔽）。

**4.** (a) $d_{head}=4096/64=64$。(b) 注意力矩阵元素数为 $Bhn^2$，$h$ 翻倍则**显存翻倍**（改多头配置最容易被忽略的代价）。(c) **参数量不变**：QKVO 仍是四个 $d_{model}\times d_{model}$ 矩阵，共 $4d^2$。(d) 缩放因子从 $\sqrt{128}\approx11.31$ 变为 $\sqrt{64}=8$。$d_{head}$ 变小使每个头的点积在更低维空间进行、估计噪声更大、单头表达力下降，好处是子空间更多样；经验上 $d_{head}$ 取 64~128 较稳，再小通常掉点。

**5.** 无 cache 时生成第 $t$ 个 token 要重新前向长度 $t$ 的前缀，注意力核心成本 $O(t^2d)$（$t$ 个 query × $t$ 个 key），累计

$$\sum_{t=1}^{n}O(t^2d)=O\!\left(d\sum_{t=1}^{n}t^2\right)=O\!\left(d\cdot\frac{n(n+1)(2n+1)}{6}\right)=O(n^3d)$$

有 cache 后第 $t$ 步只需 $q_t$ 与已缓存的 $t$ 个 $k$ 做点积，即 $O(td)$，累计

$$\sum_{t=1}^{n}O(td)=O\!\left(d\cdot\frac{n(n+1)}{2}\right)=O(n^2d)$$

**为什么 $O(nd)$ 不是主要耗时**：decode 每步是"1 个 token 的向量 × 整个权重矩阵"，算术强度极低，GPU 算力严重闲置，时间几乎全花在把权重（每层 $4d^2$ 投影 + FFN）和 KV cache 从 HBM 搬进 SRAM。decode 是 **memory-bandwidth-bound**，瓶颈是搬运字节数而非 FLOPs——这正是 KV cache 量化、GQA、continuous batching 的立足点。

</details>

---

## 8. 延伸阅读

**论文**

- [ ] [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) — Transformer 原始论文，缩放点积注意力与多头注意力的出处，Table 1 复杂度对比值得精读
- [ ] [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (Dao et al., 2022)](https://arxiv.org/abs/2205.14135) — IO 感知的分块算法与 online softmax，精确等价而非近似
- [ ] [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints (Ainslie et al., 2023)](https://arxiv.org/abs/2305.13245) — MQA 与 GQA 的折中，以及用 mean-pooling 改造已有检查点
- [ ] [Fast Transformer Decoding: One Write-Head is All You Need (Shazeer, 2019)](https://arxiv.org/abs/1911.02150) — MQA 原始论文，从 decode 的 memory-bound 特性出发
- [ ] [RoFormer: Enhanced Transformer with Rotary Position Embedding (Su et al., 2021)](https://arxiv.org/abs/2104.09864) — RoPE，相对位置编码的主流方案
- [ ] [Longformer: The Long-Document Transformer (Beltagy et al., 2020)](https://arxiv.org/abs/2004.05150) — 滑动窗口 + 全局 token 的稀疏注意力设计
- [ ] [Attention is not Explanation (Jain & Wallace, 2019)](https://arxiv.org/abs/1902.10186) 与 [Quantifying Attention Flow in Transformers (Abnar & Zuidema, 2020)](https://arxiv.org/abs/2005.00928) — 可解释性争议与 attention rollout
- [ ] [Are Sixteen Heads Really Better than One? (Michel et al., 2019)](https://arxiv.org/abs/1905.10650) — 大量注意力头可被剪枝，说明"关注"不等于"因果"

**文档**

- [ ] [torch.nn.functional.scaled_dot_product_attention](https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) — 官方文档，注意输入形状是 `[B, h, n, d_head]` 与 `is_causal` 的语义
- [ ] [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) — 逐行注释的 Transformer 实现，适合对照阅读
- [ ] [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — 图解 Q/K/V 与多头机制，建立直觉

**本仓库相关笔记**

- [ ] [01 · Transformer 架构总览](README.md) — 本章目录与学习路径
- [ ] Transformer 完整结构：残差、LayerNorm/RMSNorm 与位置编码
- [ ] 05 · 推理优化与部署 — PagedAttention、continuous batching、量化与投机解码
- [ ] 97 · cheatsheet — 公式与复杂度速查

---

[⬅️ 返回本章目录](README.md)
