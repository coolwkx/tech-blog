---
article_id: kp-49c2b84d3c280156
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-f5340ad3033e
learning_sourceId: f5340ad3033e
learning_order: 14
learning_objective: 理解并验证：-DPO与免强化学习对齐：可运行示例
---

# -DPO与免强化学习对齐：可运行示例

> **学习目标**：能够解释「-DPO与免强化学习对齐：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Bradley-Terry 模型与排序损失、KL 散度、Sigmoid 与交叉熵、极大似然；读过第 01 篇（RLHF 与 KL 惩罚）和第 02 篇（奖励模型）会非常顺。
>
> **所属主题**：-DPO与免强化学习对齐 · 可运行示例

## 本次只学这一点

`# 依赖：仅需 numpy（pip install numpy）。用 numpy 实现 DPO 损失与梯度并做梯度下降，策略用「对回答的小型表格分布」模拟，以便手算校验，不依赖 torch。`

```python
# 依赖：pip install numpy
"""DPO 损失、梯度与最小训练循环（纯 numpy）。

为便于校验，这里不走语言模型，而是把「策略对某个回答的概率」直接当作
可优化的参数（每个 (prompt, response) 一个 logit，经 softmax 归一化）。
这样 DPO 的每一项都能手工复算。
"""

import numpy as np

BETA = 0.1


def softmax(z):
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()


class ToyPolicy:
    """一个极简的"策略"：每个回答有一个 logit，概率 = 该 prompt 下的 softmax。"""

    def __init__(self, n_prompts, n_responses, seed=0):
        rng = np.random.default_rng(seed)
        self.logits = rng.normal(scale=0.1, size=(n_prompts, n_responses))
        self.ref_logits = self.logits.copy()   # 参考模型：初始策略的冻结副本

    def logp(self, p, r):
        return float(np.log(softmax(self.logits[p])[r]))

    def ref_logp(self, p, r):
        return float(np.log(softmax(self.ref_logits[p])[r]))

    def dlogp_dlogit(self, p, r):
        """d log pi(r|p) / d logit[p, k] = delta_{kr} - pi(k|p)。"""
        probs = softmax(self.logits[p])
        g = -probs
        g[r] += 1.0
        return g


def implicit_reward(policy, p, r, beta=BETA):
    """隐式奖励 r_hat = beta * log( pi_theta(y|x) / pi_ref(y|x) )。"""
    return beta * (policy.logp(p, r) - policy.ref_logp(p, r))


def dpo_loss_and_grad(policy, data, beta=BETA):
    """data: [(prompt_id, chosen_resp_id, rejected_resp_id), ...]"""
    n = len(data)
    total_loss = 0.0
    grad = np.zeros_like(policy.logits)
    for p, y_w, y_l in data:
        rw = implicit_reward(policy, p, y_w, beta)
        rl = implicit_reward(policy, p, y_l, beta)
        u = rw - rl
        # -log sigmoid(u)，数值稳定写法
        if u >= 0:
            loss = np.log1p(np.exp(-u))
        else:
            loss = -u + np.log1p(np.exp(u))
        total_loss += loss
        # 梯度权重 w = sigma(-u)
        w = 1.0 / (1.0 + np.exp(u))
        # dL/dtheta = -beta * w * (dlogpi_w - dlogpi_l)
        grad[p] += (-beta * w) * (
            policy.dlogp_dlogit(p, y_w) - policy.dlogp_dlogit(p, y_l)
        )
    return total_loss / n, grad / n


def accuracy(policy, data, beta=BETA):
    ok = 0
    for p, y_w, y_l in data:
        if implicit_reward(policy, p, y_w, beta) > implicit_reward(policy, p, y_l, beta):
            ok += 1
    return ok / len(data)


def main():
    n_prompts, n_responses = 6, 3
    policy = ToyPolicy(n_prompts, n_responses, seed=1)
    # 数据: 每个 prompt 让 chosen 固定比 rejected 好
    data = [(p, 0, 1) for p in range(n_prompts)] + \
           [(p, 1, 2) for p in range(n_prompts)]

    print("训练前准确率:", round(accuracy(policy, data), 3))
    lr = 0.5
    for step in range(1, 61):
        loss, grad = dpo_loss_and_grad(policy, data)
        policy.logits -= lr * grad
        if step % 15 == 0:
            print(f"step {step:3d}  DPO loss={loss:.4f}  acc={accuracy(policy, data):.3f}")

    print("\n各 prompt 的隐式奖励差 (chosen - rejected):")
    for p, y_w, y_l in data[:6]:
        d = implicit_reward(policy, p, y_w) - implicit_reward(policy, p, y_l)
        print(f"  prompt {p}  chosen={y_w} rejected={y_l}  "
              f"delta_r_hat = {d:+.4f}")

    # ---- 对照实验 1: beta 的影响 ----
    print("\n[对照] beta 对'学得多快/偏多远'的影响 (同样 60 步, lr=0.5):")
    for beta in (0.02, 0.1, 0.5):
        pol = ToyPolicy(n_prompts, n_responses, seed=1)
        for _ in range(60):
            _, g = dpo_loss_and_grad(pol, data, beta=beta)
            pol.logits -= lr * g
        logratio = pol.logp(0, 0) - pol.ref_logp(0, 0)
        dr = implicit_reward(pol, 0, 0, beta) - implicit_reward(pol, 0, 1, beta)
        print(f"  beta={beta:<4} acc={accuracy(pol, data, beta):.3f}  "
              f"log_ratio(chosen)={logratio:+.3f}  delta_r_hat={dr:+.4f}")

    # ---- 对照实验 2: 梯度权重的难例效应 ----
    print("\n[对照] 梯度权重 w = sigmoid(-u):")
    for u in (-3.0, -1.0, 0.0, 1.0, 3.0):
        print(f"  u={u:+.1f} -> w={1/(1+np.exp(u)):.4f}")


if __name__ == "__main__":
    main()
```

**代码与公式的对应关系：**

| 代码 | 公式 |
|---|---|
| `implicit_reward` | $\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{ref}(y\mid x)}$ |
| `u = rw - rl` | $\hat r_\theta(y_w)-\hat r_\theta(y_l)$ |
| 分段 `loss` | 数值稳定的 $-\log\sigma(u)$ |
| `w = 1/(1+exp(u))` | $\sigma(-u)$，DPO 梯度中的动态权重 |
| `grad[p] += -beta*w*(dlogp_w - dlogp_l)` | $\nabla_\theta\mathcal{L}_{DPO}$ |
| 对照实验 1 | 同一 $\beta$ 下 log 比与隐式奖励的此消彼长 |
| 对照实验 2 | 难例加权：$u$ 越负（判错越狠），权重越接近 1 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-DPO与免强化学习对齐：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/03-DPO与免强化学习对齐.md)
