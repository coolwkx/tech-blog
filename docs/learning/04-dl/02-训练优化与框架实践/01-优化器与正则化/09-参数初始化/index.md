---
article_id: kp-d5abdbed60be1151
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 8
learning_objective: 理解并验证：参数初始化
---

# 参数初始化

> **学习目标**：能够解释「参数初始化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

**为什么不能全零**：若 $W=0$（偏置也 0），第一遍前向时同层所有神经元输出完全相同，反向传播收到的梯度也完全相同，于是**永远保持相同**，等价于每层只有一个神经元——这叫**对称权重现象**。（偏置可以置 0，它不破坏对称性；LSTM 遗忘门偏置常初始化为 1 或 2 以增大时序梯度。）

**基于固定方差**：从 $N(0,\sigma^2)$ 或 $U[-r,r]$ 采样，由 $\mathrm{Var}[U]=r^2/3$ 得 $r=\sqrt{3\sigma^2}$。缺点是 $\sigma^2$ 与输入个数、激活函数、层数都无关：太小 → 信号逐层衰减、Sigmoid 落入近似线性区（丢掉非线性）；太大 → 净输入过大、Sigmoid 饱和、梯度消失。因此固定方差初始化一般要配逐层归一化。

**方差缩放（Xavier / Glorot）**。设第 $l$ 层净输入 $z^{(l)}=\sum_{i=1}^{n_{l-1}}w_i^{(l)}x_i^{(l-1)}$，各 $w_i,x_i$ 独立零均值，则

$$\mathrm{Var}\Big[\sum_i w_ix_i\Big]=\sum_i\mathrm{Var}[w_ix_i]=\sum_i\mathrm{Var}[w_i]\mathrm{Var}[x_i]=n_{l-1}\mathrm{Var}[w]\mathrm{Var}[x].$$

**前向**要方差不变需 $n_{l-1}\mathrm{Var}[w]=1$，即 $\mathrm{Var}[w]=1/n_{l-1}$；**反向**误差项 $\delta^{(l-1)}=(W^{(l)})^{\top}\delta^{(l)}$ 同理要求 $\mathrm{Var}[w]=1/n_l$。两者取折中得 $\mathrm{Var}[w^{(l)}]=\frac{2}{n_{l-1}+n_l}$，对应均匀分布区间半径 $\sqrt{6/(n_{l-1}+n_l)}$。推导假设激活为恒等函数，但对 Logistic/Tanh 也适用（参数与输入绝对值小时它们近似线性）；Logistic 线性区斜率约 $0.25$，故实践中常把方差再乘经验因子 $\rho$。**He / Kaiming 初始化**：ReLU 会零掉一半输出、使方差近似减半，故为补偿把方差翻倍：$\mathrm{Var}[w]=2/n_{l-1}$，均匀分布半径 $\sqrt{6/n_{l-1}}$。（高斯分布下 Xavier 的 $\sigma^2=\frac{2}{n_{l-1}+n_l}$、He 的 $\sigma^2=\frac{2}{n_{l-1}}$。）

**一个必须知道的陷阱**：PyTorch `nn.Linear` 的默认初始化是 `kaiming_uniform_(w, a=sqrt(5))`，算出来是 $U[-1/\sqrt{\text{fan\_in}},1/\sqrt{\text{fan\_in}}]$，方差只有 $\frac{1}{3n_{in}}$，即只有 He（$\frac{2}{n_{in}}$）的 $\frac16$。默认值对深层网络往往偏小，**显式指定初始化是常规操作**：

```python
nn.init.xavier_uniform_(w) # Tanh / Sigmoid
nn.init.kaiming_normal_(w, mode='fan_in', nonlinearity='relu') # ReLU 家族
nn.init.orthogonal_(w, gain=math.sqrt(2)) # RNN 循环权重
```

**正交初始化**：逐元素独立采样只在"平均意义"上保持范数，宽度不够时仍可能梯度爆炸/消失。直接要求 $W(W)^{\top}=I$ 就得到**范数保持性（norm-preserving）**：$\|\delta^{(l-1)}\|_2=\|(W^{(l)})^{\top}\delta^{(l)}\|_2=\|\delta^{(l)}\|_2$。实现两步：① 用 $N(0,1)$ 生成方阵；② 做奇异值分解，取 $U$（或 $V$）作为权重。常用于 RNN 循环权重，配 ReLU 时乘增益 $\sqrt2$。**预训练初始化**（加载大规模数据上训好的参数再 fine-tuning）同时提供好起点与正则效果，但灵活性差。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数初始化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
