---
article_id: kp-b2e045a99b3b9bfd
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-a9dec5ff9c41
learning_sourceId: a9dec5ff9c41
learning_order: 3
learning_objective: 理解并验证：长程依赖问题（Long-Term Dependencies）
---

# 长程依赖问题（Long-Term Dependencies）

> **学习目标**：能够解释「长程依赖问题（Long-Term Dependencies）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：多层前馈网络与反向传播、链式法则与 Jacobian、Logistic/Tanh 及其导数、梯度下降与学习率、PyTorch 的 `nn.Module` 与张量维度。
>
> **所属主题**：-RNN与序列模型 · 算法细节

## 本次只学这一点

定义 $\gamma\triangleq\big\|\mathrm{diag}(f'(z_\tau))W^{\top}\big\|$，则 $\|\delta_{t,k}\|\lesssim\gamma^{\,t-k}\|\delta_{t,t}\|$。

- $\gamma>1$：间隔 $t-k\to\infty$ 时 $\gamma^{t-k}\to\infty$ → **梯度爆炸**，损失曲面剧烈震荡甚至数值溢出 NaN；
- $\gamma<1$：$\gamma^{t-k}\to 0$ → **梯度消失**，远距离状态对参数更新几乎没有贡献。

由于 Logistic 导数最大仅 0.25、Tanh 导数最大为 1，且 $\|W\|$ 通常不大，RNN 实践中以梯度消失为主。

**必须强调的易错点**：RNN 里的梯度消失**不是** $\partial\mathcal{L}/\partial W$ 消失了（它由所有时刻求和而来，总还有值），而是 $\partial\mathcal{L}/\partial h_t$（即误差项 $\delta_{t,k}$）随间隔 $t-k$ 增大而消失。后果是参数更新只被当前时刻附近几个状态主导，**长距离状态对参数没有影响**，于是模型"理论上能建模长程依赖，实际上只能学到短期依赖"。

两种症状的解法路线完全不同：

- **梯度爆炸** → 优化手段即可：权重衰减（对参数加 $\ell_1/\ell_2$ 正则，把 $\|W\|$ 压到 $\le 1$）；**梯度截断**（gradient clipping）。按值截断 $g\leftarrow\max(\min(g,\text{max}),\text{min})$；按模截断：若 $\|g\|_2>\eta$ 则 $g\leftarrow\frac{\eta}{\|g\|_2}g$。教材（7.2.4.4 节）指出按模截断是训练 RNN 避免爆炸的有效方法，且对阈值不敏感。
- **梯度消失** → 必须**改模型**：优化技巧无效。最简单想法是让 $h_t=h_{t-1}+\phi(x_t;\theta)$，$\partial h_t/\partial h_{t-1}=I$，梯度不衰减但也就丢掉了反馈边上的非线性；折中且有效的方式是**门控机制**，即 LSTM 与 GRU。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「长程依赖问题（Long-Term Dependencies）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)
