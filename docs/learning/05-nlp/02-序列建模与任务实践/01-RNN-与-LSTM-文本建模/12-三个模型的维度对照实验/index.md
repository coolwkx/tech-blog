---
article_id: kp-2b91d1c56d659017
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 11
learning_objective: 理解并验证：三个模型的维度对照实验
---

# 三个模型的维度对照实验

> **学习目标**：能够解释「三个模型的维度对照实验」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

batch, seq_len, input_size, hidden = 4, 10, 8, 6

for name, layer in [("RNN", nn.RNN(input_size, hidden, num_layers=1, batch_first=True)),
 ("LSTM", nn.LSTM(input_size, hidden, num_layers=1, batch_first=True)),
 ("GRU", nn.GRU(input_size, hidden, num_layers=1, batch_first=True))]:
 x = torch.randn(batch, seq_len, input_size)
 out = layer(x) # 不传初始状态时，PyTorch 自动初始化为 0
 output = out[0]
 state = out[1]
 print(f"{name:4s} output={tuple(output.shape)} state={type(state).__name__}"
 f" {tuple(state.shape) if torch.is_tensor(state) else [tuple(s.shape) for s in state]}")

# 双向 + 2 层
bi = nn.LSTM(input_size, hidden, num_layers=2, bidirectional=True, batch_first=True)
x = torch.randn(batch, seq_len, input_size)
output, (hn, cn) = bi(x)
print("双向2层 output:", tuple(output.shape)) # (4, 10, 12) = hidden*2
print("双向2层 hn :", tuple(hn.shape)) # (4, 4, 6) = num_layers*2
```

记住两条形状规律：**output 的最后一维 = `hidden_size × num_directions`**；**hn/cn 的第一维 = `num_layers × num_directions`**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三个模型的维度对照实验」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
