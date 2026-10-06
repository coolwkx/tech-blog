---
article_id: kp-d0b0d6c6b06addf9
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-88f79f4f1547
learning_sourceId: 88f79f4f1547
learning_order: 12
learning_objective: 理解并验证：手算一轮 KMeans（验证 2.3 的计算）
---

# 手算一轮 KMeans（验证 2.3 的计算）

> **学习目标**：能够解释「手算一轮 KMeans（验证 2.3 的计算）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
>
> **所属主题**：KMeans 聚类 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""手算一轮 KMeans：分配 -> 更新质心 -> 判断是否收敛"""
import numpy as np

X = np.array([[1, 1], [3, 3], [2, 3], [8, 7], [9, 8],
[10, 8], [8, 7], [6, 6], [2, 2], [9, 1]], dtype=float)
names = list("ABCDEFGHIJ")

centers = np.array([[1, 1], [3, 3]], dtype=float) # P1=A, P2=B


def assign(X, centers):
    """返回每个点到各中心的距离矩阵与归属标签"""
    d = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
    return d, d.argmin(axis=1)


for it in range(1, 8):
    d, labels = assign(X, centers)
    print(f"\n===== 第 {it} 轮 =====")
    for nm, xi, di, lb in zip(names, X, d, labels):
        print(f" {nm}{tuple(xi)}: 到P1={di[0]:6.2f} 到P2={di[1]:6.2f} -> 簇{lb + 1}")

        new_centers = np.array([X[labels == k].mean(axis=0) for k in range(2)])
        sse = sum(((X[labels == k] - new_centers[k]) ** 2).sum() for k in range(2))
        print(" 新质心:", new_centers.round(4).tolist(), " SSE =", round(sse, 4))

        if np.allclose(new_centers, centers):
            print(" >>> 质心不再移动，算法收敛！")
            break
        centers = new_centers

        # 期望第 1 轮：簇1={A,I}，新质心 (1.5,1.5)；
        # 簇2={B,C,D,E,F,G,H,J}，新质心 (6.875,5.375)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「手算一轮 KMeans（验证 2.3 的计算）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/07-KMeans聚类.md)
