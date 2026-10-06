---
article_id: kp-bd2b3535d008e0a3
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-c08205495b15
learning_sourceId: c08205495b15
learning_order: 8
learning_objective: 理解并验证：卷积层的三维结构
---

# 卷积层的三维结构

> **学习目标**：能够解释「卷积层的三维结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：全连接前馈网络与反向传播（第 4 章）、梯度下降与 ReLU、张量的维度概念（NCHW）、numpy/PyTorch 基础张量操作。
>
> **所属主题**：-CNN卷积神经网络 · 算法细节

## 本次只学这一点

图像是二维的，因此把神经元组织成"高 × 宽 × 深度"的三维张量，深度即**特征映射（feature map）**的个数。设输入特征映射组 $\boldsymbol{X}\in\mathbb{R}^{H\times W\times D}$（切片 $X^d\in\mathbb{R}^{H\times W}$，$1\le d\le D$）、输出 $\boldsymbol{Y}\in\mathbb{R}^{H'\times W'\times D'}$（切片 $Y^p$，$1\le p\le D'$）、卷积核 $\boldsymbol{W}\in\mathbb{R}^{K\times K\times D\times D'}$（切片 $W^{p,d}\in\mathbb{R}^{K\times K}$），则

$$Z^p = W^p \otimes \boldsymbol{X} + b^p = \sum_{d=1}^{D} W^{p,d}\otimes X^{d} + b^p,\qquad Y^p = f(Z^p),$$

其中 $f(\cdot)$ 为非线性激活函数，**一般用 ReLU**（左饱和、正区间导数恒为 1，缓解梯度消失，且计算只需加乘与比较）。核心语义：**输出通道 $p$ 必须看完所有输入通道 $d$ 才能算出**——跨通道信息在这里融合；同一个 $p$ 在所有空间位置共享 $W^{p,\cdot}$。每个输出特征映射需要 $D$ 个 $K\times K$ 卷积核加 1 个偏置，共 $D'$ 个输出映射，因此

$$\#\text{params} = K\times K\times D\times D' + D' = (K^2 D + 1)\,D' .$$

| 层 | 输入 | 核 | 输出 | 参数量计算 | 参数量 |
| --- | --- | --- | --- | --- | --- |
| LeNet-5 C1 | $32\times32\times1$ | $5\times5$，6 个 | $28\times28\times6$ | $5\cdot5\cdot1\cdot6+6$ | 156 |
| AlexNet conv1（单卡口径）| $224\times224\times3$ | $11\times11$，64 个 | $55\times55\times64$ | $11\cdot11\cdot3\cdot64+64$ | 23,296 |
| 教材口径：两个 $11\times11\times3\times48$ | $224\times224\times3$ | $11\times11$，$48\times2=96$ 个 | $2\times(55\times55\times48)$ | $11\cdot11\cdot3\cdot96+96$ | 34,944 |
| VGG16 首个卷积层 | $224\times224\times3$ | $3\times3$，64 个 | $224\times224\times64$ | $3\cdot3\cdot3\cdot64+64$ | 1,792 |
| $1\times1$ 降维：$256\to64$ | $100\times100\times256$ | $1\times1$，64 个 | $100\times100\times64$ | $1\cdot1\cdot256\cdot64+64$ | 16,448 |

对照 LeNet-5 的**连接数** $156\times784=122304$（教材数据），而参数量只有 156——这正是权重共享的威力：连接多、参数少。再对照 AlexNet 的三个全连接层：$4096\times(256\cdot6\cdot6+1)\approx 37.7\text{M}$ 个参数，**一个全连接层就比前面所有卷积层加起来还多几十倍**，这也解释了为什么现代网络趋势是减少全连接层、趋向全卷积网络（FCN）。

**感受野的成长**：$s=1$ 的 $L$ 层 $K\times K$ 卷积堆叠后，单个输出神经元的感受野为 $1+L(K-1)$。三层 $3\times3$ 的感受野是 $7\times7$，与一层 $7\times7$ 相当，但参数量 $3\cdot(3^2D^2)=27D^2$ 远小于 $49D^2$，且多了两次非线性——这就是 VGG 全面使用 $3\times3$ 堆叠的理由。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「卷积层的三维结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)
