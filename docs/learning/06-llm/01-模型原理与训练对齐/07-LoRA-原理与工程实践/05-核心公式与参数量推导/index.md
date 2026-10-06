---
article_id: kp-8bb8df478e28e21a
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-968a88f3144b
learning_sourceId: 968a88f3144b
learning_order: 4
learning_objective: 理解并验证：核心公式与参数量推导
---

# 核心公式与参数量推导

> **学习目标**：能够解释「核心公式与参数量推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性层与矩阵乘法；反向传播；Transformer 里 $W_q/W_k/W_v/W_o$ 的形状；显存账本中"梯度 + 优化器状态随可训练参数增长"（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：LoRA 原理与工程实践 · 关键机制

## 本次只学这一点

对一个预训练权重矩阵 $W_0\in\mathbb{R}^{d\times k}$（$d$ 为输出维度，$k$ 为输入维度），LoRA 把更新约束为低秩分解：

$$
W = W_0 + \Delta W = W_0 + \frac{\alpha}{r}\,B A,
\qquad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k}
$$

前向传播为：

$$
h = W_0 x + \Delta W x = W_0 x + \frac{\alpha}{r}\,B A x,\qquad x\in\mathbb{R}^{k}
$$

训练时 $W_0$ 冻结（`requires_grad=False`），只有 $A$、$B$ 参与梯度更新。

**参数量推导**：

$$
\underbrace{dk}_{\text{全参更新}} \;\longrightarrow\; \underbrace{dr + rk}_{A \text{ 与 } B} = r(d+k)
$$

当代入典型的方阵 $d=k$ 时：

$$
r(d+d) = 2dr \quad\text{vs}\quad d^2
$$

压缩比为：

$$
\frac{2dr}{d^2} = \frac{2r}{d}
$$

**数值例（推导）**：$d=k=4096$、$r=8$ 时

$$
2dr = 2\times8\times4096 = 65{,}536,\qquad d^2 = 16{,}777{,}216
$$

$$
\frac{65536}{16777216} = 0.3906\%
$$

即单个 $4096\times4096$ 矩阵的 LoRA 参数只占该矩阵的 **0.39%**。整个 7B 模型上（$r=8$，只适配 $W_q,W_v$，32 层）新增参数为

$$
32 \times 2 \times 65{,}536 = 4{,}194{,}304 \approx 4.19\text{M}
$$

占 7B 的 $0.0599\%$。若把六个投影矩阵全部适配（$q,k,v,o,\text{gate},\text{up},\text{down}$ 共 7 个），新增约 $14.7$ M，占 $0.21\%$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「核心公式与参数量推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)
