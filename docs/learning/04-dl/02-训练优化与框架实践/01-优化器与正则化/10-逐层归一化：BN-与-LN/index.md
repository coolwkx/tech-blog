---
article_id: kp-ae86f7c82f154172
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 9
learning_objective: 理解并验证：逐层归一化：BN 与 LN
---

# 逐层归一化：BN 与 LN

> **学习目标**：能够解释「逐层归一化：BN 与 LN」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

**为什么有效**：① **更好的尺度不变性**——深层网络中前层参数一变、本层输入分布就漂移，本层参数得重新适应，这叫**内部协变量偏移（internal covariate shift）**，把每层输入拉回标准正态可让高层输入更稳定；② **更平滑的优化地形**——让多数神经元落在非饱和区，梯度更大更稳，**允许更大学习率**，收敛更快。

**批量归一化（Batch Normalization）** 的提出动机是解决内部协变量偏移，但后续研究（Santurkar et al., 2018）发现**主因是优化地形被平滑，而非真的消除了协变量偏移**——BN 甚至会放大某些层的分布变化却依然加速训练。给定小批量 $\mathcal B$（大小 $m$），对第 $l$ 层净输入 $z^{(l)}$ 的每一维取 $\boldsymbol\mu_{\mathcal B}=\frac1m\sum_{i=1}^mz^{(i)}$、$\boldsymbol\sigma^2_{\mathcal B}=\frac1m\sum_{i=1}^m(z^{(i)}-\boldsymbol\mu_{\mathcal B})\odot(z^{(i)}-\boldsymbol\mu_{\mathcal B})$，再标准化并做仿射恢复：

$$\hat z^{(l)}=\frac{z^{(l)}-\boldsymbol\mu_{\mathcal B}}{\sqrt{\boldsymbol\sigma^2_{\mathcal B}+\epsilon}}\odot\gamma+\boldsymbol\beta\ \triangleq\ \mathrm{BN}_{\gamma,\boldsymbol\beta}\big(z^{(l)}\big).$$

要点：① $\gamma,\boldsymbol\beta$ 是**可学习的**缩放/平移，没有它们把净输入强压到 0 附近会使 Sigmoid 型激活退化成近似线性、削弱表达能力；取 $\gamma=\sqrt{\sigma^2_{\mathcal B}},\boldsymbol\beta=\mu_{\mathcal B}$ 即恒等变换，说明标准归一化被包含在该参数族里。② BN 加在**仿射变换之后、激活函数之前**，因它自带平移 $\boldsymbol\beta$，前面的仿射层**不再需要偏置**（所以常写 `nn.Conv2d(..., bias=False)`）。③ $\mu_{\mathcal B},\sigma^2_{\mathcal B}$ 是净输入的**函数而非常量**，反向传播必须把它们的梯度也传过去。④ **训练用当前批统计量，推理用累积的移动平均**（PyTorch：$\text{running}\leftarrow(1-m)\text{running}+m\cdot\text{batch}$，`momentum` 默认 $0.1$）；忘记 `model.eval` 会让推理也用批统计量，结果依赖同批样本且抖动。⑤ 自带轻微正则：一个样本的预测依赖同批随机成员，模型难以"过拟合到某个特定样本"。

**层归一化（Layer Normalization）**。BN 要求批不能太小，且 RNN 这种净输入分布随时间动态变化的结构无法直接用 BN。LN 改为对**同一层所有神经元**在**单个样本内**求统计量：$\mu^{(l)}=\frac1M\sum_{i=1}^Mz_i^{(l)}$、$\sigma^{(l)2}=\frac1M\sum_{i=1}^M(z_i^{(l)}-\mu^{(l)})^2$、$\hat z^{(l)}=\frac{z^{(l)}-\mu^{(l)}}{\sqrt{\sigma^{(l)2}+\epsilon}}\odot\gamma+\boldsymbol\beta$。用矩阵语言说：小批量矩阵 $Z^{(l)}\in\mathbb R^{m\times M}$，**LN 对每一行（每个样本）归一化，BN 对每一列（每个特征维）归一化**。LN 与 batch 无关、batch size 可以取 1，天然适合 RNN/Transformer：$a_t=Wh_{t-1}+Ux_t$ 后接 $h_t=f(\mathrm{LN}_{\gamma,\beta}(a_t))$，可显著缓解沿时间累积的梯度爆炸/消失。

| 对比项 | Batch Normalization | Layer Normalization |
| --- | --- | --- |
| 归一化维度 | 跨样本，对每个特征维（矩阵的列） | 跨特征，对每个样本（矩阵的行） |
| 是否依赖批量 | 依赖，批太小统计量不准 | 不依赖，batch size = 1 也可 |
| 训练/推理是否一致 | **不一致**，需移动平均 + `eval` | 一致，无需额外统计量 |
| 适合 RNN/变长序列 | 不适合 | 适合 |
| 常见位置 | CNN 卷积层后、激活前 | RNN / Transformer 子层内 |
| 选用建议 | 批量足够大时一般更优 | 批量很小时用 LN |

**权重归一化（Weight Normalization）** 用再参数化把权重拆成"长度 × 方向"，$w_{i,:}=g_i\frac{v_i}{\|v_i\|}$（$g_i$ 标量、$v_i$ 与输入同维）；因为权重常被共享，参数量增加很少、开销小。**局部响应归一化（LRN）** 受生物侧抑制启发，用在卷积层**激活之后**，只对相邻特征映射做局部归一化且**不减均值**：$\hat x_i=x_i/(k+\alpha\sum_{j=\max(1,i-n/2)}^{\min(C,i+n/2)}x_j^2)^{\beta}$（AlexNet 用 $n=5,\alpha=10^{-4},\beta=0.75,k=2$）。它与最大汇聚的侧抑制不同：LRN 抑制**同一位置、相邻通道**，最大汇聚抑制**同一通道、相邻位置**。现代网络基本用 BN 取代了它。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「逐层归一化：BN 与 LN」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
