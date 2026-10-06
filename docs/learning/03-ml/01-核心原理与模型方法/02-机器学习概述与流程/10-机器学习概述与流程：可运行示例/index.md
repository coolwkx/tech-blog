---
article_id: kp-4a5d3183d2d0f114
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-fcedd0430c9c
learning_sourceId: fcedd0430c9c
learning_order: 9
learning_objective: 理解并验证：机器学习概述与流程：可运行示例
---

# 机器学习概述与流程：可运行示例

> **学习目标**：能够解释「机器学习概述与流程：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy 数组与 pandas DataFrame 的基本操作、一点点高中函数与坐标系概念。
>
> **所属主题**：机器学习概述与流程 · 可运行示例

## 本次只学这一点

下面这段代码把"七步法"压进一个脚本，用鸢尾花数据集演示完整闭环。注意**标准化的纪律都遵守了**（只在训练集 fit，测试集只 transform）。

```python
# -*- coding: utf-8 -*-
"""机器学习建模流程最小可运行模板（scikit-learn）

覆盖：加载数据 -> 划分数据集 -> 特征预处理 -> 训练 -> 预测 -> 评估 -> 保存 -> 加载推理
"""
import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


def main():
    # ① 获取数据
    iris = load_iris()
    X, y = iris.data, iris.target # X: (150, 4) y: (150,)

    # ② 划分数据集：stratify=y 保证训练/测试集里各类别比例一致
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=22, stratify=y
    )

    # ③ 特征工程：标准化（Z-Score）
    # 关键：统计量只能从训练集学出来，否则测试集信息会"泄漏"进训练
    transfer = StandardScaler()
    X_train = transfer.fit_transform(X_train) # 训练集：fit + transform
    X_test = transfer.transform(X_test) # 测试集：只 transform

    # ④ 模型训练
    estimator = KNeighborsClassifier(n_neighbors=5)
    estimator.fit(X_train, y_train)

    # ⑤ 模型评估
    y_pred = estimator.predict(X_test)
    print("预测值 :", y_pred)
    print("真实值 :", y_test)
    print("准确率 :", accuracy_score(y_test, y_pred))
    print("estimator.score:", estimator.score(X_test, y_test))
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # ⑥ 调优：交叉验证给出更稳的泛化估计（5 折）
    cv_scores = cross_val_score(estimator, X_train, y_train, cv=5)
    print("5 折交叉验证得分:", np.round(cv_scores, 4), "均值:", cv_scores.mean())

    # ⑦ 保存与推理
    joblib.dump(estimator, "knn_iris.pkl")
    model = joblib.load("knn_iris.pkl")

    # 模拟一条线上新样本：必须做同样的标准化！
    new_sample = np.array([[5.1, 3.5, 1.4, 0.2]])
    new_sample = transfer.transform(new_sample)
    print("新样本预测类别:", model.predict(new_sample))
    print("新样本各类别概率:", np.round(model.predict_proba(new_sample), 4))


    if __name__ == "__main__":
        main()
```

**预期输出要点**：准确率约 0.93 上下（`n_neighbors=5`、`random_state=22` 时通常 14/15 或 15/15）；`predict_proba` 返回 3 个概率且和为 1。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「机器学习概述与流程：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)
