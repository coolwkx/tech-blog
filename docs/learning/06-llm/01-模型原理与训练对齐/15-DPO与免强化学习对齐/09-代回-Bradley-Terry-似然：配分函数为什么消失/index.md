---
article_id: kp-d2854b31426dffb7
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 8
learning_objective: 理解并验证：代回 Bradley-Terry 似然：配分函数为什么消失
---

# 代回 Bradley-Terry 似然：配分函数为什么消失

> **学习目标**：能够解释「代回 Bradley-Terry 似然：配分函数为什么消失」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 数学推导

## 本次只学这一点

第 02 篇给出的偏好概率（用隐式奖励替换真实奖励）：

$$p\big(y_w\succ y_l\mid x\big)=\sigma\Big(r(x,y_w)-r(x,y_l)\Big)=\sigma\Big(\hat r_\theta(x,y_w)+\beta\log Z(x)-\hat r_\theta(x,y_l)-\beta\log Z(x)\Big)$$

**两个 $\beta\log Z(x)$ 直接相消**：

$$p\big(y_w\succ y_l\mid x\big)=\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\Big)$$

**这就是配分函数消失的原因**：它只依赖 $x$，而成对比较恰恰只比较同一 $x$ 下的两条回答。**如果偏好数据跨 prompt 配对，这个消去就不成立，DPO 的理论基础也随之破裂**——这是 DPO 数据必须同 prompt 配对的硬性原因（与 RM 训练完全相同）。

对数据集取负对数似然，得到 DPO 损失：

$$\boxed{\ \mathcal{L}_{DPO}(\theta)=-\,\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}\left[\log\sigma\!\left(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\right)\right]\ }$$

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「代回 Bradley-Terry 似然：配分函数为什么消失」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
