---
article_id: kp-8f0848b884aa42a7
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 8
learning_objective: 理解并验证：PyTorch 中的维度约定（最容易出错的地方）
---

# PyTorch 中的维度约定（最容易出错的地方）

> **学习目标**：能够解释「PyTorch 中的维度约定（最容易出错的地方）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 方法细节

## 本次只学这一点

`nn.RNN` / `nn.LSTM` / `nn.GRU` 的默认布局是 `batch_first=False`：

| 张量 | 形状 | 说明 |
|------|------|------|
| 输入 `input` | `(seq_len, batch, input_size)` | 默认；`batch_first=True` 时变为 `(batch, seq_len, input_size)` |
| 初始隐状态 `h0` | `(num_layers * num_directions, batch, hidden_size)` | 双向时第一维乘 2 |
| 初始细胞状态 `c0`（仅 LSTM） | 同 `h0` | — |
| 输出 `output` | `(seq_len, batch, hidden_size * num_directions)` | 每个时间步的隐状态 |
| 末状态 `hn` | `(num_layers * num_directions, batch, hidden_size)` | — |

**分类任务的取法**：N vs 1 结构要取**最后一个时间步**的输出。若 `batch_first=True`，写 `output[:, -1, :]`；若默认布局，写 `output[-1]`。代码里 `lstm_output[0][-1].unsqueeze(0)` 是在 `batch_size=1` 下的等价写法（先取第 0 个样本，再取最后一个时间步）——这种下标写法在 batch>1 时会出错，务必改用 `output[:, -1, :]`。

代码与在此处还有一处差异：用默认 `batch_first=False`，而实现统一设置了 `batch_first=True`，理由是 `DataLoader` 返回的 `x` 形状是 `(batch, seq_len, input_size)`，设为 True 可以直接承接，避免反复 `transpose`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PyTorch 中的维度约定（最容易出错的地方）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
