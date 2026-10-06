---
article_id: kp-93a472ef6086b503
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-33f370d2f18b
learning_sourceId: 33f370d2f18b
learning_order: 4
learning_objective: 理解并验证：信息熵
---

# 信息熵

> **学习目标**：能够解释「信息熵」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率与信息论中"熵"的直观含义、对数运算 $\log_2$、pandas 的缺失值处理与 `get_dummies`（见 [01-机器学习概述与流程](../../../../../03-ml/01-基础与特征工程/01-机器学习概述与流程.md)）。
>
> **所属主题**：决策树 · 算法细节

## 本次只学这一点

$$H(D) = -\sum_{k=1}^{K}p_k\log_2 p_k,\qquad p_k = \frac{|C_k|}{|D|}$$

**三个经典计算**（原例）：

| 类别分布 | 计算 | 结果 |
| --- | --- | --- |
| $\{\tfrac13,\tfrac13,\tfrac13\}$ | $-\tfrac13\log_2\tfrac13\times 3$ | $1.0986$（最混乱） |
| $\{\tfrac1{10},\tfrac2{10},\tfrac7{10}\}$ | $-\tfrac1{10}\log_2\tfrac1{10}-\tfrac2{10}\log_2\tfrac2{10}-\tfrac7{10}\log_2\tfrac7{10}$ | $0.8018$ |
| $\{1,0,0\}$ | $-1\log_2 1$ | $0$（完全纯） |

**数据 α（ABCDEFGH）vs 数据 β（AAAABBCD）**（引入例）：

- α：8 种字符各出现 1 次，$H(\alpha) = -\sum_{i=1}^{8}\tfrac18\log_2\tfrac18 = 3$ bit；
- β：$A$ 占 $\tfrac12$、$B$ 占 $\tfrac14$、$C,D$ 各占 $\tfrac18$，$H(\beta)=-\tfrac12\log_2\tfrac12-\tfrac14\log_2\tfrac14-2\times\tfrac18\log_2\tfrac18 = 1.75$ bit。

**结论**：$H(\alpha) > H(\beta)$。数据 α 包含的信息种类更多、更不确定；β 更集中、更有序。**"熵越大，系统越混乱；信息越集中，熵越小。"**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/02-经典算法/05-决策树.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「信息熵」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/02-经典算法/05-决策树.md)
