---
article_id: kp-2bf1fcc797202628
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 0
learning_objective: 理解并验证：词级分词（word-level tokenization）的三个死穴
---

# 词级分词（word-level tokenization）的三个死穴

> **学习目标**：能够解释「词级分词（word-level tokenization）的三个死穴」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 为什么需要它

## 本次只学这一点

| 痛点 | 具体表现 | 量级 |
| --- | --- | --- |
| OOV（out-of-vocabulary） | 没见过的词只能映射成 `[UNK]`，信息归零 | 形态丰富语言（土耳其语、芬兰语）测试集 OOV 率可达 5% ~ 30% |
| 词表爆炸 | 想减少 OOV 就得把屈折形式、拼写变体全塞进词表 | 100 万词的 embedding：1e6 × 768 × 4 B ≈ **2.86 GiB**，只为存一张表 |
| 长尾稀疏 | 只出现 1~2 次的词，embedding 基本学不出语义 | Zipf 定律：语料中绝大多数词都在长尾 |

而且「词」这个概念本身就不牢靠：中文没有空格，`研究生物` 是 `研究/生物` 还是 `研究生/物`？德语会造复合词（`Lebensversicherungsgesellschaft`），日语没有分词边界。**让分词结果决定模型的输入单元，等于把一个语言学难题塞进了工程链路。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「词级分词（word-level tokenization）的三个死穴」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
