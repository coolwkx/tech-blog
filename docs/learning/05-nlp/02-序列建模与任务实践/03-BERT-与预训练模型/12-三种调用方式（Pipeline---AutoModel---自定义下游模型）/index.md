---
article_id: kp-8bba1dce04d72f9a
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 11
learning_objective: 理解并验证：三种调用方式（Pipeline / AutoModel / 自定义下游模型）
---

# 三种调用方式（Pipeline / AutoModel / 自定义下游模型）

> **学习目标**：能够解释「三种调用方式（Pipeline / AutoModel / 自定义下游模型）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch datasets
import torch
import torch.nn as nn
from transformers import (pipeline, AutoTokenizer,
 AutoModelForSequenceClassification, BertModel)

MODEL_NAME = "bert-base-chinese" # 首次运行会联网下载；也可换成本地路径

# ---------- 方式一：Pipeline，三行搞定 ----------
clf = pipeline(task="text-classification", model=MODEL_NAME)
print(clf("这个产品非常好用，性价比很高"))

# 完形填空：注意 [MASK] 必须大写，且一次只能有一个 MASK
fill = pipeline(task="fill-mask", model=MODEL_NAME)
print([d["token_str"] for d in fill("我想明天去[MASK]家吃饭")][:5])

# 特征抽取：得到每个 token 的向量
feat = pipeline(task="feature-extraction", model=MODEL_NAME)
out = feat("人生该如何起头")
print("特征形状:", torch.tensor(out).shape) # [1, seq_len, 768]

# ---------- 方式二：AutoModel，手动编码与前向 ----------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.eval

encoded = tokenizer(
 ["这段文本很长，需要截断和补齐。" * 30],
 padding="max_length", # 不足补齐
 truncation=True, # 超长截断
 max_length=32,
 return_tensors="pt", # 返回 PyTorch 张量（二维）
)
print("input_ids :", encoded["input_ids"].shape)
print("token_type_ids :", encoded["token_type_ids"].shape)
print("attention_mask :", encoded["attention_mask"].shape)

with torch.no_grad:
 logits = model(**encoded).logits
print("logits:", logits.shape, "预测:", logits.argmax(-1).tolist())
```

对着打印出的形状理解三件输入：`input_ids` 是 token 的 ID，`token_type_ids`（也叫 segment ids）区分句子 A/B，`attention_mask` 标记哪些位置是真实 token（1）哪些是 PAD（0）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三种调用方式（Pipeline / AutoModel / 自定义下游模型）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
