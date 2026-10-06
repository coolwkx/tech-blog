---
article_id: kp-c20a42eb1214545f
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 7
learning_objective: 理解并验证：手推两层 MLP 的梯度
---

# 手推两层 MLP 的梯度

> **学习目标**：能够解释「手推两层 MLP 的梯度」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 深入机制

## 本次只学这一点

**定义（行样本约定）**：$X\in\mathbb R^{B\times D}$、$W_1\in\mathbb R^{H\times D}$、$b_1\in\mathbb R^{H}$、$W_2\in\mathbb R^{O\times H}$、$b_2\in\mathbb R^{O}$，其中 $B$ 为 batch、$D$ 为输入维、$H$ 为隐藏维、$O$ 为输出维：

$$
Z_1=XW_1^{\top}+\mathbf 1b_1^{\top}\in\mathbb R^{B\times H},\qquad
A_1=\mathrm{ReLU}(Z_1)\in\mathbb R^{B\times H},\qquad
\hat Y=A_1W_2^{\top}+\mathbf 1b_2^{\top}\in\mathbb R^{B\times O}
$$

$$
L=\frac1B\sum_{i,j}(\hat Y-Y)_{ij}^2\in\mathbb R,\qquad \Delta_2\triangleq\frac{\partial L}{\partial\hat Y}=\frac{2}{B}(\hat Y-Y)\in\mathbb R^{B\times O}
$$

**① 第二层**（由 $\hat Y=A_1W_2^{\top}+\dots$）：

$$
\frac{\partial L}{\partial W_2}=\Delta_2^{\top}A_1\in\mathbb R^{O\times B}\cdot\mathbb R^{B\times H}=\mathbb R^{O\times H}\ \text{（与 }W_2\text{ 同形 }\checkmark),\qquad
\frac{\partial L}{\partial b_2}=\Delta_2^{\top}\mathbf 1\in\mathbb R^{O}
$$

继续往隐藏层传（左乘 $W_2$，因为 $W_2^\top$ 的转置是 $W_2$）：

$$
\frac{\partial L}{\partial A_1}=\Delta_2W_2\in\mathbb R^{B\times O}\cdot\mathbb R^{O\times H}=\mathbb R^{B\times H}\ \text{（与 }A_1\text{ 同形 }\checkmark)
$$

**③ 穿过 ReLU**（逐元素，与上游梯度相乘）：$\Delta_1\triangleq\dfrac{\partial L}{\partial Z_1}=\dfrac{\partial L}{\partial A_1}\odot\mathbb 1[Z_1>0]\in\mathbb R^{B\times H}$。

**④ 第一层**（与①同理）：

$$
\frac{\partial L}{\partial W_1}=\Delta_1^{\top}X\in\mathbb R^{H\times D}\ \text{（与 }W_1\text{ 同形 }\checkmark),\quad
\frac{\partial L}{\partial b_1}=\Delta_1^{\top}\mathbf 1\in\mathbb R^{H},\quad
\frac{\partial L}{\partial X}=\Delta_1W_1\in\mathbb R^{B\times D}
$$

**形状自查**（推完必做）：$X,\hat Y,W_1,W_2,b_1,b_2,Z_1,A_1$ 的梯度形状必须分别等于它们的前向形状 $B\times D$、$B\times O$、$H\times D$、$O\times H$、$H$、$O$、$B\times H$、$B\times H$。

规律：**梯度永远与它对应的量同形**，这一条能挡掉绝大多数手推错误。**反向成本**：前向需 $BDH+BHO$ 次乘加，反向需两次同类矩阵乘法（约 $2\times$）加逐元素运算，这就是「反向 ≈ 2 倍前向」的来源。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手推两层 MLP 的梯度」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
