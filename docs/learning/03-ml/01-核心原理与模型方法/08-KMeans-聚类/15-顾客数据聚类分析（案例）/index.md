---
article_id: kp-cf83c8edd43ce796
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 14
learning_objective: 理解并验证：顾客数据聚类分析（案例）
---

# 顾客数据聚类分析（案例）

> **学习目标**：能够解释「顾客数据聚类分析（案例）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""顾客数据聚类：找到"收入高 + 消费高"的大宗商品客户群"""
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

CSV = "customers.csv"


def main():
    dataset = pd.read_csv(CSV)
    dataset.columns = ["CustomerID", "Gender", "Age", "Annual Income", "Spending Score"]
    print(dataset.info())

    # 只取"年收入"与"消费指数"两个特征做二维可视化聚类
    X = dataset.iloc[:, [3, 4]]
    print(X.head())

    # ---- 第一步：用肘部法 + 轮廓系数确定 K ----
    mysse, mysscore = [], []
    for i in range(2, 11):
        mykmeans = KMeans(n_clusters=i, n_init=10, random_state=0)
        mykmeans.fit(X)
        mysse.append(mykmeans.inertia_)
        mysscore.append(silhouette_score(X, mykmeans.predict(X)))

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].plot(range(2, 11), mysse)
        axes[0].set_title("the elbow method")
        axes[0].set_xlabel("number of clusters")
        axes[0].set_ylabel("SSE")
        axes[0].grid(True)

        axes[1].plot(range(2, 11), mysscore)
        axes[1].set_title("silhouette score")
        axes[1].grid(True)
        plt.show()
        # 结论：肘部法与轮廓系数都显示"聚成 5 类效果最好"

        # ---- 第二步：用 K=5 聚类并可视化 ----
        mykmeans = KMeans(n_clusters=5, n_init=10, random_state=0)
        y_kmeans = mykmeans.fit_predict(X)

        plt.figure(figsize=(10, 7))
        colors = ["red", "blue", "green", "cyan", "magenta"]
        labels = ["Standard", "Traditional", "Normal", "Youth", "TA"]
        for c in range(5):
            plt.scatter(X.values()[y_kmeans == c, 0], X.values()[y_kmeans == c, 1],
            s=100, c=colors[c], label=labels[c])
            plt.scatter(mykmeans.cluster_centers_[:, 0], mykmeans.cluster_centers_[:, 1],
            s=300, c="black", label="Centroids", marker="X")
            plt.title("Clusters of customers")
            plt.xlabel("Annual Income (k$)")
            plt.ylabel("Spending Score (1-100)")
            plt.legend()
            plt.show()

            # ---- 第三步：业务解读 ----
            result = X.copy()
            result["cluster"] = y_kmeans
            print(result.groupby("cluster").mean())
            # 右上角那一簇 = 收入高 + 消费高 => 大宗商品客户群；左下角 = 低收入低消费


            if __name__ == "__main__":
                main()
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「顾客数据聚类分析（案例）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
