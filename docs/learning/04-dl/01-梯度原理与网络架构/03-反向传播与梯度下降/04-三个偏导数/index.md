---
article_id: kp-fb1673417ea1e793
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 3
learning_objective: 理解并验证：三个偏导数
---

# 三个偏导数

> **学习目标**：能够解释「三个偏导数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 算法细节

## 本次只学这一点

**（1）$\partial \boldsymbol{z}^{(l)}/\partial w^{(l)}_{ij}$**：因为 $z^{(l)}_k=\sum_j w^{(l)}_{kj}a^{(l-1)}_j+b^{(l)}_k$，只有 $k=i$ 的那一项对 $w^{(l)}_{ij}$ 敏感，且系数正好是 $a^{(l-1)}_j$，于是

$$\frac{\partial z^{(l)}_k}{\partial w^{(l)}_{ij}}=\begin{cases}a^{(l-1)}_j,&k=i\\[2pt]0,&k\ne i\end{cases}\quad\Longrightarrow\quad \frac{\partial \boldsymbol{z}^{(l)}}{\partial w^{(l)}_{ij}}=\mathbb{I}_i\big(a^{(l-1)}_j\big)\in\mathbb{R}^{1\times M_l},$$

其中 $\mathbb{I}_i(\cdot)$ 表示只有第 $i$ 个元素非零的行向量（教材公式 4.54）。注意 $z^{(l)}$ 只依赖第 $l-1$ 层的激活值，与本层激活函数无关。

**（2）$\partial \boldsymbol{z}^{(l)}/\partial \boldsymbol{b}^{(l)}=\boldsymbol{I}$**：$z^{(l)}_i$ 对 $b^{(l)}_i$ 的偏导是 1、对其它偏置是 0，所以 Jacobian 是 $M_l\times M_l$ 的单位矩阵（教材公式 4.55）。这说明**偏置不参与任何"混合"，它只影响自己那一个神经元**，这也是偏置梯度形式更简单的原因。

**（3）误差项 $\boldsymbol{\delta}^{(l)}=\partial\mathcal{L}/\partial\boldsymbol{z}^{(l)}$ 的反向递推**（教材公式 4.56）：从 $\boldsymbol{\delta}^{(l+1)}$ 到 $\boldsymbol{\delta}^{(l)}$ 中间隔着两条边，正好对应两步链式法则——$\boldsymbol{z}^{(l+1)}=\boldsymbol{W}^{(l+1)}\boldsymbol{a}^{(l)}+\boldsymbol{b}^{(l+1)}$ 与 $\boldsymbol{a}^{(l)}=f_l(\boldsymbol{z}^{(l)})$。两个局部 Jacobian 是

$$\frac{\partial \boldsymbol{z}^{(l+1)}}{\partial \boldsymbol{a}^{(l)}}=\boldsymbol{W}^{(l+1)}\in\mathbb{R}^{M_{l+1}\times M_l},\qquad \frac{\partial \boldsymbol{a}^{(l)}}{\partial \boldsymbol{z}^{(l)}}=\mathrm{diag}\big(f_l'(\boldsymbol{z}^{(l)})\big)\in\mathbb{R}^{M_l\times M_l},$$

第二个式子成立是因为 $f$ 逐元素作用（$a_i=f(z_i)$ 只依赖 $z_i$，故 Jacobian 为对角阵）。把三段乘起来：

$$\boldsymbol{\delta}^{(l)}=\frac{\partial \boldsymbol{a}^{(l)}}{\partial \boldsymbol{z}^{(l)}}\cdot\frac{\partial \boldsymbol{z}^{(l+1)}}{\partial \boldsymbol{a}^{(l)}}\cdot\frac{\partial \mathcal{L}}{\partial \boldsymbol{z}^{(l+1)}}=\mathrm{diag}\big(f_l'(\boldsymbol{z}^{(l)})\big)\big(\boldsymbol{W}^{(l+1)}\big)^\top\boldsymbol{\delta}^{(l+1)}=f_l'\big(\boldsymbol{z}^{(l)}\big)\odot\Big(\big(\boldsymbol{W}^{(l+1)}\big)^\top\boldsymbol{\delta}^{(l+1)}\Big)\tag{4.63}$$

其中 $\odot$ 为逐元素相乘（Hadamard 积）。分量形式最能看出含义：$\delta^{(l)}_i=f_l'\big(z^{(l)}_i\big)\sum_{k}w^{(l+1)}_{ki}\delta^{(l+1)}_k$，即**第 $l$ 层某个神经元的误差项，等于所有与它相连的第 $l+1$ 层神经元的误差项按连接权重加权求和，再乘上它自己激活函数的导数**。加权和说明"我的错误有多少来自下游"，$f'$ 说明"我的输出还有多灵敏"。由于 $\boldsymbol{\delta}^{(l)}$ 只依赖 $\boldsymbol{\delta}^{(l+1)}$，可以从 $l=L$ 一路倒推到 $l=1$——这就是"误差的反向传播"这个名字的由来。

**输出层的起点（Softmax + 交叉熵）**：设 $\boldsymbol{z}^{(L)}$ 为 logits，$p_k=e^{z_k}/\sum_j e^{z_j}$，$\mathcal{L}=-\sum_k y_k\log p_k$（$\boldsymbol{y}$ 为 one-hot）。因为 $\partial p_k/\partial z_m=p_k(\mathbb{1}[k=m]-p_m)$，所以

$$\frac{\partial \mathcal{L}}{\partial z_m}=-\sum_k\frac{y_k}{p_k}p_k(\mathbb{1}[k=m]-p_m)=-y_m+p_m\sum_k y_k=p_m-y_m\ \Longrightarrow\ \boldsymbol{\delta}^{(L)}=\hat{\boldsymbol{y}}-\boldsymbol{y}.$$

预测减真值，形式极其干净——这也是交叉熵比平方误差更适合配合 Softmax 的原因：它把 Softmax 的 Jacobian "约掉"了。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三个偏导数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
