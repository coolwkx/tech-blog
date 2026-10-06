---
article_id: kp-909ff4f3dde87db1
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 2
learning_objective: 理解并验证：四大算法速览
---

# 四大算法速览

> **学习目标**：能够解释「四大算法速览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 核心思想

## 本次只学这一点

| 算法 | 流派 | 弱学习器 | 核心思想 | 关键超参数 |
| --- | --- | --- | --- | --- |
| 随机森林 | Bagging | 决策树 | 样本随机 + 特征随机 + 平权投票 | `n_estimators`、`max_depth`、`max_features` |
| AdaBoost | Boosting | 决策树桩（`max_depth=1`） | **提高被前一步分错样本的权重** | `n_estimators`、`learning_rate`、`base_estimator` |
| GBDT | Boosting | CART 回归树 | **拟合上一轮损失函数的负梯度** | `n_estimators`、`max_depth`、`learning_rate` |
| XGBoost | Boosting | CART 回归树 | GBDT + **正则化项** + 二阶泰勒展开 | `n_estimators`、`max_depth`、`eta`、`gamma`、`lambda` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四大算法速览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
