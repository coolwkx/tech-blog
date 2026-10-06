---
article_id: kp-c21c86da14263f8c
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 5
learning_objective: 理解并验证：梯度估计修正：动量法与 Nesterov
---

# 梯度估计修正：动量法与 Nesterov

> **学习目标**：能够解释「梯度估计修正：动量法与 Nesterov」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

小批量梯度是真实梯度的带噪估计，用"最近一段时间的平均梯度"代替当前随机梯度可以显著提速。**动量法** $\Delta\theta_t=\rho\Delta\theta_{t-1}-\alpha g_t$（$\rho$ 通常 $0.9$），取 $\Delta\theta_0=0$ 展开：

$$\begin{aligned}\Delta\theta_1&=-\alpha g_1,\\ \Delta\theta_2&=\rho(-\alpha g_1)-\alpha g_2=-\alpha(\rho g_1+g_2),\\ \Delta\theta_3&=\rho\Delta\theta_2-\alpha g_3=-\alpha(\rho^2g_1+\rho g_2+g_3),\\ &\ \ \vdots\\ \Delta\theta_t&=-\alpha\sum_{\tau=1}^{t}\rho^{\,t-\tau}g_\tau .\end{aligned}$$

即对梯度做了一次系数和为 $\sum_{k=0}^{t-1}\rho^k\to\frac{1}{1-\rho}$ 的指数加权平均。两个推论：① **加速**——梯度长期同方向时（$g_\tau\equiv g$）有效步长为 $\alpha/(1-\rho)$，$\rho=0.9$ 时放大 10 倍，所以换成动量后常需把 $\alpha$ 调小；② **抑制振荡**——某方向梯度来回变号时交替项 $\sum_k\rho^k(-1)^k\to\frac{1}{1+\rho}$，幅度被压掉近一半，因此动量在狭长峡谷中沿长轴加速、沿短轴减速。

**Nesterov 加速梯度（NAG）**。动量法的更新可拆成"先按动量走到 $\hat\theta_t=\theta_{t-1}+\rho\Delta\theta_{t-1}$，再用 $\theta_{t-1}$ 处的梯度修正"：$\theta_t=\hat\theta_t-\alpha g(\theta_{t-1})$。第二步用的是**旧点**梯度，逻辑上不自然——人已经站在 $\hat\theta_t$，就该看 $\hat\theta_t$ 的梯度。改成"先看再走"：

$$\Delta\theta_t=\rho\Delta\theta_{t-1}-\alpha\,g\!\left(\theta_{t-1}+\rho\Delta\theta_{t-1}\right).$$

这就是 NAG，相当于提前"瞄一眼"前方坡度、弯道处提前减速。PyTorch 用等价的重参数化形式实现 `nesterov=True`（`buf = ρ·buf + g`，`d_p = g + ρ·buf`）；梯度变化缓慢时它与动量法一致，差异只在曲率大处体现。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度估计修正：动量法与 Nesterov」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
