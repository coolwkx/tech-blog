---
article_id: kp-16adadcc73e1844d
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 5
learning_objective: 理解并验证：损失掩码：为什么只对回答算 loss
---

# 损失掩码：为什么只对回答算 loss

> **学习目标**：能够解释「损失掩码：为什么只对回答算 loss」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

设一条样本的 token 序列为 $x_{1:T}$，其中 prompt 部分占前 $P$ 个 token（$x_{1:P}$），回答部分占后 $T-P$ 个 token。原始语言模型损失是

$$
\mathcal{L}_{\text{full}}
= -\frac{1}{T-1}\sum_{t=2}^{T}\log p_\theta(x_t \mid x_{<t})
$$

**掩码后的损失**是给每个位置引入权重 $m_t\in\{0,1\}$：

$$
\boxed{\;
\mathcal{L}_{\text{masked}}
= -\frac{1}{\sum_{t=2}^{T} m_t}\sum_{t=2}^{T} m_t \log p_\theta(x_t \mid x_{<t})
\;}
$$

其中 $m_t = 0$（被掩码）当 $t \le P$，$m_t = 1$ 当 $t > P$。PyTorch 的实现约定是：**把 $m_t=0$ 的位置的 label 写成 `-100`**，然后使用

```python
loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
```

`ignore_index=-100` 表示该位置既不贡献分子（loss 项），也不贡献分母（归一化计数）。这与 `nn.CrossEntropyLoss` 支持 `ignore_index` 的官方语义一致（见 [PyTorch 文档](https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)）。

**不掩码会发生什么？**

| 后果 | 机制 |
| --- | --- |
| 模型学会"复述用户输入" | prompt 的每个 token 都被要求高概率预测，而它们是给定的确定性文本，模型会倾向于在推理时把它们重写出来 |
| loss 数值被低估、失去可比性 | 分母包含了大量"简单"的 prompt token，loss 看起来降得很快但并不代表回答质量提升 |
| 训练与推理目标不一致 | 推理时我们只关心从 prompt 之后开始的分布，训练却把注意力分散到 prompt 上 |
| 短回答样本被稀释 | prompt 越长，回答部分在 loss 中的占比越小，模型对回答的学习信号越弱 |

**注意例外**：如果你做的是**领域继续预训练（DAPT）**，那就应该对全文算 loss——此时数据本身没有"prompt/回答"的区分。掩码策略必须与训练目标匹配。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「损失掩码：为什么只对回答算 loss」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
