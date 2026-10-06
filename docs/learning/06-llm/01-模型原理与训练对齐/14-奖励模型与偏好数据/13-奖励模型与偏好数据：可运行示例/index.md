---
article_id: kp-23bd98de5d04bbaa
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-cfbeb0483800
learning_sourceId: cfbeb0483800
learning_order: 12
learning_objective: 理解并验证：-奖励模型与偏好数据：可运行示例
---

# -奖励模型与偏好数据：可运行示例

> **学习目标**：能够解释「-奖励模型与偏好数据：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Sigmoid 与交叉熵、极大似然估计、梯度下降；读过第 01 篇（RLHF 三阶段与四个模型）会更顺。
>
> **所属主题**：-奖励模型与偏好数据 · 可运行示例

## 本次只学这一点

`# 依赖：仅需 numpy（pip install numpy）。这是 Bradley-Terry 奖励模型的纯 numpy 参考实现：用特征向量模拟「隐状态 → 标量分数」，手写梯度并做梯度下降，不依赖 torch。`

```python
# 依赖：pip install numpy
"""Bradley-Terry 奖励模型的最小可运行实现（纯 numpy）。

设定：每个回答用一个 d 维特征向量 h 表示（真实场景中它是语言模型最后一个
token 的隐状态，这里用随机特征模拟）。奖励 r = w·h + b。
损失：-log sigmoid(r_w - r_l)，梯度按 2.3 节手工推导实现。
"""

import numpy as np

rng = np.random.default_rng(0)
D = 8


def true_reward(h):
    """构造一个"真实质量"函数：更符合人类偏好 => 分数更高。"""
    return 1.5 * h[0] - 0.8 * h[1] + 0.3 * h[2]


def make_dataset(n_pairs=400, noise=0.6):
    """生成偏好对：同一 prompt 采样两条回答，模拟一次带噪声的人类标注。

    noise 控制标注者的"分辨力"：noise 越大，标注越接近随机。
    """
    data = []
    for _ in range(n_pairs):
        h_a = rng.normal(size=D)
        h_b = rng.normal(size=D)
        # 标注者认为 a 更好的真实概率（sigmoid 化的质量差）
        p_a_wins = 1.0 / (1.0 + np.exp(-(true_reward(h_a) - true_reward(h_b)) / noise))
        if rng.random() < p_a_wins:
            data.append((h_a, h_b))   # 标注为 "a 更好" => chosen=a, rejected=b
        else:
            data.append((h_b, h_a))   # 标注为 "b 更好" => chosen=b, rejected=a
    return data


def loss_and_grad(params, data):
    """返回 (loss, grads)，params = [w (D,), b (1,)]。"""
    w, b = params[0], params[1]
    n = len(data)
    loss = 0.0
    gw = np.zeros_like(w)
    gb = np.zeros_like(b)
    for h_w, h_l in data:
        r_w = float(w @ h_w + b)
        r_l = float(w @ h_l + b)
        delta = r_w - r_l
        # 数值稳定的 log sigmoid
        if delta >= 0:
            log_sig = -np.log1p(np.exp(-delta))
        else:
            log_sig = delta - np.log1p(np.exp(delta))
        loss -= log_sig
        # 梯度: sigma(r_l - r_w) * (dh_l - dh_w)
        sigma_neg = 1.0 / (1.0 + np.exp(delta))     # = sigma(-delta)
        gw -= sigma_neg * (h_l - h_w)
        # 注意：损失对 b 的梯度为 0（因为只依赖差值），b 不可辨识
    return loss / n, [gw / n, gb / n]


def pairwise_accuracy(params, data):
    w, b = params[0], params[1]
    correct = sum(
        float(w @ h_w + b) > float(w @ h_l + b) for h_w, h_l in data
    )
    return correct / len(data)


def main():
    train = make_dataset(400)
    test = make_dataset(200)

    w = np.zeros(D)
    b = np.array(0.0)
    lr = 0.05
    for step in range(1, 201):
        loss, grads = loss_and_grad([w, b], train)
        w -= lr * grads[0]
        b -= lr * grads[1]
        if step % 50 == 0:
            print(f"step {step:3d}  loss={loss:.4f}  "
                  f"train_acc={pairwise_accuracy([w, b], train):.3f}  "
                  f"test_acc={pairwise_accuracy([w, b], test):.3f}")

    print("\n学到的 w =", np.round(w, 3))
    print("真实权重方向 = [1.5, -0.8, 0.3, 0, 0, 0, 0, 0]  (前三维按比例可见)")
    print("b =", round(float(b), 4), " (理论不可辨识：损失只依赖 w·h 的差值)")

    # 演示 2.3 节的"难例加权"：比较离谱错误与轻微错误的梯度权重
    params = [w, b]
    for name, delta in (("轻微错误 delta=-0.2", -0.2), ("离谱错误 delta=-3.0", -3.0)):
        print(f"\n{name}: sigma(-delta) = {1/(1+np.exp(delta)):.4f}")
    print("=> 判错越离谱，权重越接近 1（最多把学习信号拉满），"
          "但永远不会超过 1，所以不会出现梯度爆炸。")


if __name__ == "__main__":
    main()
```

**这段代码对应到公式的哪一步：**

| 代码 | 公式 |
|---|---|
| `delta = r_w - r_l` | $\Delta=r_\phi(x,y_w)-r_\phi(x,y_l)$ |
| `log_sig`（分段写法） | 数值稳定的 $\log\sigma(\Delta)$ |
| `loss -= log_sig` | 负对数似然 $\mathcal{L}_{RM}$ |
| `sigma_neg = 1/(1+exp(delta))` | 权重 $\sigma(r_l-r_w)$ |
| `gw -= sigma_neg*(h_l-h_w)` | $\nabla_\phi\mathcal{L}$ 的方向 |
| `b` 学不动 | 平移不可辨识（损失只依赖差值） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-奖励模型与偏好数据：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/03-对齐与后训练/02-奖励模型与偏好数据.md)
