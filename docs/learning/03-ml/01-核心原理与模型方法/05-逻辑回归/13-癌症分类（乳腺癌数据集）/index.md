---
article_id: kp-7ea155175f07a492
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 12
learning_objective: 理解并验证：癌症分类（乳腺癌数据集）
---

# 癌症分类（乳腺癌数据集）

> **学习目标**：能够解释「癌症分类（乳腺癌数据集）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""逻辑回归：乳腺癌（Wisconsin）二分类
数据：699 条样本，11 列（第 1 列是 id，后 9 列是医学特征，最后 1 列是类别：2=良性、4=恶性）
含 16 个用 '?' 标出的缺失值
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
confusion_matrix, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

CSV = "breast-cancer-wisconsin.csv"


def main():
    # 1. 获取数据
    data = pd.read_csv(CSV)
    print(data.info())

    # 2. 数据基本处理
    # 2.1 缺失值处理：'?' -> NaN -> 删除
    data = data.replace("?", np.nan)
    data = data.dropna()

    # 2.2 确定特征值与目标值（第 1 列 id 没有判别力，丢掉）
    x = data.iloc[:, 1:-1]
    y = data["Class"]

    # 2.3 分割数据：stratify 保持类别比例
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=22, stratify=y
    )

    # 3. 特征工程：标准化（逻辑回归用梯度下降求解，需要统一量纲）
    transfer = StandardScaler()
    x_train = transfer.fit_transform(x_train)
    x_test = transfer.transform(x_test)

    # 4. 模型训练
    estimator = LogisticRegression(max_iter=1000)
    estimator.fit(x_train, y_train)

    # 5. 模型预测与评估
    y_pred = estimator.predict(x_test)
    print("混淆矩阵:\n", confusion_matrix(y_test, y_pred, labels=[2, 4]))
    print("准确率:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred, target_names=["良性(2)", "恶性(4)"]))

    # 6. 计算 AUC：必须传"正例的概率"，不能传 0/1 预测标签
    y_score = estimator.predict_proba(x_test)[:, 1]
    print("classes_:", estimator.classes_)
    print("AUC:", roc_auc_score((y_test == 4).astype(int), y_score))

    # 7. 查看系数（标准化后可直接比较特征重要性）
    print("系数:", dict(zip(x.columns, np.round(estimator.coef_[0], 3))))
    print("截距:", estimator.intercept_)


    if __name__ == "__main__":
        main()
```

> **AUC 的正确用法**：`roc_auc_score(y_true, y_score)` 要求 `y_true` 是 **0/1** 标记，`y_score` 是**概率或置信度**。代码里 `roc_auc_score(y_test, y_predict)` 传的是 0/1 预测值，这会退化成"准确率"的变体，**不是真正的 AUC**，实战中必须改为 `predict_proba`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「癌症分类（乳腺癌数据集）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
