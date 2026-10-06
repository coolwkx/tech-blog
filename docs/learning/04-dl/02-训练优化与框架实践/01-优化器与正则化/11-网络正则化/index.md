---
article_id: kp-8a4278f7e0d3324d
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 10
learning_objective: 理解并验证：网络正则化
---

# 网络正则化

> **学习目标**：能够解释「网络正则化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 算法细节

## 本次只学这一点

**$\ell_1$ / $\ell_2$ 正则化**统一写作 $\theta^{\star}=\arg\min_\theta\frac1N\sum_{i=1}^N\mathcal L(y^{(i)},f(x^{(i)};\theta))+\lambda\Omega(\theta)$，其中 $\Omega_{\ell_1}=\sum_j|\theta_j|$、$\Omega_{\ell_2}=\sum_j\theta_j^2$。它**等价于**带约束的优化 $\min\frac1N\sum\mathcal L$ s.t. $\Omega(\theta)\le1/\lambda$：几何上 $\ell_1$ 的约束域是带尖角的菱形，最优点容易被顶到坐标轴上，因此产生**稀疏**解；$\ell_2$ 的约束域是球，只做整体收缩。（$\ell_1$ 在 0 点不可导，工程上用 $\sqrt{\theta^2+\delta}$ 近似或用次梯度。）两者折中即弹性网络。要注意在**过度参数化**的深度网络中，$\ell_1/\ell_2$ 的效果往往不如浅层模型显著。

**权重衰减与 $\ell_2$ 的关系**。权重衰减在每次更新时乘一个衰减系数 $\theta_t\leftarrow(1-w)\theta_{t-1}-\alpha g_t$；而在损失里加 $\frac\lambda2\|\theta\|^2$ 时梯度变成 $g_t+\lambda\theta_{t-1}$，朴素 SGD 更新为

$$\theta_t=\theta_{t-1}-\alpha(g_t+\lambda\theta_{t-1})=(1-\alpha\lambda)\theta_{t-1}-\alpha g_t .$$

逐项对照得 $w=\alpha\lambda$：**在（带动量的）SGD 里二者完全等价**，所以很多框架干脆用 $\ell_2$ 实现 weight decay。但在 **Adam 等自适应方法里二者不等价**：$\lambda\theta$ 会先进入 $m_t,v_t$，再被 $\sqrt{\hat v_t}$ **逐参数**缩放，有效正则强度随参数、随训练时刻变化（梯度小的参数被过度正则）。解决办法是把衰减从梯度里解耦、直接作用在参数上，即 **AdamW**：

```python
optim = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-2) # 真·weight decay
# torch.optim.Adam(..., weight_decay=1e-2) 等价于在 loss 里加 L2（旧式，不推荐）
```

**提前停止（early stopping）**：留独立验证集，验证误差不再下降就停止，并**回滚到验证误差最好的 checkpoint**。本质是把参数限制在初始点附近的球内、限制有效容量，等价于一种隐式 $\ell_2$ 正则；实践上验证曲线常常先降后升，准则要按任务调（如"连续 $k$ 轮不提升"）。

**Dropout（丢弃法）**：训练时以概率 $p$ 随机把神经元（连同连接）置零。教材写的是"保留率"版本：设保留率 $1-p$，训练阶段 $\tilde a=\mathrm{mask}(a)=m\odot a$，$m\sim\mathrm{Bernoulli}(1-p)$，此时激活的神经元平均只有原来 $(1-p)$ 倍；推理阶段全部激活以保证输出一致，所以要**把输入乘回 $(1-p)$**。现代框架（含 PyTorch）实现的是 **inverted dropout**：训练时立刻把保留的激活**除以保留率**，推理时什么都不做：

$$\text{训练：}\ \tilde a=\frac{m\odot a}{1-p},\ m\sim\mathrm{Bernoulli}(1-p);\qquad \text{推理：}\ \tilde a=a .$$

这样训练与推理的**期望一致**（$\mathbb E[\tilde a]=a$），推理路径零开销。PyTorch 语义：`nn.Dropout(p=0.5)` 中 `p` 是**被丢弃**的概率，保留元素放大 $1/(1-p)=2$ 倍，且只在 `model.train` 时生效、`model.eval` 时自动关闭。① **集成视角**：每次丢弃相当于采出一个子网络，$n$ 个神经元可采出 $2^n$ 个子网络，它们**共享参数**、每次迭代训练一个，最终模型可近似看作指数级子网络的集成；推理用全部权重并按期望缩放，近似给出集成的平均预测（对单层线性/Softmax 单元，权重缩放恰好对应子网络预测的几何平均，其余情形是近似）。② **贝叶斯视角**：可解释为对参数 $\theta$ 做蒙特卡洛采样 $\mathbb E_{p(\theta)}[f]\approx\frac1T\sum_tf(x,\hat\theta_t)$。③ **超参数**：隐藏层保留率 $0.5$（子网络多样性最大）、**输入层保留率要接近 1**（丢输入相当于加噪声，太大信息就被毁）。④ **RNN 上**不能逐时刻独立丢弃隐状态，那会摧毁时间维记忆：做法是只对**非循环连接**丢弃，更严格的是**变分丢弃（variational dropout）**——对参数矩阵每个元素采样一次掩码，并在所有时刻复用**同一个掩码**。

**数据增强**：旋转、翻转、缩放、平移、加噪声；视觉上最有效，NLP 中相对困难（教材明确指出文本等类型上还没有太好的通用方法）。**标签平滑（label smoothing）** 用软目标代替 one-hot：$q=[0,\dots,1,\dots,0]^{\top}\to\tilde q=[\frac{\epsilon}{K-1},\dots,1-\epsilon,\dots,\frac{\epsilon}{K-1}]^{\top}$（$K$ 为类别数），交叉熵损失为 $\mathcal L=-(1-\epsilon)\log p_y-\frac{\epsilon}{K-1}\sum_{k\ne y}\log p_k$。PyTorch 的 `CrossEntropyLoss(label_smoothing=ε)` 用等价写法 $\tilde q=(1-\epsilon)q+\frac{\epsilon}{K}\mathbf 1$（$\epsilon$ 均摊到 $K$ 类而非 $K-1$ 个非目标类），两种写法在非目标类上的总概率质量都是 $\epsilon$。动机：one-hot 要求正确类 logit **远大于**其他类才能让概率趋近 1，会把权重推得越来越大；标签本身标错时过拟合更严重。加噪可避免输出过度自信，且通常不损害分类能力。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「网络正则化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
