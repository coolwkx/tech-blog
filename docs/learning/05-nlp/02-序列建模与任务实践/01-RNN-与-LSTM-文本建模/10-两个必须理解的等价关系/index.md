---
article_id: kp-96841239c7e9ef5c
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 9
learning_objective: 理解并验证：两个必须理解的等价关系
---

# 两个必须理解的等价关系

> **学习目标**：能够解释「两个必须理解的等价关系」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 方法细节

## 本次只学这一点

**（1）`log_softmax` + `NLLLoss` ≡ `CrossEntropyLoss`**

PyTorch 的 `CrossEntropyLoss` 内部就是 `log_softmax` + `NLLLoss`。因此两种写法等价：

```python
# 写法 A
criterion = nn.CrossEntropyLoss
loss = criterion(logits, y) # logits 是未归一化的输出

# 写法 B（等价）
criterion = nn.NLLLoss
log_prob = nn.LogSoftmax(dim=-1)(logits)
loss = criterion(log_prob, y)
```

为什么代码偏爱写法 B？因为 `log_softmax` 与 NLL 都工作在**对数域**，数值更稳定（避免先 softmax 得到 0 概率再取 log 变成 $-\infty$）。但要注意：**用了写法 B 就不能再在模型外做 softmax**，否则概率被归一化两次，损失完全错乱。这也是「输出层用了 softmax，又接 CrossEntropyLoss」成为高频 bug 的原因。

**（2）`sparse=True` 的 Embedding 需要稀疏优化器**

`nn.Embedding(vocab_size, dim, sparse=True)` 在反向传播时只更新被激活的行，词表大时能省大量内存与计算。但普通 `Adam` 不支持稀疏梯度，需要换 `SparseAdam` 或用 `Adagrad`（`torch.optim.SparseAdam`）。用错优化器会直接报错。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两个必须理解的等价关系」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
