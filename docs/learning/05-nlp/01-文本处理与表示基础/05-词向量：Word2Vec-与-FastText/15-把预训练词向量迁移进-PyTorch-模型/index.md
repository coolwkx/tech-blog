---
article_id: kp-6dac3cea8a5b8a3c
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-5865c55f8aa7
learning_sourceId: 5865c55f8aa7
learning_order: 14
learning_objective: 理解并验证：把预训练词向量迁移进 PyTorch 模型
---

# 把预训练词向量迁移进 PyTorch 模型

> **学习目标**：能够解释「把预训练词向量迁移进 PyTorch 模型」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。
>
> **所属主题**：词向量：Word2Vec 与 FastText · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install torch gensim
import torch
import torch.nn as nn

vocab = ["<pad>", "<unk>", "肾结石", "治疗", "方法"]
word2id = {w: i for i, w in enumerate(vocab)}

# 假设从 gensim/keyedvectors 取到的向量（这里用随机值占位）
import numpy as np
pretrained = np.random.randn(len(vocab), 6).astype("float32")

# 关键：padding_idx 必须与 <pad> 一致，否则 PAD 也会被学成有语义的向量
embedding = nn.Embedding.from_pretrained(
torch.tensor(pretrained), freeze=False, padding_idx=word2id["<pad>"]
)

ids = torch.tensor([word2id[w] for w in ["肾结石", "治疗"]])
print(embedding(ids).shape) # [2, 6]

# 分层学习率：embedding 用 1e-5，分类头用 1e-3
optimizer = torch.optim.Adam([
{"params": embedding.parameters(), "lr": 1e-5},
], lr=1e-3)
print("OK")
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「把预训练词向量迁移进 PyTorch 模型」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/04-词向量-Word2Vec与FastText.md)
