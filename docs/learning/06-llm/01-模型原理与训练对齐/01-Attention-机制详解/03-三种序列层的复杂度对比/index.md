---
article_id: kp-a7916fee18f1aa26
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 2
learning_objective: 理解并验证：三种序列层的复杂度对比
---

# 三种序列层的复杂度对比

> **学习目标**：能够解释「三种序列层的复杂度对比」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 为什么需要它

## 本次只学这一点

这正是原论文 Table 1 的核心：

| 层类型 | 每层复杂度 | 顺序操作数 | 最长路径长度 |
| --- | --- | --- | --- |
| 自注意力 Self-Attention | $O(n^2 \cdot d)$ | $O(1)$ | $O(1)$ |
| 循环 Recurrent | $O(n \cdot d^2)$ | $O(n)$ | $O(n)$ |
| 卷积 Convolutional | $O(k \cdot n \cdot d^2)$ | $O(1)$ | $O(\log_k n)$ |

自注意力用 $O(n^2)$ 时间换来 $O(1)$ 路径长度与完全并行，**当 $n < d$ 时它甚至比 RNN 更便宜**——这是 Transformer 在 2017 年能赢的算术基础；而 $n$ 从 512 涨到 20 万时 $n^2$ 涨了 15 万倍，这就是长上下文成为当今主要矛盾的原因。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三种序列层的复杂度对比」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
