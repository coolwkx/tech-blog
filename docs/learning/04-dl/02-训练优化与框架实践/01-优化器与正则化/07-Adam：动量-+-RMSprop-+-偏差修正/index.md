---
article_id: kp-5d0b0e6b2d7fe979
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 6
learning_objective: 理解并验证：Adam：动量 + RMSprop + 偏差修正
---

# Adam：动量 + RMSprop + 偏差修正

> **学习目标**：能够解释「Adam：动量 + RMSprop + 偏差修正」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

Adam 同时维护梯度的一阶矩（像动量）与二阶矩（像 RMSprop）：$m_t=\beta_1m_{t-1}+(1-\beta_1)g_t$，$v_t=\beta_2v_{t-1}+(1-\beta_2)g_t\odot g_t$。**偏差修正**：由 $m_0=0$ 展开得 $m_t=(1-\beta_1)\sum_{\tau\le t}\beta_1^{\,t-\tau}g_\tau$，权重之和只有 $1-\beta_1^{\,t}$ 而非 1，故梯度平稳时

$$\mathbb E[m_t]=(1-\beta_1^{\,t})\,\mathbb E[g],$$

即 $t$ 小时被严重低估（$\beta_1=0.9,t=1$ 时因子仅 $0.1$；$\beta_2=0.999$ 时二阶矩更严重，$t=1$ 的权重和只有 $0.001$）。因此

$$\hat m_t=\frac{m_t}{1-\beta_1^{\,t}},\qquad \hat v_t=\frac{v_t}{1-\beta_2^{\,t}},\qquad \Delta\theta_t=-\frac{\alpha\,\hat m_t}{\sqrt{\hat v_t}+\epsilon}.$$

一个漂亮性质：**第一步的更新幅度恰好等于 $\alpha$**——$t=1$ 时 $\hat m_1=g_1$、$\hat v_1=g_1^2$，$\hat m_1/\sqrt{\hat v_1}=\mathrm{sign}(g_1)$，于是 $\Delta\theta_1=-\alpha\,\mathrm{sign}(g_1)$。更一般地，只要梯度恒定就有 $\hat m_t\equiv g$、$\hat v_t\equiv g^2$，每步精确走 $\alpha$，这也是 Adam 对学习率尺度不敏感、却可能"步子过大"的原因。

超参数：原论文与主流框架默认 $\beta_1=0.9,\ \beta_2=0.999,\ \epsilon=10^{-8},\ \alpha=10^{-3}$。**教材 7.2.4.3 节写的是 $\beta_2=0.99$，与 Adam 原论文及 PyTorch 默认的 $0.999$ 不一致**；$0.99$ 对非平稳目标响应更快但噪声更大，复现论文结果请以 $0.999$ 为准。学习率也可衰减，如 $\alpha_t=\alpha_0/\sqrt t$；把 NAG 思想塞进 Adam 得到 Nadam。

**梯度截断（gradient clipping）**。RNN 或深网络中梯度偶尔突然爆炸，一步大更新就能把参数甩到很远的坏区域。**按值截断**逐元素限制到 $[a,b]$：$g=\max(\min(g,b),a)$；**按模截断**保持方向、只压缩长度：

$$g\leftarrow g\cdot\frac{\text{threshold}}{\|g\|_2}\quad\text{当}\ \|g\|_2>\text{threshold}.$$

实践中常用**全局范数截断**：所有参数梯度拼成一个向量算总范数，超过阈值就整体等比缩放（保持各层相对比例）。实验发现训练对阈值并不敏感，通常一个较小的阈值效果就很好，但截断必须放在 `loss.backward()` 之后、`optimizer.step` 之前。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Adam：动量 + RMSprop + 偏差修正」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
