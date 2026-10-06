---
article_id: kp-4c152ef64695166c
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 10
learning_objective: 理解并验证：API 参数详解
---

# API 参数详解

> **学习目标**：能够解释「API 参数详解」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 算法细节

## 本次只学这一点

```python
sklearn.linear_model.LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=100)
```

| 参数 | 含义 | 常用取值 |
| --- | --- | --- |
| `penalty` | 正则化种类 | `'l2'`（默认）、`'l1'`、`'elasticnet'`、`None` |
| `C` | **正则化力度的倒数**（$C=1/\lambda$）：$C$ 越大 → 正则化越弱 → 模型越复杂 | 默认 1.0；试 `[0.01, 0.1, 1, 10, 100]` |
| `solver` | 优化算法 | `'liblinear'`（小数据集、支持 L1）、`'lbfgs'`（默认）、`'sag'/'saga'`（大数据集，`saga` 支持 L1） |
| `max_iter` | 最大迭代次数 | 不收敛时增大（如 1000） |
| `class_weight` | 类别权重 | 不平衡时用 `'balanced'` |

**solver 与 penalty 的兼容性**：

| solver | L1 | L2 | 无正则 |
| --- | --- | --- | --- |
| `liblinear` | 支持 | 支持 | 支持 |
| `lbfgs` / `newton-cg` | 不支持 | 支持 | 支持 |
| `sag` / `saga` | 仅 `saga` | 支持 | 支持 |

**默认正例的坑**：scikit-learn 的 `LogisticRegression` **默认把类别数较少的那类当作正例**。计算 Precision/Recall 时如不确定，请显式传 `pos_label`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「API 参数详解」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
