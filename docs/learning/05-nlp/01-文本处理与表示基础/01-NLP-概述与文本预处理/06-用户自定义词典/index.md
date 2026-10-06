---
article_id: kp-d748bffa4d1e0caa
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a7ffbbd54d5
learning_sourceId: 3a7ffbbd54d5
learning_order: 5
learning_objective: 理解并验证：用户自定义词典
---

# 用户自定义词典

> **学习目标**：能够解释「用户自定义词典」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。
>
> **所属主题**：NLP 概述与文本预处理 · 方法细节

## 本次只学这一点

专有名词（品牌名、领域术语）是分词错误的重灾区。jieba 支持加载自定义词典，格式为：

```
词语 词频 词性
```

其中词频和词性都可省略。加载后，jieba 会优先考虑词典里的词。工程上有两种用法：

```python
jieba.load_userdict("userdict.txt") # 全局生效
jieba.add_word("自然语言处理") # 动态加一个词
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用户自定义词典」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)
