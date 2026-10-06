---
article_id: kp-64e361564b42055d
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 7
learning_objective: 理解并验证：梯度消失与梯度爆炸
---

# 梯度消失与梯度爆炸

> **学习目标**：能够解释「梯度消失与梯度爆炸」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 算法细节

## 本次只学这一点

把递推式(4.63)从第 $l$ 层展开到第 $L$ 层会得到一个**连乘**：$\boldsymbol{\delta}^{(l)}=\prod_{\tau=l}^{L-1}\big[\mathrm{diag}(f_\tau'(\boldsymbol{z}^{(\tau)}))(\boldsymbol{W}^{(\tau+1)})^\top\big]\boldsymbol{\delta}^{(L)}$。记 $\gamma\triangleq\big\|\mathrm{diag}(f'(\boldsymbol{z}))\boldsymbol{W}^\top\big\|$，则误差项随层数大致按 $\gamma^{\,L-l}$ 变化：

- 若 $\gamma<1$，层数一深 $\gamma^{L-l}\to0$，即**梯度消失（vanishing gradient problem）**，浅层几乎收不到有效梯度，整个网络难以训练——这正是 2006 年以前深层网络难以训练、需要用逐层预训练来"救"的根本原因之一；
- 若 $\gamma>1$，$\gamma^{L-l}\to\infty$，即**梯度爆炸（exploding gradient problem）**，参数一步更新就飞出去，损失变成 NaN，训练不稳定。

加速衰减的第二个因素是激活函数的导数：$\sigma'(z)=\sigma(z)(1-\sigma(z))\in[0,0.25]$、$\tanh'(z)=1-\tanh^2(z)\in[0,1]$，两者的导数上界都 $\le 1$（Logistic 甚至只有 $0.25$）；而 Sigmoid 型函数是**两端饱和**的，饱和区导数更趋近 0。于是一层至少衰减到 1/4 甚至更少，几十层之后梯度就"弥散"了。注意梯度消失不是 $\partial\mathcal{L}/\partial\boldsymbol{a}$ 消失，而是远端的 $\partial\mathcal{L}/\partial\boldsymbol{z}$ 变得极小，参数更新几乎只由最后几层决定，长距离依赖学不到（RNN 中即长程依赖问题）。

**为什么 ReLU 能缓解？** $\mathrm{ReLU}(z)=\max(0,z)$ 在 $z>0$ 时导数等于 **1**（左饱和而非两端饱和），误差传递时那个 $f'$ 因子不再打折，$\gamma$ 主要由 $\|\boldsymbol{W}\|$ 决定，只要用 He 初始化等把权重方差控制在 $2/\text{fan\_in}$ 就能让各层尺度稳定。代价是负半轴导数恒为 0，可能出现"死亡 ReLU"（某神经元对所有样本都不激活、梯度永远为 0），所以有 LeakyReLU / ELU / GELU 等变种。

**为什么残差连接能缓解？** 残差单元写作 $\boldsymbol{a}^{(l)}=\boldsymbol{a}^{(l-1)}+F(\boldsymbol{a}^{(l-1)};\theta)$，于是 $\partial \boldsymbol{a}^{(l)}/\partial \boldsymbol{a}^{(l-1)}=\boldsymbol{I}+\partial F/\partial \boldsymbol{a}^{(l-1)}$。单位矩阵项提供了一条**导数为 1 的"梯度高速公路"**，反向传播时梯度可沿直连边原样回传，不必穿过一串会打折的非线性层——这与 LSTM 用内部状态做线性传递、GRU 的线性插值更新是同一思想。**梯度爆炸通常更好处理**：权重衰减（把 $\|\boldsymbol{W}\|$ 压小）或**梯度截断（gradient clipping）**——按模截断 $\boldsymbol{g}\leftarrow\dfrac{\text{threshold}}{\|\boldsymbol{g}\|_2}\boldsymbol{g}$（当 $\|\boldsymbol{g}\|_2>\text{threshold}$），或按值截断 $g\leftarrow\max(\min(g,u),l)$；实践表明截断对阈值并不敏感，一个小阈值就能有效防止发散。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度消失与梯度爆炸」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
