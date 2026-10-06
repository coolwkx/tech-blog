---
article_id: kp-8ec964e4657e7c37
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-d7276d2e491b
learning_sourceId: d7276d2e491b
learning_order: 17
learning_objective: 理解并验证：-GRPO与推理模型后训练：可运行示例
---

# -GRPO与推理模型后训练：可运行示例

> **学习目标**：能够解释「-GRPO与推理模型后训练：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇（PPO 的四个模型、GAE、KL 惩罚）与第 02 篇（奖励模型与 reward hacking）；对「基线为什么不引入偏差」有印象会更顺。
>
> **所属主题**：-GRPO与推理模型后训练 · 可运行示例

## 本次只学这一点

`# 依赖：仅需 numpy（pip install numpy）。实现包含三个部分：组内归一化优势估计、GRPO 裁剪损失（含 k3 KL 估计）、以及在「奖励可验证」的模拟环境下验证「全对/全错组无梯度」。`

```python
# 依赖：pip install numpy
"""GRPO 的优势估计与损失（纯 numpy 实现，逐项对照公式）。

模拟设定：每个 prompt 有难度 p（答对概率），奖励是 0/1 的可验证奖励。
策略用"每个 prompt 下每个回答的 logit"表示，概率经 softmax 归一化。
"""

import numpy as np

EPS_CLIP = 0.2
BETA_KL = 0.01


def group_advantages(rewards, eps=1e-8):
    """A_i = (r_i - mean(r)) / (std(r) + eps)，返回 (A, mean, std)。

    rewards: 形状 (G,) 的同一 prompt 下的 G 个回答得分。
    """
    r = np.asarray(rewards, dtype=np.float64)
    mean = r.mean()
    std = r.std()                      # 总体标准差（除以 G）
    adv = (r - mean) / (std + eps)
    return adv, mean, std


def kl_k3(logp_theta, logp_ref):
    """Schulman k3 估计: w - 1 - log w，其中 w 取 ratio = pi_theta / pi_ref。

    这里以"对数概率"为输入，等价地写成 exp(d) - 1 - d，d = logp_theta - logp_ref。
    该估计恒非负（由 log w <= w - 1 可得）。
    """
    d = logp_theta - logp_ref
    return np.exp(d) - 1.0 - d


def grpo_loss(logp_theta, logp_old, logp_ref, adv,
              clip_eps=EPS_CLIP, beta_kl=BETA_KL):
    """按回答内部先按 token 平均、再对 G 个回答平均的 GRPO 损失（取负号待最小化）。

    logp_theta / logp_old / logp_ref: 形状 (G, T) 的对数概率
    adv: 形状 (G,) 的组内归一化优势
    """
    ratio = np.exp(logp_theta - logp_old)
    unclipped = ratio * adv[:, None]
    clipped = np.clip(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * adv[:, None]
    per_response = np.minimum(unclipped, clipped).mean(axis=1)   # 回答内 token 平均
    pg_term = per_response.mean()                                # G 个回答等权平均
    kl_term = kl_k3(logp_theta, logp_ref).mean()
    return -(pg_term - beta_kl * kl_term), pg_term, kl_term


def simulate_group(p, G, rng):
    """模拟一个 prompt 的 G 个回答：以概率 p 答对，奖励 0/1。"""
    return (rng.random(G) < p).astype(np.float64)


def dead_group_probability(p, G):
    """全对或全错的概率 = p^G + (1-p)^G（由 2.2 节推导）。"""
    return p ** G + (1.0 - p) ** G


def main():
    rng = np.random.default_rng(7)

    # ---------- 演示 1: 组内归一化 ----------
    print("=== 演示 1: 组内优势估计 ===")
    for rewards in ([1, 1, 0, 1], [0, 0, 0, 0], [1, 1, 1, 1], [1, 0, 0, 0]):
        a, m, s = group_advantages(rewards)
        print(f"rewards={rewards}  mean={m:.3f} std={s:.3f}  A={np.round(a, 4)}")
    print("=> 全对/全错的组 advantage 恒为 0，该 prompt 不产生梯度\n")

    # ---------- 演示 2: 死组概率 ----------
    print("=== 演示 2: 全对/全错（无梯度）的概率 p^G + (1-p)^G ===")
    header = "   p   |" + "".join(f"  G={G:<3}" for G in (4, 8, 16, 64))
    print(header)
    for p in (0.1, 0.3, 0.5, 0.7, 0.9, 0.99):
        row = f" {p:<5} |" + "".join(
            f"  {dead_group_probability(p, G):<5.3f}" for G in (4, 8, 16, 64)
        )
        print(row)
    print("=> 提高 G 可降低死组比例；但 p 接近 0 或 1 时，G 再大也没用，"
          "必须做难度筛选\n")

    # ---------- 演示 3: 一次 GRPO 更新 ----------
    print("=== 演示 3: 单步 GRPO 损失计算 ===")
    G, T = 4, 3
    logp_old = np.log(np.full((G, T), 0.4))
    logp_theta = logp_old + rng.normal(scale=0.05, size=(G, T))
    logp_ref = np.log(np.full((G, T), 0.4))
    rewards = np.array([1.0, 1.0, 0.0, 1.0])
    adv, m, s = group_advantages(rewards)
    loss, pg, kl = grpo_loss(logp_theta, logp_old, logp_ref, adv)
    print(f"rewards      = {rewards}")
    print(f"advantages   = {np.round(adv, 4)}")
    print(f"ratio(mean)  = {np.exp(logp_theta - logp_old).mean():.5f}")
    print(f"pg_term      = {pg:.6f}   (裁剪后的重要性采样项)")
    print(f"kl_term(k3)  = {kl:.6f}   (恒非负)")
    print(f"total loss   = {loss:.6f}  = -(pg - beta*kl)")

    # ---------- 演示 4: k3 KL 的恒非负性 ----------
    print("\n=== 演示 4: k3 估计 w-1-log w 恒非负 ===")
    for d in (-2.0, -0.5, 0.0, 0.5, 2.0):
        print(f"  log(pi_theta/pi_ref)={d:+.1f}  k3={np.exp(d)-1-d:+.6f}")

    # ---------- 演示 5: 死组不产生梯度 ----------
    print("\n=== 演示 5: 全对组的梯度贡献为 0 ===")
    for rewards in ([1, 1, 1, 1], [1, 1, 0, 1]):
        adv, _, _ = group_advantages(rewards)
        loss, pg, _ = grpo_loss(logp_theta, logp_old, logp_ref, adv,
                                beta_kl=0.0)
        print(f"  rewards={rewards}  pg_term={pg:+.6f}")


if __name__ == "__main__":
    main()
```

**代码与公式的对应：**

| 代码 | 公式 |
|---|---|
| `group_advantages` | $A_i=(r_i-\operatorname{mean})/(\operatorname{std}+\varepsilon)$ |
| `kl_k3` | $\hat D_{KL}=w-1-\log w$，恒非负 |
| `ratio = exp(logp_theta - logp_old)` | $w_{i,t}=\pi_\theta/\pi_{\theta_{old}}$ |
| `np.minimum(unclipped, clipped)` | PPO 的 $\min$ 裁剪目标 |
| `per_response.mean()` 再 `.mean()` | 先在回答内按 token 平均、再对 $G$ 个回答平均 |
| `-(pg_term - beta_kl*kl_term)` | GRPO 的完整目标（取负后最小化） |
| `dead_group_probability` | $p^G+(1-p)^G$，全对/全错的概率 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-GRPO与推理模型后训练：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/04-GRPO与推理模型后训练.md)
