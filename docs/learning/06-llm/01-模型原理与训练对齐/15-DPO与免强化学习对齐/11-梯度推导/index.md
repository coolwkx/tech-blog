---
article_id: kp-f415619344983d59
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 10
learning_objective: 理解并验证：梯度推导
---

# 梯度推导

> **学习目标**：能够解释「梯度推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

记

$$u=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}$$

则 $\mathcal{L}=-\log\sigma(u)$，且 $\frac{\partial\mathcal{L}}{\partial u}=-\sigma(-u)$。又

$$\frac{\partial u}{\partial\theta}=\beta\Big(\nabla_\theta\log\pi_\theta(y_w\mid x)-\nabla_\theta\log\pi_\theta(y_l\mid x)\Big)$$

（$\pi_{\text{ref}}$ 与 $\theta$ 无关，所以它的项在求导时消失。）于是

$$\boxed{\ \nabla_\theta\mathcal{L}_{DPO}=-\,\beta\,\underbrace{\sigma\big(\hat r_\theta(x,y_l)-\hat r_\theta(x,y_w)\big)}_{\text{权重 }w}\Big(\nabla_\theta\log\pi_\theta(y_w\mid x)-\nabla_\theta\log\pi_\theta(y_l\mid x)\Big)\ }$$

**逐项解读这个梯度：**

| 因子 | 含义 |
|---|---|
| $w=\sigma\big(\hat r_\theta(y_l)-\hat r_\theta(y_w)\big)$ | 模型当前把顺序判错的程度；判得越准越小，判错越大越接近 1 —— 自动形成难例加权 |
| $\nabla_\theta\log\pi_\theta(y_w\mid x)$ | 提高好回答的对数概率 |
| $-\nabla_\theta\log\pi_\theta(y_l\mid x)$ | 降低坏回答的对数概率 |
| $\beta$ | 整体缩放：$\beta$ 越小，梯度幅度越小（因为 $u$ 被缩小），但**允许达到的偏移更大**（因为达到同样 $w$ 需要的对数比更大） |

**关键洞察**：梯度里**没有**任何「整体提高 chosen 概率」的显式项，只有「提高 chosen 相对于 rejected 的对数概率」。因此当 chosen 与 rejected 内容高度重合（只差一个 token 或一句话）时，DPO 可能同时压低两者的绝对概率，只是把 rejected 压得更低——这就是 2.7 节要讨论的失效模式。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
