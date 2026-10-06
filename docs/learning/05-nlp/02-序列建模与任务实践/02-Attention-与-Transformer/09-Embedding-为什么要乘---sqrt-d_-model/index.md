---
article_id: kp-dde293e281176295
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 8
learning_objective: 理解并验证：Embedding 为什么要乘 $\sqrt{d_{model}}$
---

# Embedding 为什么要乘 $\sqrt{d_{model}}$

> **学习目标**：能够解释「Embedding 为什么要乘 $\sqrt{d_{model}}$」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 方法细节

## 本次只学这一点

```python
return self.lut(x) * math.sqrt(self.d_model)
```

词嵌入参数初始化方差很小，而位置编码值域是 $[-1,1]$，两者量纲差距大。若直接相加，位置编码会「盖住」词嵌入携带的语义信息。乘 $\sqrt{d_{model}}$ 放大词嵌入，使二者量级相当，并让分布更接近标准正态，有利于后续层学习。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Embedding 为什么要乘 $\sqrt{d_{model}}$」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
