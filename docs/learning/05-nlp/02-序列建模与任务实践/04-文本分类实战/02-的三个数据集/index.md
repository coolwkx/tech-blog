---
article_id: kp-64fe88f390e21f10
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d8ba07ef6cec
learning_sourceId: d8ba07ef6cec
learning_order: 1
learning_objective: 理解并验证：的三个数据集
---

# 的三个数据集

> **学习目标**：能够解释「的三个数据集」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 02 篇分词、第 03 篇 TF-IDF 与稀疏矩阵、第 04 篇词向量与 FastText、sklearn 的基本用法。
>
> **所属主题**：文本分类实战 · 核心概念

## 本次只学这一点

| 数据集 | 规模 | 类别数 | 格式 | 特点 | 用途 |
|--------|------|--------|------|------|------|
| AG News（新闻主题） | 12 万训练 / 7600 测试 | 4（World / Sports / Business / Sci-Tech） | CSV：标签, 标题, 正文 | 英文、类别均衡、文本较短 | 浅层网络教学案例 |
| 头条新闻（文本分类） | 18 万（每类约 1.8 万） | 10（finance / realty / stocks / education / science / society / politics / sports / game / entertainment） | `文本\t标签ID`（label 从 0 开始） | 中文、高度均衡、短文本（截断到 30 字） | 传统 ML → FastText → BERT 全链路对比 |
| 酒店评论（ChnSentiCorp） | 训练 + 验证 | 2（0 消极 / 1 积极） | TSV：`sentence\tlabel` | 中文、正负略不均衡 | 文本数据分析与情感分析（见第 11 篇） |

头条数据集的标签体系值得记住，它是后面第 12 篇医疗分类的对照：0 finance、1 realty、2 stocks、3 education、4 science、5 society、6 politics、7 sports、8 game、9 entertainment。`class.txt` 每行一个类别名，行号即 label ID。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「的三个数据集」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)
