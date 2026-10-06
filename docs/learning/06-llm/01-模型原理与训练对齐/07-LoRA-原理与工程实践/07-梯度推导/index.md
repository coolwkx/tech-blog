---
article_id: kp-fd39db7a23dbad3e
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-968a88f3144b
learning_sourceId: 968a88f3144b
learning_order: 6
learning_objective: 理解并验证：梯度推导
---

# 梯度推导

> **学习目标**：能够解释「梯度推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性层与矩阵乘法；反向传播；Transformer 里 $W_q/W_k/W_v/W_o$ 的形状；显存账本中"梯度 + 优化器状态随可训练参数增长"（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：LoRA 原理与工程实践 · 关键机制

## 本次只学这一点

设 $\tilde{h} = \frac{\alpha}{r}BAx$，损失对输出的梯度记为 $g = \frac{\partial \mathcal{L}}{\partial h}\in\mathbb{R}^{d}$，则

$$
\frac{\partial \mathcal{L}}{\partial B} = \frac{\alpha}{r}\,g\,(Ax)^{\top}\in\mathbb{R}^{d\times r},
\qquad
\frac{\partial \mathcal{L}}{\partial A} = \frac{\alpha}{r}\,(B^{\top}g)\,x^{\top}\in\mathbb{R}^{r\times k}
$$

两个关键观察：

- **梯度只经过 $A$、$B$**，$W_0$ 完全没有梯度，因此**没有优化器状态**，这是 LoRA 省显存的根本原因（对比 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md) 的 16 B/参数）。
- 计算 $\frac{\partial \mathcal{L}}{\partial A}$ 需要 $B^{\top}g$，计算 $\frac{\partial \mathcal{L}}{\partial B}$ 需要 $Ax$，所以**前向时必须缓存 $Ax$**（$r$ 维，很小）和 $x$（$k$ 维）。这一点决定了一个实现细节：如果你的 LoRA 层要在 `merge` 之后继续训练，必须能重新拿到 $Ax$。

**缩放因子的梯度效应**：$\alpha/r$ 同时出现在两个梯度里，所以它等价于**缩放 LoRA 分支的学习率**。这就是"改 $r$ 时要同步改 $\alpha$"的原因——如果只把 $r$ 从 8 调到 32 而 $\alpha$ 不变，$\alpha/r$ 从 2 掉到 0.5，等效学习率降了 4 倍，你会误以为"增大 $r$ 没用"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)
