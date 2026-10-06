---
article_id: "c50c390e51bf"
learning_kind: "guide"
learning_category: "05-nlp"
---

# ② 序列建模与 Transformer

> 本章共 3 篇笔记。

## 本节目录

| 笔记 | 难度 | 预计用时 | 状态 |
| --- | --- | --- | --- |
| [2.1 RNN 与 LSTM 文本建模](07-RNN与LSTM文本建模.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [2.2 Attention 与 Transformer](08-Attention与Transformer.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [2.3 BERT 与预训练模型](09-BERT与预训练模型.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |

## 本章要回答的问题

**2.1 RNN 与 LSTM 文本建模**
- 说清 RNN 的四种输入输出结构（N vs N / N vs 1 / 1 vs N / N vs M）及各自的应用场景。
- 写出 LSTM 三个门与细胞状态的公式，并解释门控为什么能缓解梯度消失。
- 用 `nn.RNN` / `nn.LSTM` / `nn.GRU` 搭一个人名（字符级短文本）分类器，并正确对齐张量维度。

**2.2 Attention 与 Transformer**
- 手写 Scaled Dot-Product Attention 与 Multi-Head Attention，并解释除以 $\sqrt{d_k}$ 的数学原因。
- 说清 Encoder Block 与 Decoder Block 的结构差异，以及 padding mask 与 look-ahead mask 各自防的是什么。
- 从零搭出一个可前向传播的 Transformer，并解释位置编码为什么用三角函数、embedding 为什么要乘 $\sqrt{d_{model}}$。

**2.3 BERT 与预训练模型**
- 说清 Encoder-Only / Decoder-Only / Encoder-Decoder 三条技术路线的差别与代表模型。
- 解释 BERT 的三个 Embedding、两大预训练任务，以及 MLM 为什么用 80%/10%/10%。
- 用 `pipeline` / `AutoModel` / 自定义下游模型三种方式调用中文 BERT 完成分类任务。

状态说明：✅ 已完成 ｜ 🚧 编写中 ｜ 📝 计划中

---

[⬅️ 返回本区目录](../README.md)
