---
article_id: kp-6d329cc9428a7211
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 7
learning_objective: 理解并验证：Sentence-BERT（SBERT）
---

# Sentence-BERT（SBERT）

> **学习目标**：能够解释「Sentence-BERT（SBERT）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 方法细节

## 本次只学这一点

**问题**：直接用 BERT 输出 `[CLS]` 或平均 `last_hidden_state` 做句向量，效果**很差**——因为 BERT 从未被训练成「让相似句子的向量靠近」。SBERT 论文的实测显示，原始 BERT 的句向量在 STS 任务上甚至不如 GloVe 平均。

**解法**：用**孪生网络（Siamese）**结构 + 句对监督做微调：

```
 句子A ──► BERT ──► pool ──► u ─┐
 ├──► 余弦相似度（或拼接后分类）
 句子B ──► BERT(共享权重) ──► pool ──► v ─┘
```

关键设计：

| 设计点 | 做法 | 原因 |
|--------|------|------|
| 权重共享 | A、B 用同一个 BERT | 保证两段文本映射到同一空间；参数量减半 |
| 池化策略 | 默认取 `[CLS]`；也可 mean-pooling / max-pooling | mean-pooling 在多数任务上更稳，`[CLS]` 需要专门训练过才好用 |
| 训练目标 | 分类目标（softmax 三分类：蕴含/中立/矛盾）或回归目标（余弦相似度 MSE）或 triplet 排序损失 | 分类目标适合 NLI 数据（SNLI/MNLI），回归/排序适合 STS 数据 |
| 推理 | 句子独立编码，向量可缓存 | 换来了可索引、可离线预计算的工程优势 |

**为什么效果能提升**：SBERT 把「相似度」变成了训练目标的一部分，模型被显式优化为「相似句靠近、不相似句远离」。这本质上是在做**度量学习（metric learning）**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Sentence-BERT（SBERT）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
