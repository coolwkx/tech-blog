---
article_id: kp-649ae659066491ea
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 12
learning_objective: 理解并验证：GBDT：泰坦尼克号
---

# GBDT：泰坦尼克号

> **学习目标**：能够解释「GBDT：泰坦尼克号」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""GBDT（GradientBoostingClassifier）在泰坦尼克号上的训练与调参"""
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, train_test_split

def main(csv_path="train.csv"):
    taitan_df = pd.read_csv(csv_path)
    x = taitan_df[["Pclass", "Age", "Sex"]].copy
    y = taitan_df["Survived"].copy
    x["Age"] = x["Age"].fillna(x["Age"].mean)
    x = pd.get_dummies(x)
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, random_state=22, test_size=0.2, stratify=y
    )

    # 3. 默认参数下的 GBDT
    estimator = GradientBoostingClassifier(random_state=22)
    estimator.fit(x_train, y_train)
    print("GBDT 默认参数 accuracy:", round(estimator.score(x_test, y_test), 4))

    # 4. 网格搜索 + 交叉验证
    param = {"n_estimators": [100, 110, 120, 130],
    "max_depth": [2, 3, 4],
    "random_state": [9]}
    grid = GridSearchCV(GradientBoostingClassifier, param_grid=param, cv=3, n_jobs=-1)
    grid.fit(x_train, y_train)
    print("GBDT 调参后 accuracy:", round(grid.score(x_test, y_test), 4))
    print("最优参数:", grid.best_params_)
    print(classification_report(y_test, grid.predict(x_test), target_names=["died", "survived"]))

    if __name__ == "__main__":
        main
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GBDT：泰坦尼克号」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
