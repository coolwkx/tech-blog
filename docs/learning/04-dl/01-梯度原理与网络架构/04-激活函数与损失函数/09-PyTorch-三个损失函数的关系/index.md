---
article_id: kp-016a691f0ff10777
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 8
learning_objective: 理解并验证：PyTorch 三个损失函数的关系
---

# PyTorch 三个损失函数的关系

> **学习目标**：能够解释「PyTorch 三个损失函数的关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 算法细节

## 本次只学这一点

| API | 输入要求 | target 形式 | 内部是否含激活 | 数值稳定性 |
|---|---|---|---|---|
| `nn.CrossEntropyLoss` | **logits**（未归一化得分） | 类别索引 `LongTensor`，形状 $(N,)$ | 是（等价 `LogSoftmax` + `NLLLoss`） | 高（log-sum-exp） |
| `nn.NLLLoss` | **log 概率**（须先 `log_softmax`） | 类别索引 | 否 | 取决于是否用了 `log_softmax` |
| `nn.BCEWithLogitsLoss` | **logits** | 浮点标签，同形 | 是（内部 Sigmoid+BCE） | 高（log-sum-exp） |
| `nn.BCELoss` | **概率**（须先 `Sigmoid`） | 浮点标签 | 否 | 低（易 $\log0$） |

恒等关系（高频考点）：`CrossEntropyLoss(logits, y) ≡ NLLLoss(log_softmax(logits), y)`；`BCEWithLogitsLoss` ≡ `BCELoss(sigmoid(logits))` 但前者更稳。

**为何 `BCEWithLogitsLoss` 更稳**：把 $\hat y=\sigma(z)$ 代入 BCE，$y=1$ 得 $\log(1+e^{-z})$、$y=0$ 得 $\log(1+e^{z})$，统一写成

$$\mathcal{L}=\max(z,0)-zy+\log\bigl(1+e^{-|z|}\bigr),$$

指数参数恒 $\le0$，**绝不溢出**；而直接算 $\log(\sigma(z))$，$z$ 很负时 $\sigma(z)$ 下溢为 0，取对数得 $-\infty$。`CrossEntropyLoss` 内部同理用 log-sum-exp 避免 $e^z$ 上溢。

**最经典的三个误用**：①末层加了 `nn.Softmax` 又用 `nn.CrossEntropyLoss` → softmax 算了两次，概率被压平、梯度信号被削弱；②用 `nn.NLLLoss` 却没先 `log_softmax` → 对负数取对数得 NaN；③用 `nn.BCELoss` 却不先 `Sigmoid`（或过了 Sigmoid 又用 `BCEWithLogitsLoss`）→ 梯度链条断裂或二次压缩。

**接口为什么必须搭配设计**：输出层由损失函数给出 $\partial\mathcal{L}/\partial z^{(L)}$（交叉熵 → 干净的 $\hat y-y$，MSE+Sigmoid → 被 $\sigma'$ 污染的乘积），隐藏层每层乘 $f'(z^{(l)})$。所以隐藏层激活导数的绝对值**期望接近 1** 才好，这一"信号守恒"诉求正是 He 初始化（配 ReLU，方差 $\propto2/n_{in}$）与 Xavier 初始化（配 Tanh）的由来。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PyTorch 三个损失函数的关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
