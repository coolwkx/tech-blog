---
article_id: kp-670c6ae1fd3bac5e
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 1
learning_objective: 理解并验证：标量链式法则
---

# 标量链式法则

> **学习目标**：能够解释「标量链式法则」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 核心思想

## 本次只学这一点

$y=f(g(x))$、$u=g(x)$，则 $\dfrac{dy}{dx}=\dfrac{dy}{du}\cdot\dfrac{du}{dx}$。多条路径时求和：$\dfrac{\partial y}{\partial x}=\sum_{\text{从 }x\text{ 到 }y\text{ 的所有路径}}\ \prod_{\text{路径上的边}}\dfrac{\partial\,\text{child}}{\partial\,\text{parent}}$。

例如 `y = x * x + x`，$x$ 走了两条路径，所以 $\partial y/\partial x=x+x\cdot1+1=2x+1$。**「沿路径累加」是 autograd 里到处写 `+=` 的唯一理由**，也是「忘记 `zero_grad` 就梯度累加」的根源。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「标量链式法则」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
