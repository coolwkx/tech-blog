---
article_id: kp-411e0dad498b090b
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 2
learning_objective: 理解并验证：CBOW 与 Skip-gram
---

# CBOW 与 Skip-gram

> **学习目标**：能够解释「CBOW 与 Skip-gram」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 核心概念

## 本次只学这一点

| 对比项 | CBOW（连续词袋） | Skip-gram（跳字） |
|--------|------------------|-------------------|
| 任务 | 用上下文预测中心词 | 用中心词预测上下文 |
| 输入 | 窗口内 $2c$ 个上下文词 | 1 个中心词 |
| 输出 | 1 个中心词 | 窗口内 $2c$ 个上下文词 |
| 上下文处理 | 对上下文向量取**平均**后送入投影层 | 每个上下文位置单独预测 |
| 训练速度 | 快（一次梯度更新学 $2c$ 个词的信息） | 慢（每个上下文位置都要算一次） |
| 低频词效果 | 较差（平均会稀释低频词信号） | 更好（每个上下文都是独立监督） |
| 常见选择 | 大规模语料、追求速度 | 小语料、关注低频词与语义质量 |

一句话选型：**语料大、要快用 CBOW；语料小、要语义质量（尤其低频词）用 Skip-gram**。fastText 的 `train_unsupervised` 默认就是 Skip-gram。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CBOW 与 Skip-gram」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
