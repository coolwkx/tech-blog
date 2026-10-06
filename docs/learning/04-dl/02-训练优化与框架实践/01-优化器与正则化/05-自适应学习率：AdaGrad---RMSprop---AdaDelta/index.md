---
article_id: kp-b33bdc14e8d84a7e
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 4
learning_objective: 理解并验证：自适应学习率：AdaGrad / RMSprop / AdaDelta
---

# 自适应学习率：AdaGrad / RMSprop / AdaDelta

> **学习目标**：能够解释「自适应学习率：AdaGrad / RMSprop / AdaDelta」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

核心思想：不同参数收敛速度差异大，给每个参数配自己的学习率。以下 $\odot$ 为逐元素乘，开方/除/加都是逐元素操作。

**AdaGrad**（累积梯度平方，借鉴 $\ell_2$ 正则化思想）取 $G_t=\sum_{\tau=1}^{t}g_\tau\odot g_\tau$，更新 $\Delta\theta_t=-\frac{\alpha}{\sqrt{G_t}+\epsilon}\odot g_t$。梯度一直很大的参数分母大、学习率被压小；很少更新的参数分母小、学习率相对大。**致命缺点**：$G_t$ 单调递增 → 有效学习率**单调递减** → 后期 $\alpha/\sqrt{G_t}\to0$，即使还没到最优点也几乎不再更新，即"提前罢工"。

**RMSprop** 把累积换成指数加权移动平均：

$$G_t=\beta G_{t-1}+(1-\beta)\,g_t\odot g_t=(1-\beta)\sum_{\tau=1}^{t}\beta^{\,t-\tau}g_\tau\odot g_\tau,\qquad \Delta\theta_t=-\frac{\alpha}{\sqrt{G_t}+\epsilon}\odot g_t ,$$

$\beta$ 一般 $0.9$、$\alpha$ 例如 $0.001$、$\epsilon$ 取 $10^{-8}$ 量级。旧梯度被指数遗忘，$G_t$ 可升可降，学习率**不再单调衰减**，修掉了 AdaGrad 的毛病。**AdaDelta** 进一步用更新量平方的移动平均取代手动设置的 $\alpha$：$\Delta x^2_{t-1}=\rho_1\Delta x^2_{t-2}+(1-\rho_1)\Delta\theta_{t-1}\odot\Delta\theta_{t-1}$，$\Delta\theta_t=-\frac{\sqrt{\Delta x^2_{t-1}+\epsilon}}{\sqrt{G_t+\epsilon}}\odot g_t$，量纲自洽、对学习率尺度不敏感，但多一个超参且实际收益有限，如今用得少。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「自适应学习率：AdaGrad / RMSprop / AdaDelta」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
