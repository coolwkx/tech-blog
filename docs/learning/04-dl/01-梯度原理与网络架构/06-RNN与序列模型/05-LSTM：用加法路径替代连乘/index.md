---
article_id: kp-d7b2bfcf82ab8688
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-a9dec5ff9c41
learning_sourceId: a9dec5ff9c41
learning_order: 4
learning_objective: 理解并验证：LSTM：用加法路径替代连乘
---

# LSTM：用加法路径替代连乘

> **学习目标**：能够解释「LSTM：用加法路径替代连乘」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：多层前馈网络与反向传播、链式法则与 Jacobian、Logistic/Tanh 及其导数、梯度下降与学习率、PyTorch 的 `nn.Module` 与张量维度。
>
> **所属主题**：-RNN与序列模型 · 算法细节

## 本次只学这一点

LSTM（Hochreiter & Schmidhuber, 1997）引入一条独立的**内部状态**（internal state）$c_t$ 专门做线性循环信息传递，只非线性地输出给外部状态 $h_t$。三个"软门"取值于 $(0,1)$，由 Logistic 函数给出：

$$
\begin{aligned}
\tilde{c}_t &= \tanh\big(W_c x_t + U_c h_{t-1} + b_c\big) &&\text{候选状态}\\
i_t &= \sigma\big(W_i x_t + U_i h_{t-1} + b_i\big) &&\text{输入门：写入多少新信息}\\
f_t &= \sigma\big(W_f x_t + U_f h_{t-1} + b_f\big) &&\text{遗忘门：保留多少旧信息}\\
o_t &= \sigma\big(W_o x_t + U_o h_{t-1} + b_o\big) &&\text{输出门：输出多少内部状态}\\
c_t &= f_t\odot c_{t-1} + i_t\odot \tilde{c}_t\\
h_t &= o_t\odot \tanh(c_t)
\end{aligned}
$$

教材式(6.57)把四个量拼成一次矩阵乘：$[\tilde c_t;i_t;f_t;o_t]=\big[\tanh;\sigma;\sigma;\sigma\big]\big(W[x_t;h_{t-1}]+b\big)$，$W\in\mathbb{R}^{4D\times(M+D)}$——这也是 PyTorch 里 `weight_ih_l0` 形状为 $4D\times M$ 的原因。

**为什么加法能缓解梯度消失（核心推导）**。沿 $c$ 这条路径反传：

$$\frac{\partial c_t}{\partial c_{t-1}}=f_t,\qquad
\frac{\partial c_t}{\partial c_{k}}=\prod_{\tau=k+1}^{t}f_\tau$$

对比 SRN 的 $\prod \mathrm{diag}(f')W^{\top}$，区别有两点：(1) 连乘因子从"矩阵 $W^{\top}$"降级为**对角矩阵** $f_t$，不存在不同维度间的混合放大；(2) $f_t$ 由网络自己学出来，当 $f_t\approx 1$ 时梯度可以近似无损地流过任意多步。这正是"**常数误差传送带**"（constant error carousel）：$c_t$ 与 $c_{t-1}$ 是**线性关系**，误差沿这条线性路径传播不经过激活函数的饱和区。同时 $c_t$ 一路累加输入，故梯度里还多出直接项 $\partial c_t/\partial \tilde c_t=i_t$ 与 $\partial c_t/\partial f_t=c_{t-1}$，即使某条路径衰减，其余路径仍提供信号。

三个门的极端行为也帮助理解：$f_t=0,i_t=1$ 时清空历史、写入候选（但注意 $h_{t-1}$ 仍影响门与候选的计算）；$f_t=1,i_t=0$ 时完全复制上一时刻内容、不写新信息。

**"长短期记忆"名字的含义**：长期记忆 = **网络参数**（训练中学到的经验，更新周期极慢）；短期记忆 = **隐状态**（每个时刻被重写，生命周期极短）。记忆单元 $c_t$ 能抓住某个关键时刻的信息并保持较长时间，其生命周期长于短期记忆、远短于长期记忆，所以是"**长的短期记忆**"。

**遗忘门偏置初始化**：常规初始化参数很小，会让 $f_t=\sigma(W_fx+U_fh+b_f)$ 偏小，即上一时刻信息大部分被丢掉，既难捕捉长程依赖，也会让相邻时刻梯度极小。因此实践中把**遗忘门偏置 $b_f$ 初始化为 1 或 2**（`nn.LSTM` 的 `bias=True` 下 `bias_ih`/`bias_hh` 中对应 $f$ 的那一段），使训练初期 $f_t\approx 0.73\sim 0.88$。

**主要变体**：

| 变体 | 修改 | 效果 |
| --- | --- | --- |
| 无遗忘门 LSTM | $c_t=c_{t-1}+i_t\odot\tilde c_t$ | 最早版本，$c_t$ 单调增长，长序列下**饱和**、性能下降 |
| peephole 连接 | 门额外依赖 $c_{t-1}$：$f_t=\sigma(W_fx_t+U_fh_{t-1}+V_fc_{t-1}+b_f)$（$V$ 为对角阵） | 门能"看到"内部状态，部分任务有效但增加参数 |
| 耦合输入门与遗忘门 | 令 $f_t=1-i_t$，$c_t=(1-i_t)\odot c_{t-1}+i_t\odot\tilde c_t$ | 减少计算量（CIFG），实践中效果相当 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「LSTM：用加法路径替代连乘」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)
