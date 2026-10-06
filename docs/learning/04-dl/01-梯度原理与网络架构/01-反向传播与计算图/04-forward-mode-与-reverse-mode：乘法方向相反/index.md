---
article_id: kp-ace1edc07024f1c3
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 3
learning_objective: 理解并验证：forward-mode 与 reverse-mode：乘法方向相反
---

# forward-mode 与 reverse-mode：乘法方向相反

> **学习目标**：能够解释「forward-mode 与 reverse-mode：乘法方向相反」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 核心思想

## 本次只学这一点

设 $\mathbf x\in\mathbb R^n$、$\mathbf y\in\mathbb R^m$，中间 $k$ 层的雅可比为 $J_1,\dots,J_k$，总雅可比 $J=J_k\cdots J_1$。

| 模式 | 怎么算 | 需要几次传播 | 适合的形状 |
| --- | --- | --- | --- |
| forward-mode（JVP） | 左乘累积 $\dot{\mathbf y}=J_k\cdots J_1\dot{\mathbf x}$ | $n$ 次（每个输入一次） | 输入少、输出多 |
| reverse-mode（VJP） | 右乘累积 $\bar{\mathbf x}=J_1^{\top}\cdots J_k^{\top}\bar{\mathbf y}$ | $m$ 次（每个输出一次） | **输入多、输出少（我们的情况）** |

反向模式每一步传播的是**向量**（vector-Jacobian product, VJP），而不是显式构造 $m\times n$ 的雅可比。这正是每个算子的 `backward` 只实现「给我上游梯度 $\bar y$，我返回下游梯度 $\bar x$」的原因——**雅可比从不被显式物化**。记忆：forward-mode 把「输入扰动」推到底，reverse-mode 把「输出敏感度」拉回来；损失是标量时 $\bar y=1$，一次反向就够。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「forward-mode 与 reverse-mode：乘法方向相反」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
