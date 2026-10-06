---
article_id: kp-da9acaabc5f320a8
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 11
learning_objective: 理解并验证：鸢尾花分类：完整流程 + 交叉验证网格搜索
---

# 鸢尾花分类：完整流程 + 交叉验证网格搜索

> **学习目标**：能够解释「鸢尾花分类：完整流程 + 交叉验证网格搜索」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""KNN 鸢尾花分类：标准化 + 网格搜索选 K"""
import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


def main():
    # 1. 获取数据
    iris = load_iris()
    X, y = iris.data, iris.target

    # 2. 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=22, stratify=y
    )

    # 3. 特征工程：标准化（训练集 fit_transform，测试集 transform）
    transfer = StandardScaler()
    X_train = transfer.fit_transform(X_train)
    X_test = transfer.transform(X_test)

    # 4. 网格搜索 + 交叉验证选 K
    estimator = KNeighborsClassifier()
    param_grid = {"n_neighbors": range(1, 15)}
    grid = GridSearchCV(estimator=estimator, param_grid=param_grid, cv=5)
    grid.fit(X_train, y_train)

    print("最优 K :", grid.best_params_)
    print("CV 最高平均分 :", round(grid.best_score_, 4))
    print("最优估计器 :", grid.best_estimator_)

    # 5. 用最优模型评估测试集
    best = grid.best_estimator_
    y_pred = best.predict(X_test)
    print("测试集准确率 :", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # 6. 对新样本预测（别忘了用同一个 scaler 变换）
    my_data = transfer.transform([[5.1, 3.5, 1.4, 0.2]])
    print("新样本类别 :", best.predict(my_data),
    "->", iris.target_names[best.predict(my_data)[0]])
    print("新样本类别概率 :", np.round(best.predict_proba(my_data), 4))


    if __name__ == "__main__":
        main()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「鸢尾花分类：完整流程 + 交叉验证网格搜索」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
