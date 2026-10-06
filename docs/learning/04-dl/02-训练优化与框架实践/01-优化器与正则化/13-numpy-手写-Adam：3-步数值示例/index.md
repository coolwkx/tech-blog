---
article_id: kp-5622c60e08ec03e0
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 12
learning_objective: 理解并验证：numpy 手写 Adam：3 步数值示例
---

# numpy 手写 Adam：3 步数值示例

> **学习目标**：能够解释「numpy 手写 Adam：3 步数值示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 可运行示例

## 本次只学这一点

取 $\alpha=0.001,\beta_1=0.9,\beta_2=0.999,\epsilon=10^{-8}$、梯度恒为 $g=0.5$：

| $t$ | $g_t$ | $m_t$ | $v_t$ | $\hat m_t$ | $\hat v_t$ | $\Delta\theta_t$ |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.5 | 0.05 | $2.5\times10^{-4}$ | 0.5 | 0.25 | $-0.001$ |
| 2 | 0.5 | 0.095 | $4.9975\times10^{-4}$ | 0.5 | 0.25 | $-0.001$ |
| 3 | 0.5 | 0.1355 | $7.4925025\times10^{-4}$ | 0.5 | 0.25 | $-0.001$ |

手算第 1 步：$m_1=0.1\times0.5=0.05$，$\hat m_1=0.05/(1-0.9)=0.5$；$v_1=0.001\times0.25=2.5\times10^{-4}$，$\hat v_1=2.5\times10^{-4}/(1-0.999)=0.25$，$\sqrt{\hat v_1}=0.5$，故 $\Delta\theta_1=-0.001\times0.5/0.5=-0.001$。梯度恒定时可证 $\hat m_t\equiv g$、$\hat v_t\equiv g^2$，所以每一步都恰好走 $\alpha$——**Adam 的步长由学习率而非梯度大小决定**。

```python
import numpy as np

def adam(grads, alpha=1e-3, b1=.9, b2=.999, eps=1e-8):
    m = v = theta = 0.0 # 一阶矩 / 二阶矩 / 参数
    for t, g in enumerate(grads, start=1):
        m = b1 * m + (1 - b1) * g # 一阶矩：像动量
        v = b2 * v + (1 - b2) * g * g # 二阶矩：像 RMSprop
        m_hat, v_hat = m / (1 - b1 ** t), v / (1 - b2 ** t) # 偏差修正
        dtheta = -alpha * m_hat / (np.sqrt(v_hat) + eps)
        theta += dtheta
        print(f"t={t} g={g:<5} m={m:.6f} v={v:.3e} m_hat={m_hat:.6f} "
        f"v_hat={v_hat:.6f} dtheta={dtheta:.6f} theta={theta:.6f}")

        adam([0.5, 0.5, 0.5]) # 恒定梯度：每步恰好走 alpha，输出与上表一致
        adam([5.0, 0.05, 5.0]) # 梯度突变：更新幅度依然平稳
```

第二段里 $g$ 从 5.0 掉到 0.05，更新幅度并不同比例塌缩——因为 $g$ 同时进入 $\hat m_t$ 和 $\sqrt{\hat v_t}$，比值被"归一化"了，这就是自适应学习率的本质。对照之下纯 SGD（`theta -= 0.1 * g`）的位移完全被梯度量级主导，所以 SGD 需要小心调学习率，而 Adam 常被当作省心的默认选择。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「numpy 手写 Adam：3 步数值示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
