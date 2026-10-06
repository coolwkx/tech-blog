---
article_id: kp-bbcc8b09a7f88cd4
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 9
learning_objective: 理解并验证：参数学习：经验风险最小化与结构风险最小化
---

# 参数学习：经验风险最小化与结构风险最小化

> **学习目标**：能够解释「参数学习：经验风险最小化与结构风险最小化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 算法细节

## 本次只学这一点

给定训练集 $\mathcal{D}=\{(\boldsymbol x^{(n)},\boldsymbol y^{(n)})\}_{n=1}^{N}$，用**交叉熵损失**（等价于负对数似然）：

$$\mathcal{L}(\boldsymbol y,\hat{\boldsymbol y})=-\boldsymbol y^\top\log\hat{\boldsymbol y}$$

**经验风险（empirical risk）**是训练集上的平均损失，经验风险最小化（ERM）容易过拟合；加上只作用于权重（不含偏置）的 $\ell_2$ 正则项就得到**结构风险最小化（SRM）**：

$$\mathcal{R}(\boldsymbol W,\boldsymbol b)=\frac{1}{N}\sum_{n=1}^{N}\mathcal{L}\big(\boldsymbol y^{(n)},\hat{\boldsymbol y}^{(n)}\big)+\frac{1}{2}\lambda\|\boldsymbol W\|_F^2,\qquad \|\boldsymbol W\|_F^2=\sum_{l=1}^{L}\sum_{i=1}^{M_l}\sum_{j=1}^{M_{l-1}}\big(w_{ij}^{(l)}\big)^2$$

对应到梯度下降的更新式（权重带正则项梯度，偏置不带）：

$$\boldsymbol W^{(l)}\leftarrow\boldsymbol W^{(l)}-\alpha\Big(\frac{1}{N}\sum_{n=1}^{N}\frac{\partial\mathcal{L}^{(n)}}{\partial\boldsymbol W^{(l)}}+\lambda\boldsymbol W^{(l)}\Big),\qquad \boldsymbol b^{(l)}\leftarrow\boldsymbol b^{(l)}-\alpha\,\frac{1}{N}\sum_{n=1}^{N}\frac{\partial\mathcal{L}^{(n)}}{\partial\boldsymbol b^{(l)}}$$

**手推步骤：从输出层误差推出各层梯度（反向传播）**

**手推步骤 1**：定义第 $l$ 层的**误差项** $\boldsymbol\delta^{(l)}\triangleq\dfrac{\partial\mathcal{L}}{\partial\boldsymbol z^{(l)}}\in\mathbb{R}^{M_l}$。它衡量"第 $l$ 层每个神经元对最终损失有多敏感"，也就是**贡献度分配（credit assignment）**问题的答案。

**手推步骤 2**：由 $\boldsymbol z^{(l+1)}=\boldsymbol W^{(l+1)}\boldsymbol a^{(l)}+\boldsymbol b^{(l+1)}$ 与 $\boldsymbol a^{(l)}=f_l(\boldsymbol z^{(l)})$，对 $\boldsymbol z^{(l)}$ 用链式法则，逐元素求导得

$$\frac{\partial\boldsymbol z^{(l+1)}}{\partial\boldsymbol z^{(l)}}=\big(\boldsymbol W^{(l+1)}\big)^\top\mathrm{diag}\big(f_l'(\boldsymbol z^{(l)})\big)\ \Longrightarrow\ \boldsymbol\delta^{(l)}=f_l'\big(\boldsymbol z^{(l)}\big)\odot\Big(\big(\boldsymbol W^{(l+1)}\big)^\top\boldsymbol\delta^{(l+1)}\Big)$$

其中 $\odot$ 是逐元素相乘。它的含义很直观：**第 $l$ 层某神经元的误差项 = 所有与它相连的第 $l+1$ 层神经元误差项的加权和，再乘上该神经元激活函数的导数**。

**手推步骤 3**：把 $\boldsymbol\delta^{(l)}$ 乘上输入即可得参数梯度（外积形式）

$$\frac{\partial\mathcal{L}}{\partial\boldsymbol W^{(l)}}=\boldsymbol\delta^{(l)}\big(\boldsymbol a^{(l-1)}\big)^\top\in\mathbb{R}^{M_l\times M_{l-1}},\qquad \frac{\partial\mathcal{L}}{\partial\boldsymbol b^{(l)}}=\boldsymbol\delta^{(l)}\in\mathbb{R}^{M_l}$$

**手推步骤 4（梯度为什么会消失）**：Logistic 与 Tanh 的导数分别是

$$\sigma'(z)=\sigma(z)\big(1-\sigma(z)\big)\in(0,\ 0.25],\qquad \tanh'(z)=1-\tanh^2(z)\in(0,\ 1]$$

误差每回传一层都要乘一次这样的导数，$L$ 层之后就是 $L$ 个 $\le 0.25$ 的因子连乘，指数级衰减，这就是**梯度消失问题（vanishing gradient problem）**。教材给的缓解办法是换用导数较大、且正半轴导数恒为 1 的激活函数（如 ReLU），以及后续章节的初始化、归一化、门控等技巧。

**手推步骤 5（数值稳定的小技巧）**：直接计算 $\mathrm{softmax}$ 时 $\exp(z_c)$ 容易溢出，实际实现要先减去最大值：

$$\mathrm{softmax}(\boldsymbol z)_c=\frac{\exp(z_c-z_{\max})}{\sum_{c'}\exp(z_{c'}-z_{\max})}$$

同理 $\log\mathrm{softmax}$ 用 log-sum-exp 计算。这也是为什么 PyTorch 的 `nn.CrossEntropyLoss` 直接吃**未经 softmax 的 logits**（内部融合了 log-softmax 与 NLL，梯度仍为 $\hat{\boldsymbol y}-\boldsymbol y$，数值上更稳）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数学习：经验风险最小化与结构风险最小化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
