---
article_id: kp-9a17deb0ae17cfb8
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 7
learning_objective: 理解并验证：缩放点积注意力与张量形状
---

# 缩放点积注意力与张量形状

> **学习目标**：能够解释「缩放点积注意力与张量形状」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

给定输入序列长度 $n$、模型维度 $d_{model}$、注意力头数 $h$，每个头的维度 $d_k=d_v=d_{model}/h$。

| 张量 | 形状 | 说明 |
|---|---|---|
| 输入 $X$ | $(n, d_{model})$ | 一个 batch 内的一条序列 |
| $W_Q, W_K, W_V$ | $(d_{model}, d_{model})$ | 线性投影参数 |
| $Q, K, V$ | $(n, d_{model})$ | 投影结果 |
| 按头切分并转置 | $(h, n, d_k)$ | 每个头独立计算 |
| 注意力分数 $QK^{\top}$ | $(h, n, n)$ | 每个 token 对所有 token 的相似度 |
| 注意力输出 | $(h, n, d_k)$ | 加权求和结果 |
| 拼接 + 输出投影 | $(n, d_{model})$ | 多头结果合并 |

**缩放点积注意力公式**：

$$\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V$$

**为什么要除以 $\sqrt{d_k}$**：当 $d_k$ 较大时，$Q\cdot K$ 的点积方差随维度线性增长（约等于 $d_k$），
softmax 的输入会落入梯度极小的饱和区，导致梯度消失、训练不稳定。除以 $\sqrt{d_k}$ 把方差拉回 1 附近，
使 softmax 保持在梯度良好的区间。

**Multi-Head 为什么有效**：单头只能学到一种「相似度视角」；多头把表示空间切成 $h$ 份分别做注意力，
不同头可以分别关注语法依赖、指代、位置邻近等不同模式，最后拼接再投影，等价于在多个子空间并行做关系建模，
表达力显著强于单头（且总计算量与单头同维时基本相当）。

**Mask 的两种类型**：

| 类型 | 作用 | 使用场景 |
|---|---|---|
| Padding mask | 屏蔽补齐到同一长度的无效 pad token | 所有 batch 训练 |
| Causal mask（因果/上三角 mask） | 遮掉未来位置，只允许看到左侧上文 | decoder-only 生成模型 |
| 交叉 mask | decoder 只能关注 encoder 的有效位置 | encoder-decoder |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「缩放点积注意力与张量形状」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
