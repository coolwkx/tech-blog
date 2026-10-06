---
article_id: kp-06a11ae09b47dfc3
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-91e7f327ca9f
learning_sourceId: 91e7f327ca9f
learning_order: 14
learning_objective: 理解并验证：-对齐概览与RLHF：可运行示例
---

# -对齐概览与RLHF：可运行示例

> **学习目标**：能够解释「-对齐概览与RLHF：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与自回归语言模型、交叉熵与最大似然、softmax 与对数概率、梯度的基本概念；了解「SFT 微调」是什么。有强化学习的策略（policy）与奖励（reward）概念更好，没有也能读，本文把需要的部分从头推导。
>
> **所属主题**：-对齐概览与RLHF · 可运行示例

## 本次只学这一点

`# 依赖：仅需 numpy（pip install numpy）。本机无 GPU/torch，以下实现是纯 numpy 的「按公式重写」，用于校验公式与数值，不是完整训练器。`

下面这段代码把 2.4–2.6 的公式全部落成可执行的计算：接受一组手工构造的 log 概率与奖励，打印 reward 设计、GAE 优势、returns、裁剪后的 actor loss 与 critic loss。

```python
# 依赖：pip install numpy
"""RLHF-PPO 损失函数的纯 numpy 参考实现（逐项对照公式，非完整训练器）。

设计约定（与常见 RLHF 实现一致）：
- 只考虑 response 部分的 token；最后一个有效 token 位置获得 reward model 分数。
- 即时奖励 R_t = -kl_ctl * (logp - ref_logp)，仅 t==T 时额外加上 clip 后的 rm 分数。
- 优势用 GAE 从后往前递推；actor loss 用 PPO-clip；critic loss 用 value-clip。
"""

import numpy as np


def compute_rewards(logp, ref_logp, rm_score, kl_ctl=0.1,
                    clip_reward_value=5.0):
    """构造每个 token 的即时奖励 R_t。形状均为 (T,)，rm_score 为标量。"""
    kl_penalty = -kl_ctl * (logp - ref_logp)          # 越偏离 ref，惩罚越大
    rewards = kl_penalty.copy()
    rewards[-1] += float(np.clip(rm_score, -clip_reward_value, clip_reward_value))
    return rewards


def gae(values, rewards, gamma=1.0, lam=0.95):
    """从后往前递推 GAE 优势与实际收益(returns)。

    delta_t = R_t + gamma * V_{t+1} - V_t
    A_t     = delta_t + gamma * lam * A_{t+1},  A_T = delta_T
    returns = A + V
    """
    T = len(rewards)
    advantages = np.zeros(T, dtype=np.float64)
    last = 0.0
    for t in reversed(range(T)):
        next_value = values[t + 1] if t < T - 1 else 0.0
        delta = rewards[t] + gamma * next_value - values[t]
        last = delta + gamma * lam * last
        advantages[t] = last
    returns = advantages + values
    return advantages, returns


def actor_loss(logp, old_logp, advantages, cliprange=0.2):
    """PPO-clip 的 actor loss（取负号后最小化即等价于最大化目标）。"""
    ratio = np.exp(logp - old_logp)
    pg1 = -advantages * ratio
    pg2 = -advantages * np.clip(ratio, 1.0 - cliprange, 1.0 + cliprange)
    return float(np.mean(np.maximum(pg1, pg2)))


def critic_loss(values, old_values, returns, cliprange_value=0.2):
    """Critic 的 value-clip 平方误差 loss。"""
    values_clipped = np.clip(values,
                             old_values - cliprange_value,
                             old_values + cliprange_value)
    vf1 = (values - returns) ** 2
    vf2 = (values_clipped - returns) ** 2
    return float(0.5 * np.mean(np.maximum(vf1, vf2)))


def demo():
    # 一条长度为 4 的 response：故意让第 3 个 token 明显偏离 ref，观察 KL 惩罚
    old_logp = np.array([-1.00, -1.20, -0.80, -2.00])
    logp = np.array([-0.90, -1.10, -2.60, -1.90])   # 第 3 个 token 概率大幅下降
    ref_logp = np.array([-1.05, -1.15, -0.85, -2.05])
    values = np.array([0.10, 0.20, -0.05, 0.30])
    old_values = values.copy()
    rm_score = 1.80

    rewards = compute_rewards(logp, ref_logp, rm_score)
    adv, returns = gae(values, rewards)

    print("R_t      =", np.round(rewards, 4))
    print("A_t      =", np.round(adv, 4))
    print("returns  =", np.round(returns, 4))
    print("ratio    =", np.round(np.exp(logp - old_logp), 4))
    print("L_actor  =", round(actor_loss(logp, old_logp, adv), 6))
    print("L_critic =", round(critic_loss(values, old_values, returns), 6))

    # 反事实检查 1：把第 3 个 token 的偏离抹掉，KL 惩罚应变小、优势应变大
    logp2 = logp.copy()
    logp2[2] = ref_logp[2]
    rewards2 = compute_rewards(logp2, ref_logp, rm_score)
    adv2, _ = gae(values, rewards2)
    print("\n[对照] 消除第3个token偏离后:")
    print("R_t      =", np.round(rewards2, 4))
    print("A_t      =", np.round(adv2, 4))

    # 反事实检查 2：把 kl_ctl 调大 10 倍，看总奖励被压低多少
    for k in (0.0, 0.1, 1.0):
        r = compute_rewards(logp, ref_logp, rm_score, kl_ctl=k)
        a, _ = gae(values, r)
        print(f"\nkl_ctl={k:<4} sum(R)={r.sum(): .4f}  A_0={a[0]: .4f}")


if __name__ == "__main__":
    demo()
```

**运行后可以观察到的三点规律（由公式直接决定，不需要训练）：**

1. 第 3 个 token 的 $\log\pi_\theta$ 从 $-0.80$ 掉到 $-2.60$，偏离 Reference 变大，故该位置的 $R_3=-\beta_{KL}(\log\pi_\theta-\log\pi_{\text{ref}})$ 变得很负，进而通过 GAE 影响它之前的优势。
2. 把该位置的偏离抹平后，$R_t$ 整体抬升，优势随之变大——这直观展示了 KL 惩罚「扣分」的作用。
3. `kl_ctl` 从 0 增到 1.0，`sum(R)` 单调下降。**这就是 $\beta_{KL}$ 调大时训练信号变弱、更新更保守的数值表现**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-对齐概览与RLHF：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/01-对齐概览与RLHF.md)
