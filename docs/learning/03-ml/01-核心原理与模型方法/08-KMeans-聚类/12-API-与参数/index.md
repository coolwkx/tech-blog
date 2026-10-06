---
article_id: kp-08eec8f49e12db52
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 11
learning_objective: 理解并验证：API 与参数
---

# API 与参数

> **学习目标**：能够解释「API 与参数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 算法细节

## 本次只学这一点

```python
sklearn.cluster.KMeans(
 n_clusters=8, # 簇数 K（默认 8）
 init='k-means++', # 初始化方式：'k-means++' 比 'random' 更稳
 n_init=10, # 用不同初始中心跑几次，取 SSE 最小的那次
 max_iter=300, # 单次运行的最大迭代次数
 tol=1e-4, # 收敛阈值
 random_state=None,
)
```

| 成员 | 含义 |
| --- | --- |
| `fit(X)` / `predict(X)` | 计算聚类中心 / 预测每个样本属于哪个簇 |
| `fit_predict(X)` | 先 `fit` 再 `predict`，一步到位 |
| `inertia_` | **SSE 值** |
| `cluster_centers_` | 各质心的坐标，形状 `(n_clusters, n_features)` |
| `labels_` | 每个样本的簇标签 |

| 评估 API | 方向 |
| --- | --- |
| `silhouette_score(X, labels)` | 越大越好 |
| `calinski_harabasz_score(X, labels)` | 越大越好 |
| `KMeans(...).inertia_` | 越小越好（需配合肘部法） |

> **历史坑**：早期 API 名是 `calinski_harabaz_score`（少了一个 `s`），已被废弃；现在必须用 `calinski_harabasz_score`。同理 `sklearn.datasets.samples_generator` 已废弃，应改为 `sklearn.datasets`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「API 与参数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
