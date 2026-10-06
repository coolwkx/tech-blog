---
article_id: kp-88c02cf9fbcb7076
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 4
learning_objective: 理解并验证：随机森林（Random Forest）
---

# 随机森林（Random Forest）

> **学习目标**：能够解释「随机森林（Random Forest）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 算法细节

## 本次只学这一点

**定义**：基于 Bagging 思想、**以决策树为弱学习器**的集成算法。

**构建步骤（5 步）**：
1. 从训练集中**有放回**地随机抽取 $m$ 个样本；
2. 从全部特征中**随机挑选 $n$ 个特征**（$n<$ 总特征数）作为该次分裂的候选特征；
3. 用抽样得到的数据与特征训练一棵决策树（不剪枝或弱剪枝）；
4. 重复 1~3 共 $K$ 次，得到 $K$ 棵树；
5. **分类**：平权投票、多数表决输出结果；**回归**：简单平均。

**随机森林的"随机"二重奏**：

| 随机层 | 内容 | 参数 |
| --- | --- | --- |
| 数据随机 | bootstrap 采样，约 63.2% 的样本会被抽到（$1-(1-\frac1m)^m\to 1-e^{-1}$） | 由 `bootstrap=True` 控制 |
| 特征随机 | 每次分裂只用随机 $n$ 个特征 | `max_features`（分类常用 $\sqrt{d}$，回归常用 $d/3$） |

**sklearn API**：

```python
sklearn.ensemble.RandomForestClassifier(
n_estimators=100, # 树的数量
criterion='gini', # 分裂准则
max_depth=None, # 最大深度
max_features='sqrt', # 每次分裂考虑的特征数
bootstrap=True, # 是否自助采样
oob_score=False, # 是否用袋外样本评估
random_state=None,
n_jobs=None, # 并行核数
)
```

| 属性 | 含义 |
| --- | --- |
| `estimators_` | 所有子决策树的列表 |
| `feature_importances_` | 特征重要性（基于不纯度下降） |
| `oob_score_` | 袋外样本得分（免费的验证集！） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「随机森林（Random Forest）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
