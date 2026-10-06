---
article_id: kp-37dc17a4baf97cd5
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 2
learning_objective: 理解并验证：向量情形：雅可比
---

# 向量情形：雅可比

> **学习目标**：能够解释「向量情形：雅可比」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 核心思想

## 本次只学这一点

输入输出都是向量时（$\mathbf f:\mathbb R^n\to\mathbb R^m$），一阶导数不是向量而是 $m\times n$ 的**雅可比矩阵**：

$$
J=\frac{\partial \mathbf f}{\partial \mathbf x}\in\mathbb R^{m\times n},\qquad J_{ij}=\frac{\partial f_i}{\partial x_j},\qquad
\frac{\partial \mathbf z}{\partial \mathbf x}=\underbrace{\frac{\partial \mathbf z}{\partial \mathbf y}}_{p\times m}\underbrace{\frac{\partial \mathbf y}{\partial \mathbf x}}_{m\times n}
$$

下标就是自查工具：**雅可比连乘时中间维度必须对上**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「向量情形：雅可比」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
