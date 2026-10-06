---
article_id: kp-245e1b7f569c55dd
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 7
learning_objective: 理解并验证：位置编码
---

# 位置编码

> **学习目标**：能够解释「位置编码」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 方法细节

## 本次只学这一点

Transformer 丢弃了递归结构，不加位置信息则打乱词序结果不变。编码用三角函数：

$$
PE_{(pos,2i)}=\sin\!\left(\frac{pos}{10000^{2i/d_{model}}}\right),\qquad
PE_{(pos,2i+1)}=\cos\!\left(\frac{pos}{10000^{2i/d_{model}}}\right)
$$

实现上用 `div_term = exp(arange(0, d_model, 2) * -(log(10000.0)/d_model))` 一次算出分母，偶数列赋 sin、奇数列赋 cos。用三角函数的理由：

1. 同一词汇随位置不同，位置嵌入会变化，从而携带位置信息。
2. sin/cos 值域 $[-1,1]$，控制嵌入数值大小，有助于梯度计算。
3. 由和角公式可得 $PE_{pos+k}$ 是 $PE_{pos}$ 的线性函数，模型因此能学到相对位置关系；且周期函数不受序列长度限制。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「位置编码」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
