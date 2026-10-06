---
article_id: kp-450eb4755810cea7
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-33f370d2f18b
learning_sourceId: 33f370d2f18b
learning_order: 12
learning_objective: 理解并验证：泰坦尼克号生存预测
---

# 泰坦尼克号生存预测

> **学习目标**：能够解释「泰坦尼克号生存预测」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率与信息论中"熵"的直观含义、对数运算 $\log_2$、pandas 的缺失值处理与 `get_dummies`（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：决策树 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""决策树：泰坦尼克号生存预测（含树可视化）"""
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

def main(csv_path="train.csv"):
    # 1. 读取数据
    taitan_df = pd.read_csv(csv_path)
    print(taitan_df.info)

    # 2. 数据基本处理
    x = taitan_df[["Pclass", "Age", "Sex"]].copy
    y = taitan_df["Survived"]
    # 2.1 缺失值处理：Age 用均值填充
    x["Age"] = x["Age"].fillna(x["Age"].mean)
    # 2.2 类别型特征 one-hot 编码
    x = pd.get_dummies(x)

    # 2.3 数据集划分
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=33, stratify=y
    )

    # 3. 模型训练（限制 max_depth 做预剪枝，防止过拟合）
    estimator = DecisionTreeClassifier(max_depth=5, min_samples_leaf=3,
    random_state=33)
    estimator.fit(x_train, y_train)

    # 4. 模型预测与评估
    y_pred = estimator.predict(x_test)
    print("准确率:", estimator.score(x_test, y_test))
    print(classification_report(y_test, y_pred, target_names=["died", "survived"]))

    # 5. 特征重要性（决策树自带，靠近根的特征更重要）
    print("特征重要性:", dict(zip(x.columns, estimator.feature_importances_.round(4))))

    # 6. 决策树可视化
    plt.figure(figsize=(30, 20))
    plot_tree(estimator,
    max_depth=3,
    filled=True,
    feature_names=list(x.columns),
    class_names=["died", "survived"])
    plt.show()

    if __name__ == "__main__":
        main
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/05-决策树.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「泰坦尼克号生存预测」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/05-决策树.md)
