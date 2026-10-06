---
article_id: kp-63bc24c267949c30
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 10
learning_objective: 理解并验证：类别不平衡的处理
---

# 类别不平衡的处理

> **学习目标**：能够解释「类别不平衡的处理」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 算法细节

## 本次只学这一点

**危害**：若负样本占 74%，模型全部预测负例就有 74% 准确率，但 F1 为 0。

**处理手段**：

| 层面 | 手段 | API / 做法 |
| --- | --- | --- |
| 数据层 | 过采样少数类（SMOTE） | `imblearn.over_sampling.SMOTE` |
| 数据层 | 欠采样多数类 | `imblearn.under_sampling.RandomUnderSampler` |
| 算法层 | 类别权重 | `class_weight='balanced'` |
| 算法层 | 样本权重 | `class_weight.compute_sample_weight('balanced', y)` 传给 `fit(sample_weight=...)` |
| 评估层 | 换指标 | F1、AUC、PR 曲线、`classification_report` |
| 折分层 | 分层抽样 | `StratifiedKFold` / `train_test_split(stratify=y)` |

**实例（XGBoost 红酒品质分类）**：

```python
classes_weights = class_weight.compute_sample_weight(class_weight='balanced', y=y_train)
estimator.fit(x_train, y_train, sample_weight=classes_weights)
```

**实例（电信客户流失）**：`Churn_Yes` 占比约 26%，属于标签不平衡样本，因此重点关注 Precision、Recall 与 AUC。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「类别不平衡的处理」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
