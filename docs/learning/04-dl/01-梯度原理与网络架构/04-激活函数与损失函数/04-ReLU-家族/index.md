---
article_id: kp-89c0113b48c1064e
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 3
learning_objective: 理解并验证：ReLU 家族
---

# ReLU 家族

> **学习目标**：能够解释「ReLU 家族」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

$$\text{ReLU}(x)=\max(0,x),\qquad \text{ReLU}'(x)=\mathbf{1}(x>0).$$

**优点**（教材 4.1.2 节）：①只需加、乘、比较，**计算高效**，导数非 0 即 1；②**生物合理性**（biological plausibility）——单侧抑制、宽兴奋边界，人脑同一时刻仅约 1%~4% 神经元活跃；③**稀疏性**——Sigmoid 型导致非稀疏网络，而 ReLU 约 50% 神经元激活（负半轴严格输出 0）；④**缓解梯度消失**——左饱和但正半轴导数恒 1，误差可原样回传。

**缺点**：①**非零中心化**，输出恒 $\ge0$，同样引入 bias shift；②**Dying ReLU（死亡 ReLU）**——若某次不当更新让某神经元**在所有训练样本上**净输入都 $\le0$，它的梯度永远为 0，参数再也无法更新，该神经元永久死亡（输出恒 0，相当于被剪掉）。注意死因是"在所有样本上都负"，而非偶尔为负。

| 变种 | 表达式 | 关键性质 |
|---|---|---|
| LeakyReLU | $\max(\alpha x,x)$，$\alpha$ 常取 0.01 | 负半轴保留小梯度，非激活时仍可更新，避免永久死亡；$\alpha<1$ 时等价于一个简单的 maxout 单元 |
| PReLU | $\max(0,x)+\gamma_i\min(0,x)$ | $\gamma_i$ **可学习**且每神经元可不同（也可整组共享）；$\gamma_i=0$ 退化为 ReLU，很小时近似 LeakyReLU；非饱和函数 |
| ELU | $\max(0,x)+\min(0,\alpha(e^x-1))$ | 负半轴饱和到 $-\alpha$，**近似零中心化**，输出均值被拉向 0；$\alpha\ge0$ 控制负半轴饱和曲线；抗噪但含 `exp` |
| Softplus | $\log(1+e^x)$ | ReLU 的**平滑版本**，导数恰为 Logistic：$\frac{d}{dx}\log(1+e^x)=\frac{e^x}{1+e^x}=\sigma(x)$；有单侧抑制与宽兴奋边界，但**无稀疏激活性** |

Softplus 把两条线连了起来：$\frac{d}{dx}\text{Softplus}=\sigma$，所以它是 Logistic 的"积分"版本；$x\gg0$ 时 $\approx x$（ReLU），$x\ll0$ 时 $\approx e^x\to0$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ReLU 家族」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
