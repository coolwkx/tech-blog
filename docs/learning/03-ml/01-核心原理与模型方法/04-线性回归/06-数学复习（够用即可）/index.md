---
article_id: kp-c1a228814c9d8ae4
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 5
learning_objective: 理解并验证：数学复习（够用即可）
---

# 数学复习（够用即可）

> **学习目标**：能够解释「数学复习（够用即可）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 算法细节

## 本次只学这一点

**标量 / 向量 / 矩阵 / 张量**

| 名称 | 定义 | 例子 |
| --- | --- | --- |
| 标量 scalar | 一个独立的数，只有大小没有方向 | $5$ |
| 向量 vector | 一列顺序排列的元素，默认列向量 | 张三的数理化成绩 $(70,80,90)^\top$ |
| 矩阵 matrix | 二维数组，$m$ 行 $n$ 列 | 张三、李四的成绩：$2\times 3$ |
| 张量 tensor | 向量与矩阵的推广（多维数组） | 一张 RGB 图片 $H\times W\times 3$ |

**范数（Norm）**

$$\|\boldsymbol{x}\|_1 = \sum_i |x_i|,\qquad \|\boldsymbol{x}\|_2 = \sqrt{\sum_i x_i^2},\qquad \|\boldsymbol{x}\|_p = \left(\sum_i |x_i|^p\right)^{1/p}$$

**常用导数**

| 公式 | 例子 |
| --- | --- |
| $(C)^\prime = 0$ | $(5)^\prime=0$ |
| $(x^\alpha)^\prime = \alpha x^{\alpha-1}$ | $(x^3)^\prime = 3x^2$ |
| $(e^x)^\prime = e^x$ | $(e^x)^\prime=e^x$ |
| $(a^x)^\prime = a^x\ln a$ | $(2^x)^\prime=2^x\ln 2$ |
| $(\ln x)^\prime = 1/x$ | $(\ln x)^\prime=1/x$ |
| $(\sin x)^\prime=\cos x$，$(\cos x)^\prime=-\sin x$ | —— |
| 复合：$\{g[h(x)]\}^\prime = g^\prime(h)\cdot h^\prime(x)$ | $(\sin 2x)^\prime = 2\cos 2x$ |

**导数与极值**：可导函数在极值点处导数为 0，即 $f^\prime(x_0)=0$。这就是"求最小值"的全部武器。

**矩阵要点**：$A\times B \neq B\times A$（不满足交换律），但 $A(BC)=(AB)C$（结合律）；$AI=IA=A$；只有方阵且行列式非零才可能有逆 $A^{-1}$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数学复习（够用即可）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
