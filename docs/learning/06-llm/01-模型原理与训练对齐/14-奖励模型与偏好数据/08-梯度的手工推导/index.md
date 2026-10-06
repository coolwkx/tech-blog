---
article_id: kp-24e70b2494f18362
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-cfbeb0483800
learning_sourceId: cfbeb0483800
learning_order: 7
learning_objective: 理解并验证：梯度的手工推导
---

# 梯度的手工推导

> **学习目标**：能够解释「梯度的手工推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Sigmoid 与交叉熵、极大似然估计、梯度下降；读过第 01 篇（RLHF 三阶段与四个模型）会更顺。
>
> **所属主题**：-奖励模型与偏好数据 · 数学推导

## 本次只学这一点

记 $\Delta=r_\phi(x,y_w)-r_\phi(x,y_l)$。利用 $\frac{d}{d\Delta}\log\sigma(\Delta)=1-\sigma(\Delta)=\sigma(-\Delta)$ 以及链式法则：

$$\nabla_\phi\Big[-\log\sigma(\Delta)\Big]=-\big(1-\sigma(\Delta)\big)\nabla_\phi\Delta=-\sigma(-\Delta)\Big(\nabla_\phi r_\phi(x,y_w)-\nabla_\phi r_\phi(x,y_l)\Big)$$

即

$$\boxed{\ \nabla_\phi \mathcal{L}=\sigma\Big(r_\phi(x,y_l)-r_\phi(x,y_w)\Big)\Big(\nabla_\phi r_\phi(x,y_l)-\nabla_\phi r_\phi(x,y_w)\Big)\ }$$

**这个梯度非常直观**：权重 $\sigma(r_l-r_w)$ 就是「模型当前判错的程度（错得越离谱越接近 1）」；梯度方向是「拉高 $y_w$ 的分数、拉低 $y_l$ 的分数」。于是训练会自动把注意力集中在难例上——这与逻辑回归的梯度形式完全一致。

**由梯度可以推出三个工程结论：**

1. **零初始化不好**：若 $r_\phi$ 初始输出对所有输入都相同，则 $\Delta=0$，$\sigma(0)=0.5$，权重非零，梯度不为零，训练可以起步；但若用「只在 $y_w$ 上算 SFT 损失」这种退化目标，特权信息就浪费了。强制 $r_\phi(y_w)=r_\phi(y_l)$（例如把两者拼成同一个序列）会让梯度恒为 0。
2. **必须同 prompt 配对**：如果 $y_w$ 来自任务 A、$y_l$ 来自任务 B，那么「奖励差」里混进了「任务难度差」，RM 会学成「任务 A 比任务 B 好」而非「这条回答比那条好」。**这是偏好数据最常见的构造错误。**
3. **损失对分数只依赖差值**：所以在训练 RM 时不需要也不应做绝对值的回归目标（比如「这条打 4 分」）；混入绝对分数会让尺度不可辨识，反而破坏 RL 阶段优势的稳定性。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度的手工推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)
