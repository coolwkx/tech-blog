---
article_id: kp-0547c705191c4ce9
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 12
learning_objective: 理解并验证：位置编码、前馈层、LayerNorm、子层连接
---

# 位置编码、前馈层、LayerNorm、子层连接

> **学习目标**：能够解释「位置编码、前馈层、LayerNorm、子层连接」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 可运行示例

## 本次只学这一点

```python
class Embeddings(nn.Module):
    def __init__(self, d_model, vocab):
        super.__init__
        self.d_model = d_model
        self.lut = nn.Embedding(vocab, d_model)

        def forward(self, x):
            return self.lut(x) * math.sqrt(self.d_model) # 与位置编码量级匹配

        class PositionalEncoding(nn.Module):
            def __init__(self, d_model, dropout=0.1, max_len=5000):
                super.__init__
                self.dropout = nn.Dropout(p=dropout)
                pe = torch.zeros(max_len, d_model)
                position = torch.arange(0, max_len).unsqueeze(1).float # [max_len,1]
                div_term = torch.exp(
                torch.arange(0, d_model, 2).float * (-math.log(10000.0) / d_model)
                ) # [d_model/2]
                pe[:, 0::2] = torch.sin(position * div_term) # 偶数列
                pe[:, 1::2] = torch.cos(position * div_term) # 奇数列
                # register_buffer: 随模型保存/迁移，但不作为可训练参数
                self.register_buffer("pe", pe.unsqueeze(0)) # [1,max_len,d_model]

                def forward(self, x):
                    x = x + self.pe[:, :x.size(1)]
                    return self.dropout(x)

                class PositionwiseFeedForward(nn.Module):
                    def __init__(self, d_model, d_ff, dropout=0.1):
                        super.__init__
                        self.w1 = nn.Linear(d_model, d_ff)
                        self.w2 = nn.Linear(d_ff, d_model)
                        self.dropout = nn.Dropout(p=dropout)

                        def forward(self, x):
                            return self.w2(self.dropout(F.relu(self.w1(x))))

                        class LayerNorm(nn.Module):
                            def __init__(self, features, eps=1e-6):
                                super.__init__
                                self.a2 = nn.Parameter(torch.ones(features)) # gamma
                                self.b2 = nn.Parameter(torch.zeros(features)) # beta
                                self.eps = eps

                                def forward(self, x):
                                    mean = x.mean(-1, keepdim=True)
                                    std = x.std(-1, keepdim=True)
                                    return self.a2 * (x - mean) / (std + self.eps) + self.b2

                                class SublayerConnection(nn.Module):
                                    """Pre-LN 残差结构: x + dropout(sublayer(norm(x)))"""

                                    def __init__(self, size, dropout=0.1):
                                        super.__init__
                                        self.norm = LayerNorm(size)
                                        self.dropout = nn.Dropout(dropout)

                                        def forward(self, x, sublayer):
                                            return x + self.dropout(sublayer(self.norm(x)))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「位置编码、前馈层、LayerNorm、子层连接」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
