---
article_id: kp-91d9af7604ef69df
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a7ffbbd54d5
learning_sourceId: 3a7ffbbd54d5
learning_order: 12
learning_objective: 理解并验证：n-gram 特征与文本长度规范（纯 numpy，无额外依赖）
---

# n-gram 特征与文本长度规范（纯 numpy，无额外依赖）

> **学习目标**：能够解释「n-gram 特征与文本长度规范（纯 numpy，无额外依赖）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。
>
> **所属主题**：NLP 概述与文本预处理 · 可运行示例

## 本次只学这一点

```python
import numpy as np

def add_n_gram(a: list, n: int = 2) -> set:
 """把列表 a 切成 n-gram 集合，例如 [1,3,2,1,5,3] -> {(1,3),(3,2),...}"""
 return set(zip(*[a[i:] for i in range(n)]))

print(add_n_gram([1, 3, 2, 1, 5, 3], n=2))
# {(1, 3), (3, 2), (2, 1), (1, 5), (5, 3)}

def my_padding(x: list, max_len: int = 5) -> list:
 """先截断再补齐: 取前 max_len 个，不足则尾部补 0"""
 x = x[:max_len]
 x = x + [0] * (max_len - len(x))
 return x

print(my_padding([1, 2, 3, 45, 5, 6, 7, 8], max_len=5)) # [1, 2, 3, 45, 5]
print(my_padding([1, 2], max_len=5)) # [1, 2, 0, 0, 0]
```

如果要按 batch 统一长度，`keras` 的 API 更省事（注意顺序：先截断后补齐）：

```python
# 依赖: pip install tensorflow (或用 numpy 手写上面的 my_padding 代替)
from tensorflow.keras.preprocessing import sequence

x_train = [[1, 23, 5, 32, 55, 63, 2, 21, 78, 32, 23, 1],
[2, 32, 1, 23, 1]]
print(sequence.pad_sequences(x_train, maxlen=10, padding="post", truncating="pre"))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「n-gram 特征与文本长度规范（纯 numpy，无额外依赖）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)
