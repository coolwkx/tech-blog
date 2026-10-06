---
article_id: kp-287875c750b310a6
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 6
learning_objective: 理解并验证：关键一步：写出最优策略的闭式解
---

# 关键一步：写出最优策略的闭式解

> **学习目标**：能够解释「关键一步：写出最优策略的闭式解」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

**第一步：把 KL 展开成可逐点处理的期望。**

$$D_{KL}\big(\pi\|\pi_{\text{ref}}\big)=\mathbb{E}_{y\sim\pi}\Big[\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]$$

代入目标：

$$J(\pi)=\mathbb{E}_{y\sim\pi}\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]=\sum_y \pi(y\mid x)\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]$$

**第二步：把「求最优分布」变成一个逐点的变分问题。** 由于目标是对 $y$ 的可加求和，且 $\pi$ 只需满足 $\sum_y\pi(y\mid x)=1$，可以引入拉格朗日乘子 $\lambda(x)$：

$$\mathcal{L}(\pi,\lambda)=\sum_y \pi(y\mid x)\Big[r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}\Big]+\lambda(x)\Big(\sum_y\pi(y\mid x)-1\Big)$$

**第三步：对每个 $\pi(y\mid x)$ 求偏导并令其为 0。**

$$\frac{\partial\mathcal{L}}{\partial\pi(y\mid x)}=r(x,y)-\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}-\beta+\lambda(x)=0$$

**第四步：解出 $\pi$。** 移项整理：

$$\beta\log\frac{\pi(y\mid x)}{\pi_{\text{ref}}(y\mid x)}=r(x,y)+\lambda(x)-\beta$$

$$\pi(y\mid x)=\pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}\big[r(x,y)+\lambda(x)-\beta\big]\Big)$$

把与 $y$ 无关的因子 $\exp\big(\frac{\lambda(x)-\beta}{\beta}\big)$ 吸收进归一化常数，定义配分函数

$$Z(x)=\sum_y \pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}r(x,y)\Big)$$

就得到

$$\boxed{\ \pi^*(y\mid x)=\frac{1}{Z(x)}\,\pi_{\text{ref}}(y\mid x)\exp\!\Big(\frac{1}{\beta}r(x,y)\Big)\ }$$

**这就是「Gibbs 分布形式」的最优策略：以参考分布为底，按奖励的指数做重加权。** 三个直观含义：

1. $\beta\to\infty$ 时指数项趋于均匀，$\pi^*\to\pi_{\text{ref}}$：惩罚太贵，索性不动。
2. $\beta\to 0$ 时指数项极端放大，$\pi^*$ 把全部质量压到 $\arg\max_y r(x,y)$：奖励至上。（这也解释了为什么 $\beta$ 是温度的角色。）
3. $\lambda(x)$ 被吸收进 $Z(x)$ 后消失了，**说明最优策略与「奖励的绝对水平」无关，只与奖励的相对形状有关**。

**注意 $Z(x)$ 的代价**：它需要对整个词表/整个回答空间求和，实际不可计算。DPO 的巧妙之处就在于后面会把它约掉。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键一步：写出最优策略的闭式解」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
