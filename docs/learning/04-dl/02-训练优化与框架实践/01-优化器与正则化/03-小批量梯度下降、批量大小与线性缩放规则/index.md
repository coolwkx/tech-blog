---
article_id: kp-8565f2a6a2a7c3b8
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 2
learning_objective: 理解并验证：小批量梯度下降、批量大小与线性缩放规则
---

# 小批量梯度下降、批量大小与线性缩放规则

> **学习目标**：能够解释「小批量梯度下降、批量大小与线性缩放规则」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

每次迭代抽 $B$ 个样本 $\mathcal B$，梯度取批内平均 $g_t=\mathfrak g(\theta_{t-1})=\frac1B\sum_{(x,y)\in\mathcal B}\partial\mathcal L(y,f(x;\theta))/\partial\theta$，更新 $\theta_t\leftarrow\theta_{t-1}-\alpha g_t$。教材区分两个量：$\mathfrak g$ 是**梯度**，$\Delta\theta_t\triangleq\theta_t-\theta_{t-1}$ 是**实际更新方向**；标准 SGD 下 $\Delta\theta_t=-\alpha g_t$，但在动量/Adam 里二者不再一致。

**批量大小的影响**：由 $\mathbb E[\tilde g]=g$、$\mathrm{Var}[\tilde g]=\Sigma/B$ 可知批量**不影响梯度期望、只影响方差**，噪声标准差 $\propto1/\sqrt B$。批量越大 → 噪声越小 → 训练越稳 → 可用更大学习率；批量小还用大学习率，噪声会把参数甩飞。**线性缩放规则（linear scaling rule）**：批量增大 $k$ 倍，学习率也增大 $k$ 倍。一个简洁推导是"每个 epoch 走过的总位移不变"——一个 epoch 有 $N/B$ 次迭代、位移量级为 $(N/B)\cdot\alpha$，令其不变即得

$$\frac{\alpha}{B}=\text{const}\ \Longrightarrow\ \alpha\propto B .$$

批量特别大时该规则失效（曲率让大步长越界），经验上改用 $\alpha\propto\sqrt B$ 并配 warmup。还要留意两点：以 epoch 为横轴比较时**小批量反而收敛更快**（一个 epoch 内更新次数更多）；有效权重衰减强度 $\alpha\lambda$ 会随 $\alpha$ 一起放大。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「小批量梯度下降、批量大小与线性缩放规则」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
