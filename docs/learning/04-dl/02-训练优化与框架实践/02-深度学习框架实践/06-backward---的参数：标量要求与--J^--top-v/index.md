---
article_id: kp-170f73195a5de017
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-ae2a0b64784b
learning_sourceId: ae2a0b64784b
learning_order: 5
learning_objective: 理解并验证：backward() 的参数：标量要求与 $J^{\top}v$
---

# backward() 的参数：标量要求与 $J^{\top}v$

> **学习目标**：能够解释「backward() 的参数：标量要求与 $J^{\top}v$」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会 Python（类、`with`、装饰器）；知道张量与矩阵乘法；了解前向传播、损失函数、梯度下降与链式法则（参见本目录 01 反向传播与计算图、02 优化与训练技巧）。
>
> **所属主题**：-深度学习框架实践 · 算法细节

## 本次只学这一点

`backward()` 起点隐含 $v=1$；若输出不是标量 $y\in\mathbb{R}^m$，就必须显式给出 $v\in\mathbb{R}^m$，引擎算向量-雅可比积 $(J^{\top}v)_i=\sum_j (\partial y_j/\partial x_i)\,v_j$（例：$y=x^3,\ x=(1,2),\ v=(1,1)\Rightarrow\nabla=(3,12)=3x^2$）。多输出网络里的 `loss.backward()` 能用，是因为标量化那一步已先 `.sum()` 或 `.mean()` 过了。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「backward() 的参数：标量要求与 $J^{\top}v$」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)
