---
article_id: kp-d43da657cc1c856f
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 10
learning_objective: 理解并验证：距离公式的 numpy 实现
---

# 距离公式的 numpy 实现

> **学习目标**：能够解释「距离公式的 numpy 实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""四种距离的 numpy 实现与对比"""
import numpy as np


def euclidean(a, b):
    return np.sqrt(np.sum((a - b) ** 2))


def manhattan(a, b):
    return np.sum(np.abs(a - b))


def chebyshev(a, b):
    return np.max(np.abs(a - b))


def minkowski(a, b, p):
    """p=1 -> 曼哈顿, p=2 -> 欧氏, p->inf -> 切比雪夫"""
    return np.power(np.sum(np.abs(a - b) ** p), 1.0 / p)


if __name__ == "__main__":
    a = np.array([0.0, 0.0])
    b = np.array([3.0, 4.0])
    print("欧氏距离 :", euclidean(a, b)) # 5.0
    print("曼哈顿距离 :", manhattan(a, b)) # 7.0
    print("切比雪夫距离:", chebyshev(a, b)) # 4.0
    for p in (1, 2, 3, 10):
        print(f"闵氏距离 p={p:2d}: {minkowski(a, b, p):.4f}")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「距离公式的 numpy 实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
