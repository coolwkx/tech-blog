---
article_id: kp-5f5423eddd858e9f
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-8321d1237f76
learning_sourceId: 8321d1237f76
learning_order: 8
learning_objective: 理解并验证：KNN 的预测公式化描述
---

# KNN 的预测公式化描述

> **学习目标**：能够解释「KNN 的预测公式化描述」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：KNN 算法 · 算法细节

## 本次只学这一点

1. 计算距离并取最近邻下标集合：$\mathcal{N}_K(\boldsymbol{q}) = \arg\text{K-smallest}_{i}\ d(\boldsymbol{q},\boldsymbol{x}_i)$
2. **分类（多数表决）**：

$$\hat{y} = \arg\max_{c}\ \sum_{i \in \mathcal{N}_K(\boldsymbol{q})} \mathbb{1}[y_i = c]$$

 等价于预测概率 $\hat{p}(c\mid\boldsymbol{q}) = \frac{1}{K}\sum_{i\in\mathcal{N}_K}\mathbb{1}[y_i=c]$，再取最大者。

3. **回归（均值）**：

$$\hat{y} = \frac{1}{K}\sum_{i \in \mathcal{N}_K(\boldsymbol{q})} y_i$$

4. **距离加权版本**（`weights='distance'`）：

$$\hat{y} = \frac{\sum_{i\in\mathcal{N}_K} w_i\, y_i}{\sum_{i\in\mathcal{N}_K} w_i},\qquad w_i = \frac{1}{d(\boldsymbol{q},\boldsymbol{x}_i)}$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/02-KNN算法.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「KNN 的预测公式化描述」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/02-KNN算法.md)
