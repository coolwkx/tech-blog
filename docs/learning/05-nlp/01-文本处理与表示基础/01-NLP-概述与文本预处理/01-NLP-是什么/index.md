---
article_id: kp-5629d70801282640
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a7ffbbd54d5
learning_sourceId: 3a7ffbbd54d5
learning_order: 0
learning_objective: 理解并验证：NLP 是什么
---

# NLP 是什么

> **学习目标**：能够解释「NLP 是什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。
>
> **所属主题**：NLP 概述与文本预处理 · 核心概念

## 本次只学这一点

人工智能（Artificial Intelligence, AI）的目标是让机器模仿甚至超越人的某项机能。按处理的信息模态，最常被拿来对比的三个方向是：

| 缩写 | 全称 | 处理对象 | 典型任务 |
|------|------|----------|----------|
| NLP | Natural Language Processing | 人类语言（文本 / 语音转写后的文本） | 分类、翻译、问答、摘要 |
| CV | Computer Vision | 图像、视频 | 检测、分割、识别 |
| ASR | Automatic Speech Recognition | 语音波形 | 语音转文字 |

NLP 的定义可以收紧成一句话：**让机器理解并生成人类语言**。注意「理解」和「生成」是两个方向——BERT 类模型偏理解（判别式），GPT 类模型偏生成（自回归），这也解释了后面第 09 篇为什么要分 Encoder-only / Decoder-only / Encoder-Decoder 三条技术路线。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「NLP 是什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)
