---
article_id: kp-b00e2c485c502b9b
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 6
learning_objective: 理解并验证：CBOW 的前向与维度变化
---

# CBOW 的前向与维度变化

> **学习目标**：能够解释「CBOW 的前向与维度变化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 方法细节

## 本次只学这一点

设词表大小 $V$、词向量维度 $N$、窗口半径 $c$：

1. **输入**：$2c$ 个上下文词的 one-hot，$x^{(1)},\dots,x^{(2c)} \in \mathbb{R}^V$。
2. **投影**：共享一个输入矩阵 $W \in \mathbb{R}^{V \times N}$，得到 $v_i = W^\top x^{(i)}$（即查表得到该词的 $N$ 维向量）。
3. **平均**：$h = \frac{1}{2c}\sum_i v_i \in \mathbb{R}^N$。这一步是 CBOW 名字的由来——把上下文当成一个无序的「词袋」。
4. **输出**：$u = W'^\top h \in \mathbb{R}^V$，其中 $W' \in \mathbb{R}^{N \times V}$ 是输出矩阵。
5. **softmax**：$\hat y_j = \dfrac{\exp(u_j)}{\sum_{j'=1}^{V}\exp(u_{j'})}$。
6. **损失**：与真实中心词的 one-hot 做交叉熵。

**Skip-gram** 只是把 2–6 步反过来：输入 1 个中心词的 one-hot，对其 $2c$ 个上下文位置各做一次上述预测，总损失是各位置交叉熵之和。

训练完成后，通常用 $W$（输入矩阵）的转置作为词向量表；也有实现把 $W$ 与 $W'$ 相加或拼接。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CBOW 的前向与维度变化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
