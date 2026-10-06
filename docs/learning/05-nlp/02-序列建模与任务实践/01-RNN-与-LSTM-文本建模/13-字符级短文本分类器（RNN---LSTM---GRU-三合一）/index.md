---
article_id: kp-1e9ab73b6d56fa63
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 12
learning_objective: 理解并验证：字符级短文本分类器（RNN / LSTM / GRU 三合一）
---

# 字符级短文本分类器（RNN / LSTM / GRU 三合一）

> **学习目标**：能够解释「字符级短文本分类器（RNN / LSTM / GRU 三合一）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install torch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ---------- 1. 内联小数据集：字符级人名 -> 国别 ----------
raw = [("zhang", "Chinese"), ("wang", "Chinese"), ("liu", "Chinese"), ("chen", "Chinese"),
("smith", "English"), ("brown", "English"), ("jones", "English"), ("wilson", "English"),
("yuasa", "Japanese"), ("yuhara", "Japanese"), ("tanaka", "Japanese"), ("suzuki", "Japanese")]

classes = sorted({c for _, c in raw})
class2id = {c: i for i, c in enumerate(classes)}
chars = sorted({ch for name, _ in raw for ch in name})
char2id = {ch: i + 1 for i, ch in enumerate(chars)} # 0 留给 PAD

MAX_LEN = 10
n_chars = len(char2id) + 1

def name_to_tensor(name: str) -> torch.Tensor:
    """字符 -> id 序列，补齐或截断到 MAX_LEN"""
    ids = [char2id.get(ch, 0) for ch in name.lower()][:MAX_LEN]
    ids += [0] * (MAX_LEN - len(ids))
    return torch.tensor(ids, dtype=torch.long)

class NameDataset(Dataset):
    def __init__(self, data):
        self.x = [name_to_tensor(n) for n, _ in data]
        self.y = [class2id[c] for _, c in data]

        def __len__(self):
            return len(self.x)

        def __getitem__(self, idx):
            return self.x[idx], torch.tensor(self.y[idx], dtype=torch.long)

        # ---------- 2. 模型：Embedding + RNN/LSTM/GRU + 取最后时间步 ----------
        class NameClassifier(nn.Module):
            def __init__(self, rnn_type="lstm", vocab_size=n_chars, embed_dim=16,
            hidden_size=32, num_class=len(classes), num_layers=1):
                super.__init__
                self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
                # batch_first=True: 输入为 (batch, seq_len, embed_dim)
                rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[rnn_type]
                self.rnn = rnn_cls(embed_dim, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, num_class)
                self.log_softmax = nn.LogSoftmax(dim=-1)

                def forward(self, x):
                    emb = self.embedding(x) # (B, L, E)
                    output, _ = self.rnn(emb) # (B, L, H)
                    last = output[:, -1, :] # 取最后一个时间步 -> (B, H)
                    return self.log_softmax(self.fc(last)) # 配 NLLLoss 使用

                # ---------- 3. 训练与预测 ----------
                def train_model(rnn_type, epochs=80):
                    torch.manual_seed(0)
                    loader = DataLoader(NameDataset(raw), batch_size=4, shuffle=True)
                    model = NameClassifier(rnn_type=rnn_type)
                    criterion = nn.NLLLoss # 与模型内 log_softmax 配对
                    optimizer = optim.Adam(model.parameters(), lr=0.01)
                    # RNN 训练标配：梯度裁剪，防止梯度爆炸
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

                    for epoch in range(epochs):
                        total_loss = 0.0
                        for x, y in loader:
                            out = model(x)
                            loss = criterion(out, y)
                            optimizer.zero_grad()
                            loss.backward()
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
                            optimizer.step
                            total_loss += loss.item
                            if (epoch + 1) % 20 == 0:
                                print(f" [{rnn_type}] epoch {epoch+1:3d} loss={total_loss/len(loader):.4f}")
                                return model

                            def predict(model, name):
                                model.eval
                                with torch.no_grad:
                                    out = model(name_to_tensor(name).unsqueeze(0)) # 加 batch 维
                                    prob = out.exp
                                    idx = int(prob.argmax(dim=-1))
                                    return classes[idx], float(prob[0, idx])

                                if __name__ == "__main__":
                                    for rnn_type in ["rnn", "lstm", "gru"]:
                                        m = train_model(rnn_type)
                                        acc = sum(predict(m, n)[0] == c for n, c in raw) / len(raw)
                                        print(f"{rnn_type.upper():4s} 训练集准确率: {acc:.3f} 预测('zhang')={predict(m, 'zhang')}")
```

要点说明：

- `padding_idx=0` 保证 PAD 的向量恒为 0 且不参与梯度更新。
- 取 `output[:, -1, :]` 得整句表示；**如果样本有 padding，最后一个时间步可能是 PAD**，此时应先按真实长度取 `output[i, len_i - 1, :]`（或使用 `pack_padded_sequence`）。本示例把名字统一补到 10 且 `names` 较短，影响有限，但真实项目必须处理。
- `clip_grad_norm_` 在 `step` 之前调用，且应在 `backward` 之后。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「字符级短文本分类器（RNN / LSTM / GRU 三合一）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
