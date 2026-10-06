---
article_id: kp-c692005058c8fffa
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-11324cf8be3a
learning_sourceId: 11324cf8be3a
learning_order: 16
learning_objective: 理解并验证：sklearn 线性回归 API 速查
---

# sklearn 线性回归 API 速查

> **学习目标**：能够解释「sklearn 线性回归 API 速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：导数/偏导数与矩阵乘法（本文第 2.1 节会复习）、numpy 数组运算、`train_test_split` 与 `StandardScaler` 的用法（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：线性回归 · 可运行示例

## 本次只学这一点

| API | 优化方式 | 关键参数 | 关键属性 |
| --- | --- | --- | --- |
| `LinearRegression(fit_intercept=True)` | 正规方程（闭式解） | `fit_intercept`：是否计算偏置 | `coef_`、`intercept_` |
| `SGDRegressor(loss="squared_loss", learning_rate='constant', eta0=0.01)` | 梯度下降 | `loss`、`learning_rate`（如 `'invscaling'` 时 $\eta_t=\eta_0/t^{0.25}$）、`eta0`、`penalty` | `coef_`、`intercept_` |
| `Ridge(alpha=1.0)` | L2 正则（多种求解器） | `alpha` 惩罚力度 | `coef_`、`intercept_` |
| `RidgeCV` | L2 + 内置交叉验证选 `alpha` | `alphas` | `alpha_`、`coef_` |
| `Lasso(alpha=1.0)` | L1 正则 | `alpha` 惩罚力度 | `coef_`（部分为 0） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/03-线性回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「sklearn 线性回归 API 速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/03-线性回归.md)
