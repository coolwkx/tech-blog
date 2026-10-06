---
article_id: kp-8e7b6a9e7a46b615
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 11
learning_objective: 理解并验证：随机森林：泰坦尼克号（含交叉验证网格搜索）
---

# 随机森林：泰坦尼克号（含交叉验证网格搜索）

> **学习目标**：能够解释「随机森林：泰坦尼克号（含交叉验证网格搜索）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""随机森林 vs 单棵决策树，并用 GridSearchCV 调参"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier

def main(csv_path="train.csv"):
    # 1. 获取数据
    titan = pd.read_csv(csv_path)
    # 2. 确定特征值与目标值
    x = titan[["Pclass", "Age", "Sex"]].copy
    y = titan["Survived"]
    # 3. 特征工程
    x["Age"] = x["Age"].fillna(titan["Age"].mean) # 缺失值用均值填充
    x = pd.get_dummies(x) # 类别型特征独热编码
    # 4. 数据集划分
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, random_state=22, test_size=0.2, stratify=y
    )

    # 5-1 单棵决策树
    dtc = DecisionTreeClassifier(random_state=22)
    dtc.fit(x_train, y_train)
    print("单一决策树 accuracy:", round(dtc.score(x_test, y_test), 4))

    # 5-2 随机森林（限定深度）
    rfc = RandomForestClassifier(max_depth=6, random_state=9)
    rfc.fit(x_train, y_train)
    print("随机森林 accuracy:", round(rfc.score(x_test, y_test), 4))

    # 5-3 交叉验证 + 网格搜索
    param = {"n_estimators": [40, 50, 60, 70],
    "max_depth": [2, 4, 6, 8, 10],
    "random_state": [9]}
    grid = GridSearchCV(RandomForestClassifier, param_grid=param, cv=2, n_jobs=-1)
    grid.fit(x_train, y_train)
    print("网格搜索 accuracy:", round(grid.score(x_test, y_test), 4))
    print("最优参数:", grid.best_params_)
    print("最优模型:", grid.best_estimator_)
    print("特征重要性:", dict(zip(x.columns, grid.best_estimator_.feature_importances_.round(4))))

    if __name__ == "__main__":
        main
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「随机森林：泰坦尼克号（含交叉验证网格搜索）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
