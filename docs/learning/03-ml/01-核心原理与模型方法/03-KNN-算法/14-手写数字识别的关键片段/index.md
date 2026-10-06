---
article_id: kp-7dde2c0593aedc36
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 13
learning_objective: 理解并验证：手写数字识别的关键片段
---

# 手写数字识别的关键片段

> **学习目标**：能够解释「手写数字识别的关键片段」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 可运行示例

## 本次只学这一点

数据：`手写数字识别.csv`，每行 785 列 = 1 列标签 + 784 个像素（28×28，取值 0~255）。

```python
# -*- coding: utf-8 -*-
"""KNN 手写数字识别：读取 -> 归一化 -> 训练 -> 保存 -> 推理"""
import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

CSV = "手写数字识别.csv"


def show_digit(idx, data):
    """把第 idx 行还原成 28x28 的灰度图"""
    x = data.iloc[:, 1:]
    digit = x.iloc[idx].values.reshape(28, 28)
    plt.axis("off")
    plt.imshow(digit, cmap="gray")
    plt.show()


    def train_model(data):
        x = data.iloc[:, 1:]
        y = data.iloc[:, 0]

        # 归一化：像素值 0~255 -> 0~1（对 KNN 这类基于距离的模型很重要）
        x = x / 255

        # stratify=y：按类别比例分层抽样
        x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=21
        )

        estimator = KNeighborsClassifier(n_neighbors=3)
        estimator.fit(x_train, y_train)
        print("测试集准确率: %.4f" % estimator.score(x_test, y_test))

        joblib.dump(estimator, "knn_digit.pkl")


        def use_model(img_path):
            img = plt.imread(img_path) # 28x28 灰度图
            estimator = joblib.load("knn_digit.pkl")
            img = img / 255.0 # 关键：推理时也要做与训练一致的归一化
            img = img.reshape(1, -1) # (28,28) -> (1,784)
            print("识别结果:", estimator.predict(img))


            if __name__ == "__main__":
                data = pd.read_csv(CSV)
                train_model(data)
```

> **注意**：原代码的 `use_model` 里**没有除以 255**，而训练时做了归一化，导致训练/推理量纲不一致。这里已补上 `img = img / 255.0`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手写数字识别的关键片段」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
