---
article_id: kp-cca82c818c422877
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 8
learning_objective: 理解并验证：掩码：padding mask 与 causal mask
---

# 掩码：padding mask 与 causal mask

> **学习目标**：能够解释「掩码：padding mask 与 causal mask」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「掩码：padding mask 与 causal mask」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
