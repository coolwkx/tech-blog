---
article_id: kp-658e6d6740a4ddc8
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-f80e625a8f58
learning_sourceId: f80e625a8f58
learning_order: 14
learning_objective: 理解并验证：电信客户流失预测（含 one-hot 与特征筛选）
---

# 电信客户流失预测（含 one-hot 与特征筛选）

> **学习目标**：能够解释「电信客户流失预测（含 one-hot 与特征筛选）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性回归与梯度下降（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）、概率的基本概念（条件概率、独立事件）、对数运算、混淆矩阵的基本直觉。
>
> **所属主题**：逻辑回归 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""逻辑回归：电信客户流失预测（类别不平衡，用 AUC 与 F1 评估）"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, f1_score,
precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split

CSV = "churn.csv"


def load_and_prepare():
    """读取数据 -> one-hot 编码 -> 删除冗余列 -> 重命名标签"""
    data = pd.read_csv(CSV)
    data = pd.get_dummies(data) # 类别型特征独热编码
    data.drop(["gender_Male", "Churn_No"], axis=1, inplace=True) # 各删一列避免完全共线
    data.rename(columns={"Churn_Yes": "flag"}, inplace=True)
    return data


def step1_basic():
    data = load_and_prepare()
    print(data.info())
    print("标签分布:\n", data.flag.value_counts())
    print("流失占比: %.2f%%" % (100 * data.flag.mean()))
    # 从上面的输出可以看出：属于标签不平衡样本（约 26% 流失）


    def step2_feature_select():
        data = load_and_prepare()
        # 用分组柱状图观察 Contract_Month 与流失的关系
        sns.countplot(data=data, x="Contract_Month", hue="flag")
        plt.title("月度签约与流失的关系")
        plt.show()


        def step3_train_and_evaluate():
            data = load_and_prepare()
            x = data[["Contract_Month", "PaymentElectronic", "internet_other"]]
            y = data["flag"]
            x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=22, stratify=y
            )

            estimator = LogisticRegression(max_iter=1000, class_weight="balanced")
            estimator.fit(x_train, y_train)

            y_pred = estimator.predict(x_test)
            y_score = estimator.predict_proba(x_test)[:, 1]

            print("准确率:", round(accuracy_score(y_test, y_pred), 4))
            print("精确率:", round(precision_score(y_test, y_pred), 4))
            print("召回率:", round(recall_score(y_test, y_pred), 4))
            print("F1 :", round(f1_score(y_test, y_pred), 4))
            print("AUC :", round(roc_auc_score(y_test, y_score), 4))
            print(classification_report(y_test, y_pred, target_names=["不流失", "流失"]))


            if __name__ == "__main__":
                step1_basic()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/04-逻辑回归.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「电信客户流失预测（含 one-hot 与特征筛选）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/04-逻辑回归.md)
