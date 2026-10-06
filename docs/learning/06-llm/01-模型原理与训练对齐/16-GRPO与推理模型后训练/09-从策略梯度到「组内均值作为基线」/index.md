---
article_id: kp-3c24e45041649bf7
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-d7276d2e491b
learning_sourceId: d7276d2e491b
learning_order: 8
learning_objective: 理解并验证：从策略梯度到「组内均值作为基线」
---

# 从策略梯度到「组内均值作为基线」

> **学习目标**：能够解释「从策略梯度到「组内均值作为基线」」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇（PPO 的四个模型、GAE、KL 惩罚）与第 02 篇（奖励模型与 reward hacking）；对「基线为什么不引入偏差」有印象会更顺。
>
> **所属主题**：-GRPO与推理模型后训练 · 数学推导

## 本次只学这一点

第 01 篇已经证明：对任意只依赖状态的 $b(s)$，

$$\mathbb{E}_{a\sim\pi}\big[b(s)\nabla_\theta\log\pi_\theta(a\mid s)\big]=0$$

所以在策略梯度估计量里减去基线不引入偏差：

$$\nabla_\theta J=\mathbb{E}\Big[\big(Q(s_t,a_t)-b(s_t)\big)\nabla_\theta\log\pi_\theta(a_t\mid s_t)\Big]$$

**在 GRPO 的设定下做两步简化：**

**第一步：把 token 级换成 response 级。** 令 $\gamma=1$（语言生成里通常如此，因为「未来 token」的折扣没有明确语义），且整条回答只获得一个末端奖励 $r$，则对回答中的任意位置 $t$，从该位置起的回报都等于同一个 $r$。于是 $Q(s_t,a_t)=r$ 对所有 $t$ 成立。

**第二步：用组内均值估计基线。** 对某个 prompt $q$，真实基线是 $V(q)=\mathbb{E}_{y\sim\pi(\cdot\mid q)}[r(y)]$，用组内样本均值估计：

$$\hat b(q)=\frac{1}{G}\sum_{j=1}^{G}r_j$$

代入得到优势的朴素形式 $r_i-\hat b(q)$。再做尺度归一化（除以组内标准差）以统一不同 prompt 的尺度，就得到

$$\boxed{\ A_i=\frac{r_i-\operatorname{mean}(\mathbf r)}{\operatorname{std}(\mathbf r)},\qquad \mathbf r=(r_1,\dots,r_G)\ }$$

**这解释了 GRPO 的两个性质：**

| 性质 | 来源 |
|---|---|
| 只依赖同一组内的相对比较 | 均值与标准差都是组内统计量 |
| 整条回答共享一个优势 | 末端奖励 + $\gamma=1$ ⇒ 每个 token 的 $Q$ 相同 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从策略梯度到「组内均值作为基线」」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)
