---
article_id: kp-f5a71fb78b1fe373
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-cfbeb0483800
learning_sourceId: cfbeb0483800
learning_order: 5
learning_objective: 理解并验证：Bradley-Terry 模型与偏好概率
---

# Bradley-Terry 模型与偏好概率

> **学习目标**：能够解释「Bradley-Terry 模型与偏好概率」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Sigmoid 与交叉熵、极大似然估计、梯度下降；读过第 01 篇（RLHF 三阶段与四个模型）会更顺。
>
> **所属主题**：-奖励模型与偏好数据 · 数学推导

## 本次只学这一点

Bradley-Terry 模型假设：每个「被比较对象」$i$ 有一个潜在的强度参数 $\pi_i>0$，则在 $i$ 与 $j$ 的比较中 $i$ 获胜的概率为

$$P(i \succ j)=\frac{\pi_i}{\pi_i+\pi_j}$$

把「强度」替换成「指数化的奖励 $e^{r(x,y)}$」，即令 $\pi_i=e^{r(x,y_i)}$，立刻得到

$$P\big(y_w\succ y_l\mid x\big)=\frac{e^{r(x,y_w)}}{e^{r(x,y_w)}+e^{r(x,y_l)}}=\frac{1}{1+e^{-\left(r(x,y_w)-r(x,y_l)\right)}}=\sigma\Big(r(x,y_w)-r(x,y_l)\Big)$$

**这一步是整个 RM 训练的源头：只要假设「奖励越高越可能被偏好」且奖励对比较的影响是乘性的，偏好概率就必然是奖励之差的 sigmoid。** 注意一个重要推论：$\sigma$ 只看奖励的**差值**，因此奖励的绝对平移是不可辨识的——这也解释了为什么 RM 的绝对分数没有意义，只有同一 prompt 内的相对大小有意义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Bradley-Terry 模型与偏好概率」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)
