---
article_id: kp-9c6bf5fe0e776632
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-c08205495b15
learning_sourceId: c08205495b15
learning_order: 6
learning_objective: 理解并验证：卷积的数学性质（与反向传播的关系）
---

# 卷积的数学性质（与反向传播的关系）

> **学习目标**：能够解释「卷积的数学性质（与反向传播的关系）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：全连接前馈网络与反向传播（第 4 章）、梯度下降与 ReLU、张量的维度概念（NCHW）、numpy/PyTorch 基础张量操作。
>
> **所属主题**：-CNN卷积神经网络 · 算法细节

## 本次只学这一点

**（1）宽卷积的交换性。** 对图像 $X$ 两端各补 $m-1$、$n-1$ 个零得到全填充（full padding）的 $\tilde{X}$，定义宽卷积 $\tilde{\boldsymbol{W}} \otimes \boldsymbol{X} \triangleq \boldsymbol{W}\otimes \tilde{\boldsymbol{X}}$，则当两个信号长度固定时宽卷积具有交换性：$\mathrm{rot180}(W)\ \tilde{\otimes}\ X = \mathrm{rot180}(X)\ \tilde{\otimes}\ W$（教材习题 5-2）。

**（2）梯度形式。** 设 $Y = W \otimes X$，$\mathcal{L}(\cdot)$ 为标量函数，教材公式 (5.14)–(5.21) 给出两条形状与含义都不同的式子：

$$\frac{\partial \mathcal{L}}{\partial W}=\frac{\partial \mathcal{L}}{\partial Y}\otimes X,\qquad \frac{\partial \mathcal{L}}{\partial X}=\mathrm{rot180}\left(\frac{\partial \mathcal{L}}{\partial Y}\right)\ \tilde{\otimes}\ W .$$

两条式子含义完全不同，这是卷积层反向传播最容易记错的地方：

- **对权重的梯度是互相关**：$\partial\mathcal{L}/\partial W$ 由"误差项 $\partial\mathcal{L}/\partial Y$ 与输入 $X$ 做互相关"得到，形状回落到 $m\times n$。直观理解：$Y$ 关于 $W$ 是线性的，$\partial Y_{ij}/\partial w_{uv}$ 就是那个被扫到的输入像素 $x_{i+u-1,j+v-1}$，把所有位置累加即互相关。
- **对输入的梯度必须是真卷积**：$\partial\mathcal{L}/\partial X$ 形状要还原成输入尺寸，需要对误差项做**宽卷积**（等价于对 $X$ 做 $p=(m-1,n-1)$ 的零填充后再互相关），并把核旋转 180°。这就是"前向是互相关、反向要翻转"的由来。

在 PyTorch 里你不需要手写这些：`loss.backward()` 会自动按上式算，但你必须知道"卷积层的前向计算与反向传播在形式上互为转置"（习题 5-7）——这正是转置卷积（2.8）的出发点。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「卷积的数学性质（与反向传播的关系）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)
