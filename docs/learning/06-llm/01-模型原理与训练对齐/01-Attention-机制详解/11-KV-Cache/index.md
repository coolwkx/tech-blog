---
article_id: kp-3b4fd02c989abfc9
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 10
learning_objective: 理解并验证：KV Cache
---

# KV Cache

> **学习目标**：能够解释「KV Cache」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「KV Cache」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
