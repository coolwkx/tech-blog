---
article_id: kp-7f761aa7e4f6eaa5
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 2
learning_objective: 理解并验证：四条路线的对比目标
---

# 四条路线的对比目标

> **学习目标**：能够解释「四条路线的对比目标」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 项目目标与业务背景

## 本次只学这一点

| 路线 | 代表技术 | 想回答的问题 |
| --- | --- | --- |
| ① 传统机器学习 | TF-IDF + 随机森林 | 不用深度学习的基线在哪？ |
| ② 浅层神经网络 | FastText | 引入词向量和 n-gram 能提升多少？成本几何？ |
| ③ 预训练语言模型 | BERT + 微调 | 上下文建模的精度上限在哪？代价是什么？ |
| ④ 部署优化 | 量化 / 蒸馏 | 怎么在几乎不掉点的前提下把模型变小变快？ |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四条路线的对比目标」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
