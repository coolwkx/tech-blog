---
article_id: kp-ee00571db8520307
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 13
learning_objective: 理解并验证：验证 LSTM 的长依赖能力（门控的直观效果）
---

# 验证 LSTM 的长依赖能力（门控的直观效果）

> **学习目标**：能够解释「验证 LSTM 的长依赖能力（门控的直观效果）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

# 任务：序列末尾输出「开头那个 token 的 id」——需要记住 T 步之前的信息
def make_batch(batch=32, seq_len=60, vocab=10):
    x = torch.randint(1, vocab, (batch, seq_len))
    y = x[:, 0] # 标签 = 第一个 token
    return x, y

def run(rnn_type, seq_len=60, steps=300):
    torch.manual_seed(42)
    embed = nn.Embedding(10, 16, padding_idx=0)
    rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[rnn_type]
    rnn = rnn_cls(16, 32, batch_first=True)
    fc = nn.Linear(32, 10)
    params = list(embed.parameters()) + list(rnn.parameters()) + list(fc.parameters())
    opt = torch.optim.Adam(params, lr=0.01)
    crit = nn.CrossEntropyLoss

    for step in range(steps):
        x, y = make_batch(seq_len=seq_len)
        out, _ = rnn(embed(x))
        logits = fc(out[:, -1, :])
        loss = crit(logits, y)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step

        with torch.no_grad:
            x, y = make_batch(seq_len=seq_len)
            out, _ = rnn(embed(x))
            pred = fc(out[:, -1, :]).argmax(-1)
            acc = (pred == y).float.mean.item
            return acc

        for t in ["rnn", "lstm", "gru"]:
            for L in [10, 40]:
                print(f"{t:4s} seq_len={L:3d} 准确率={run(t, seq_len=L):.3f}")
```

预期现象：序列短（10）时三者都能学到；序列变长（40–60）时传统 RNN 的准确率明显掉到随机水平附近，而 LSTM / GRU 仍能保持较高准确率——这就是门控带来的长依赖能力差异。想更直观，可以把 `seq_len` 继续加大到 100 以上，观察 RNN 与 LSTM 的差距。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「验证 LSTM 的长依赖能力（门控的直观效果）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
