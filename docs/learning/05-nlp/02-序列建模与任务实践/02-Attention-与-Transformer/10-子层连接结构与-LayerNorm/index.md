---
article_id: kp-63a68fb73095f5e9
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 9
learning_objective: 理解并验证：子层连接结构与 LayerNorm
---

# 子层连接结构与 LayerNorm

> **学习目标**：能够解释「子层连接结构与 LayerNorm」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 方法细节

## 本次只学这一点

$$
\text{output}=x+\text{Dropout}\big(\text{Sublayer}(\text{LayerNorm}(x))\big)
$$

这是 Pre-LN 写法：先 LayerNorm，再进子层，再 Dropout，最后与原始 $x$ 残差相加。现代大模型普遍采用 Pre-LN（训练更稳定、对 warmup 依赖更小）；Post-LN 的备选写法是 `x + dropout(norm(sublayer(x)))`。

LayerNorm 在**最后一维**（特征维）上求均值方差，并保留可学习的缩放 $\gamma$ 与平移 $\beta$：

$$
y=\gamma\cdot\frac{x-\mu}{\sigma+\epsilon}+\beta
$$

这里的 `*` 是逐元素相乘，不是矩阵乘法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「子层连接结构与 LayerNorm」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
