---
article_id: kp-e6e35b897495583f
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-a9dec5ff9c41
learning_sourceId: a9dec5ff9c41
learning_order: 7
learning_objective: 理解并验证：-RNN与序列模型：可运行示例
---

# -RNN与序列模型：可运行示例

> **学习目标**：能够解释「-RNN与序列模型：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：多层前馈网络与反向传播、链式法则与 Jacobian、Logistic/Tanh 及其导数、梯度下降与学习率、PyTorch 的 `nn.Module` 与张量维度。
>
> **所属主题**：-RNN与序列模型 · 可运行示例

## 本次只学这一点

下面这段代码做四件事：(1) 用 `nn.RNN` 的权重张量手工逐时刻展开，与 `nn.RNN` 的输出逐元素比对，证明按时间展开等价于权值共享的前馈网络；(2) 打印并断言 `nn.RNN/nn.LSTM/nn.GRU` 及双向、多层配置下的输入输出形状；(3) 用 `pack_padded_sequence` 处理变长序列并取出每行**真实末位**状态；(4) 给出训练循环里的梯度截断写法。所有形状断言都用运行时张量维度（`-1` 处自动推断），已在 PyTorch 2.11 CPU 上跑通。

```python
import torch
import torch.nn as nn

torch.manual_seed(0)
B, T, M, D = 2, 4, 5, 3 # batch, seq_len, input_size, hidden_size
x = torch.randn(B, T, M)

# ---------- 1) nn.RNN 等价于手工按时间展开 ----------
rnn = nn.RNN(M, D, num_layers=1, nonlinearity="tanh", batch_first=True)
h0 = torch.zeros(1, B, D) # (num_layers*num_directions, batch, hidden)

out, hn = rnn(x, h0) # out: 每个时刻的隐状态；hn: 最后时刻的隐状态
assert out.shape == (B, T, D) # batch_first=True 时 out 为 (batch, seq_len, hidden)
assert hn.shape == (1, B, D)
assert torch.allclose(hn[0], out[:, -1]) # hn 就是最后一步的 h_T

# nn.RNN 把 weight_ih / weight_hh / bias_ih / bias_hh 拼接保存在 _flat_weights 的
# 前 4 个位置（单层单向），拆开即可手工复现前向计算：
w_ih, w_hh, b_ih, b_hh = rnn._flat_weights[:4] # (D,M) (D,D) (D,) (D,)
h = torch.zeros(B, D)
manual = []
for t in range(T):
 h = torch.tanh(x[:, t] @ w_ih.T + h @ w_hh.T + b_ih + b_hh)
 manual.append(h)
manual = torch.stack(manual, dim=1) # (B, T, D)
assert torch.allclose(manual, out, atol=1e-6) # 手工展开 == nn.RNN

# ---------- 2) 三种门控单元的形状（统一 batch_first=True） ----------
lstm = nn.LSTM(M, D, num_layers=2, batch_first=True)
gru = nn.GRU(M, D, num_layers=2, batch_first=True)

lstm_out, (hn_l, cn_l) = lstm(x, (torch.zeros(2, B, D), torch.zeros(2, B, D)))
assert lstm_out.shape == (B, T, D)
assert hn_l.shape == (2, B, D) and cn_l.shape == (2, B, D) # 2 = num_layers

gru_out, hn_g = gru(x) # 不传 h0 时默认全零初始化
assert gru_out.shape == (B, T, D) and hn_g.shape == (2, B, D)

# 取最后时刻做序列到类别（文本分类）的读出
logits = nn.Linear(D, 7)(lstm_out[:, -1]) # (B, D) -> (B, 7 类)
assert logits.shape == (B, 7)

# 双向：输出维度翻倍，隐状态首维 = num_layers * num_directions
bidi = nn.GRU(M, D, num_layers=2, bidirectional=True, batch_first=True)
bidi_out, hn_b = bidi(x)
assert bidi_out.shape == (B, T, 2 * D)
assert hn_b.shape == (2 * 2, B, D) # 前向2层 + 反向2层交替排列

# ---------- 3) 变长序列：pack_padded_sequence ----------
lengths = torch.tensor([4, 2]) # 必须按长度降序排列（默认 enforce_sorted=True）
packed = nn.utils.rnn.pack_padded_sequence(
 x, lengths, batch_first=True, enforce_sorted=True)
packed_out, packed_hn = rnn(packed, h0)
unpacked, out_lens = nn.utils.rnn.pad_packed_sequence(packed_out, batch_first=True)
assert unpacked.shape == (B, T, D) # 已还原为 (B, T, D)，短样本尾部补零
assert torch.equal(out_lens, lengths)
# packed_hn 里存的是每个样本**真实末位**（长度 2 的样本取第 2 步，不是第 4 步），
# 所以不能用 unpacked[:, -1]（那是补零位置）：
idx = (lengths - 1).view(-1, 1, 1).expand(-1, 1, D) # 每个样本的真实末位下标
last_real = unpacked.gather(1, idx).squeeze(1) # (B, D)
assert torch.allclose(last_real, packed_hn[0], atol=1e-6)
# 也可用 torch.nn.utils.rnn.unpad_sequence(unpacked, lengths, batch_first=True) 直接拿掉填充。

# ---------- 4) 训练循环中的梯度截断（防梯度爆炸） ----------
opt = torch.optim.Adam(bidi.parameters(), lr=1e-3)
loss = bidi_out.pow(2).mean
opt.zero_grad()
loss.backward()
total_norm = nn.utils.clip_grad_norm_(bidi.parameters(), max_norm=5.0)
print(f"grad norm before clip = {total_norm:.4f}")
opt.step
print("all checks passed")
```

**关键形状速查**（`batch_first=True`）：输入 `(batch, seq_len, input_size)` → `output` 为 `(batch, seq_len, hidden_size * num_directions)`，`h_n` 为 `(num_layers * num_directions, batch, hidden_size)`；LSTM 额外返回 `c_n`，形状与 `h_n` 相同。**`batch_first=True` 只影响输入/输出的前两维，不影响 `h_n`/`c_n`**——后者的第一维永远是层数乘方向数，这是最常见的形状踩坑点。

**`pack_padded_sequence` 要点**：(1) `lengths` 必须是 CPU 上的 `LongTensor`，默认要求**降序**，否则需 `enforce_sorted=False`（内部会自己排序并把 `h_n` 还原）；(2) 打包后 RNN 只对有效时刻前向，**不会**让填充位参与门控计算，因此 `h_n` 是每个样本真实末位状态；(3) 输出是 `PackedSequence`，必须 `pad_packed_sequence` 才能拿回规则张量；(4) 计算损失时要配 `ignore_index` 或掩码，避免填充位贡献梯度。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-RNN与序列模型：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/04-序列与注意力/06-RNN与序列模型.md)
