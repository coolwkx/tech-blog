---
article_id: kp-e2852dfb3de5b1e0
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 11
learning_objective: 理解并验证：现代变体
---

# 现代变体

> **学习目标**：能够解释「现代变体」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「现代变体」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
