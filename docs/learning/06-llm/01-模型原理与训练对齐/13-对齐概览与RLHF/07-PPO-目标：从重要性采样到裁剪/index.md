---
article_id: kp-e2df0cd810629b2d
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 6
learning_objective: 理解并验证：PPO 目标：从重要性采样到裁剪
---

# PPO 目标：从重要性采样到裁剪

> **学习目标**：能够解释「PPO 目标：从重要性采样到裁剪」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 数学推导

## 本次只学这一点

**第一步：一次采样、多次更新引出重要性采样。** 采样一次经验需要四个模型各跑一遍前向 + Actor 跑一遍生成，极其昂贵。所以想用同一批经验更新 `ppo_epochs` 次。若用旧策略 $\pi_{\theta_{old}}$ 采的样本去估计新策略 $\pi_\theta$ 的期望，需要用重要性权重 $w_t=\dfrac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)}$：

$$\nabla_\theta J(\theta)=\mathbb{E}_{a_t\sim\pi_{\theta_{old}}}\left[w_t\,A_t\,\nabla_\theta\log\pi_\theta(a_t\mid s_t)\right]$$

**第二步：把梯度还原成损失。** 因为 $\nabla_\theta w_t = w_t\nabla_\theta\log\pi_\theta$，于是 $w_t A_t\nabla_\theta\log\pi_\theta = A_t \nabla_\theta w_t = \nabla_\theta (A_t w_t)$，因此可得目标

$$J_{IS}(\theta)=\mathbb{E}_{a_t\sim\pi_{\theta_{old}}}\left[w_t\,A_t\right]$$

**第三步：给 $w_t$ 加裁剪。** 若 $w_t$ 偏离 1 太多，重要性采样估计的方差会爆炸，甚至把策略带跑偏。PPO 的做法是把 $w_t$ 截断在 $[1-\epsilon,1+\epsilon]$，并取「原始项」与「截断项」中更悲观的那个：

$$L^{CLIP}(\theta)=\mathbb{E}_{t}\left[\min\Big(w_t A_t,\ \operatorname{clip}(w_t,1-\epsilon,1+\epsilon)\,A_t\Big)\right]$$

**为什么取 min？** 分两种情况看：

| 优势符号 | 未截断项的含义 | 截断后的效果 |
|---|---|---|
| $A_t>0$ | 想增大 $w_t$（提高该 token 概率） | 当 $w_t>1+\epsilon$ 时，$\text{clip}=1+\epsilon$ 成为 min，梯度对该样本归零 → 不再过度上调 |
| $A_t<0$ | 想减小 $w_t$（降低该 token 概率） | 当 $w_t<1-\epsilon$ 时，$\text{clip}=1-\epsilon$ 成为 min，梯度归零 → 不再过度下调 |

也就是说，**一旦更新幅度超出 $[1-\epsilon,1+\epsilon]$，这个 token 就不再产生梯度**，等价于「走太远了就停下来」。在实现上等价于对 ratio 做 $\exp$ 后再算：

```text
log_ratio = logprobs - old_logprobs
ratio     = exp(log_ratio)
pg_loss   = -mean( min(advantages * ratio,
                       advantages * clip(ratio, 1-eps, 1+eps)) * mask )
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PPO 目标：从重要性采样到裁剪」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
