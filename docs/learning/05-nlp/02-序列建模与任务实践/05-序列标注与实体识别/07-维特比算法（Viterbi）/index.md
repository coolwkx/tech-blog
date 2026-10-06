---
article_id: kp-9a09f00d0fd29eca
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-00dabbf9e8f9
learning_sourceId: 00dabbf9e8f9
learning_order: 6
learning_objective: 理解并验证：维特比算法（Viterbi）
---

# 维特比算法（Viterbi）

> **学习目标**：能够解释「维特比算法（Viterbi）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的词性标注与 NER 两阶段拆解、概率论基础（条件概率、贝叶斯）、softmax 与交叉熵。
>
> **所属主题**：序列标注与实体识别 · 方法细节

## 本次只学这一点

目标是求 $\arg\max_y P(x, y)$。动态规划定义

$$
\delta_t(j) = \max_{y_1^{t-1}} P\big(y_1^{t-1},\, y_t = j,\, x_1^{t}\big)
$$

即「到时刻 $t$ 停在状态 $j$ 的所有路径中的最大概率」。递推：

$$
\delta_1(j) = \pi_j\, b_j(x_1)
$$

$$
\delta_t(j) = \Big[\max_{i} \delta_{t-1}(i)\, a_{ij}\Big]\, b_j(x_t), \qquad
\psi_t(j) = \arg\max_{i}\ \delta_{t-1}(i)\, a_{ij}
$$

其中 $\psi_t(j)$ 记录「最优前驱状态」用于回溯。终止与回溯：

$$
y_n^* = \arg\max_{j} \delta_n(j), \qquad y_t^* = \psi_{t+1}(y_{t+1}^*)
$$

复杂度 $O(n \cdot K^2)$（$K$ 为状态数）。与穷举 $O(K^n)$ 相比，这是指数级到多项式级的降维——核心在于「最优路径的子路径也是最优的」这一最优子结构性质。

工程实现中一律在**对数域**做（把乘法变加法），避免长序列概率下溢为 0。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「维特比算法（Viterbi）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)
