---
article_id: kp-2d1a5cbc8e2f7b4d
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a7ffbbd54d5
learning_sourceId: 3a7ffbbd54d5
learning_order: 14
learning_objective: 理解并验证：词向量层：one-hot 的「可训练」替代品
---

# 词向量层：one-hot 的「可训练」替代品

> **学习目标**：能够解释「词向量层：one-hot 的「可训练」替代品」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。
>
> **所属主题**：NLP 概述与文本预处理 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

vocab = ["<pad>", "酒店", "位置", "很好", "服务", "差"]
word2id = {w: i for i, w in enumerate(vocab)}

sentence = ["酒店", "位置", "很好"]
ids = torch.tensor([word2id[w] for w in sentence])

# num_embeddings=词表大小, embedding_dim=每个词的向量维度
embedding = nn.Embedding(num_embeddings=len(vocab), embedding_dim=4)
vecs = embedding(ids)
print(vecs.shape) # torch.Size([3, 4]) —— 3 个词，每个 4 维
```

对比一下 one-hot 与 embedding 的参数规模：one-hot 的「参数」是词表大小的稀疏向量，而 embedding 是一个 `词表大小 × 维度` 的可训练矩阵——后者维度可控，且训练后语义相近的词会自动靠近。这正是第 04 篇展开的内容。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「词向量层：one-hot 的「可训练」替代品」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)
