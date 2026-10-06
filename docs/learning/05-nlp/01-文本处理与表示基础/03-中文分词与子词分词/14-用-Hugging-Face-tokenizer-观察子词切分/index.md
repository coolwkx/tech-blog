---
article_id: kp-ab2228d108897102
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a66bd7ad2f1
learning_sourceId: 3a66bd7ad2f1
learning_order: 13
learning_objective: 理解并验证：用 Hugging Face tokenizer 观察子词切分
---

# 用 Hugging Face tokenizer 观察子词切分

> **学习目标**：能够解释「用 Hugging Face tokenizer 观察子词切分」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理流水线、序列标注的基本概念、Python 正则与字典操作。
>
> **所属主题**：中文分词与子词分词 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers
from transformers import BertTokenizer, GPT2Tokenizer

bert = BertTokenizer.from_pretrained("bert-base-uncased")
print(bert.tokenize("playing unbelievable tokenization"))
# ['playing', 'un', '##bel', '##ie', '##vable', 'token', '##ization']
# 注意 ## 前缀 = 该片段不是词首

gpt2 = GPT2Tokenizer.from_pretrained("gpt2")
print(gpt2.tokenize("playing unbelievable tokenization"))
# GPT-2 用字节级 BPE，切分结果与 WordPiece 不同

zh = BertTokenizer.from_pretrained("bert-base-chinese")
print(zh.tokenize("自然语言处理"))
# ['自', '然', '语', '言', '处', '理'] —— 中文 BERT 是字级
```

对比这三种输出，可以直观看到「同一句话在不同子词算法下粒度完全不同」，这也是不能跨模型混用 tokenizer 的原因。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 Hugging Face tokenizer 观察子词切分」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)
