---
article_id: kp-9a3c01eebe651dc8
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-e9af573d72de
learning_sourceId: e9af573d72de
learning_order: 8
learning_objective: 理解并验证：网格搜索（Grid Search）
---

# 网格搜索（Grid Search）

> **学习目标**：能够解释「网格搜索（Grid Search）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归的 MSE/RMSE/MAE（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、混淆矩阵与 ROC/AUC（见 [04-逻辑回归](../../../../../03-ml/02-经典算法/04-逻辑回归.md)）、KNN 的交叉验证与网格搜索（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：模型评估与调优 · 算法细节

## 本次只学这一点

**做法**：把候选超参数做**笛卡尔积**，对每一组参数做交叉验证评分，取最高分的组合。

**复杂度**：若有两组超参数分别有 $a$、$b$ 个候选值、CV 折数为 $c$，则总共要训练 $a\times b\times c$ 次。

**例（随机森林）**：

```python
param = {"n_estimators": [40, 50, 60, 70],
"max_depth": [2, 4, 6, 8, 10],
"random_state": [9]}
grid_search = GridSearchCV(estimator, param_grid=param, cv=2)
```

一共 $4\times5\times1\times2 = 40$ 次训练。

**关键属性**：

| 属性 | 含义 |
| --- | --- |
| `best_score_` | 交叉验证中所有参数组合的**最高平均验证得分** |
| `best_params_` | 最优超参数字典 |
| `best_estimator_` | 用最优参数在**全部训练集**上重新拟合好的估计器 |
| `cv_results_` | 每组的 `mean_test_score`、`std_test_score`、`rank_test_score` 等详情 |
| `score(X_test, y_test)` | 用最优模型在测试集上评估（**这才是最终成绩**） |

> **注意**：`best_score_` 常常略高于测试集得分，这是正常的（数据量、折数的随机性导致）。学习笔记也提示过："因为数据量和特征的问题，该值可能小于上述的平均测试得分。"

**网格搜索的替代方案**：

| 方法 | 特点 |
| --- | --- |
| `RandomizedSearchCV` | 随机采样参数组合，参数空间大时效率更高 |
| 贝叶斯优化（Optuna、Hyperopt） | 用历史评估结果指导下一次采样，最省算力 |
| 手动调参 | 参数少时更快，但可复现性差 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「网格搜索（Grid Search）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)
