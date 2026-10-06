---
article_id: kp-42e39fb0c87f6de4
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-a9dec5ff9c41
learning_sourceId: a9dec5ff9c41
learning_order: 2
learning_objective: 理解并验证：BPTT：随时间反向传播
---

# BPTT：随时间反向传播

> **学习目标**：能够解释「BPTT：随时间反向传播」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：多层前馈网络与反向传播、链式法则与 Jacobian、Logistic/Tanh 及其导数、梯度下降与学习率、PyTorch 的 `nn.Module` 与张量维度。
>
> **所属主题**：-RNN与序列模型 · 算法细节

## 本次只学这一点

设每个时刻都有监督信号，损失为 $\mathcal{L}=\sum_{t=1}^{T}\mathcal{L}_t$，$\mathcal{L}_t=\mathcal{L}\big(y_t,g(h_t)\big)$。由于 $W$ 出现在每一个时刻的 $z_t$ 中，链式法则要求对所有时刻求和：

$$\frac{\partial\mathcal{L}}{\partial W}=\sum_{t=1}^{T}\frac{\partial \mathcal{L}}{\partial z_t}\frac{\partial^{+} z_t}{\partial W}$$

教材定义误差项 $\delta_{t,k}\triangleq\dfrac{\partial \mathcal{L}_t}{\partial z_k}$。当 $k<t$ 时，反向递推为

$$\delta_{t,k}=\frac{\partial z_{k+1}}{\partial z_k}\delta_{t,k+1}=\mathrm{diag}\big(f'(z_k)\big)\,W^{\top}\,\delta_{t,k+1}$$

**手推关键一步（展开连乘）**：反复套用上式，从 $t$ 一路推到 $k$：

$$\delta_{t,k}=\prod_{\tau=k}^{t-1}\Big(\mathrm{diag}\big(f'(z_\tau)\big)W^{\top}\Big)\,\delta_{t,t}$$

于是

$$\frac{\partial \mathcal{L}}{\partial W}=\sum_{t=1}^{T}\sum_{k=1}^{t}\delta_{t,k}\,h_{k-1}^{\top},\qquad
\frac{\partial \mathcal{L}}{\partial U}=\sum_{t=1}^{T}\sum_{k=1}^{t}\delta_{t,k}\,x_{k}^{\top},\qquad
\frac{\partial \mathcal{L}}{\partial b}=\sum_{t=1}^{T}\sum_{k=1}^{t}\delta_{t,k}$$

注意两个特征：外层对 $t$（哪个时刻的损失）求和，内层对 $k$（哪个时刻的参数贡献）求和，双重求和正是"参数共享"的数学体现；而 $\delta$ 的递推因子 $\mathrm{diag}(f'(z_k))W^{\top}$ 与 $t$ 无关，这为下一节的 $\gamma$ 判据埋下伏笔。

与之对照的是 **RTRL**（Real-Time Recurrent Learning），它用自动微分的**前向模式**从第 1 个时刻起实时递推 $\partial h_t/\partial w_{ij}$，无需等到序列结束：

| 对比项 | BPTT | RTRL |
| --- | --- | --- |
| 微分模式 | 反向模式（reverse mode） | 前向模式（forward mode） |
| 时间复杂度 | 与序列长度 $T$ 线性 | 与序列长度 $T$ 线性，但每步需维护 $O(D^2M)$ 个偏导 |
| 空间复杂度 | 需保存所有时刻中间梯度，$O(T)$ 较高 | 只需保存当前时刻的偏导矩阵，无需存储历史 |
| 适用场景 | 离线整句训练（NLP 主流） | **在线学习**、**无限序列**流式任务 |
| 实践地位 | 主流，PyTorch 中即 `loss.backward()` + 梯度累加 | 很少直接用，思想见于在线学习/递推最小二乘 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BPTT：随时间反向传播」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)
