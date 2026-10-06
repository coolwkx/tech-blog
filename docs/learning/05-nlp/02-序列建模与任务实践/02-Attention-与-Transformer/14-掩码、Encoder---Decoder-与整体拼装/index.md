---
article_id: kp-287f8b3cbf11a1c4
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 13
learning_objective: 理解并验证：掩码、Encoder / Decoder 与整体拼装
---

# 掩码、Encoder / Decoder 与整体拼装

> **学习目标**：能够解释「掩码、Encoder / Decoder 与整体拼装」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 可运行示例

## 本次只学这一点

```python
def subsequent_mask(size):
    """下三角矩阵: 位置 i 只能看到 <= i 的信息"""
    triu = torch.triu(torch.ones(1, size, size), diagonal=1) # 上三角(不含对角线)
    return (1 - triu).to(torch.uint8)

class EncoderLayer(nn.Module):
    def __init__(self, size, self_attn, feed_forward, dropout):
        super.__init__
        self.self_attn = self_attn
        self.feed_forward = feed_forward
        self.sublayer = clones(SublayerConnection(size, dropout), 2)
        self.size = size

        def forward(self, x, mask):
            x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, mask))
            return self.sublayer[1](x, self.feed_forward)

        class Encoder(nn.Module):
            def __init__(self, layer, n):
                super.__init__
                self.layers = clones(layer, n)
                self.norm = LayerNorm(layer.size)

                def forward(self, x, mask):
                    for layer in self.layers:
                        x = layer(x, mask)
                        return self.norm(x)

                    class DecoderLayer(nn.Module):
                        def __init__(self, size, self_attn, src_attn, feed_forward, dropout):
                            super.__init__
                            self.size = size
                            self.self_attn = self_attn # Q = K = V
                            self.src_attn = src_attn # Q != K = V
                            self.feed_forward = feed_forward
                            self.sublayer = clones(SublayerConnection(size, dropout), 3)

                            def forward(self, x, memory, source_mask, target_mask):
                                m = memory
                                x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, target_mask))
                                x = self.sublayer[1](x, lambda x: self.src_attn(x, m, m, source_mask))
                                return self.sublayer[2](x, self.feed_forward)

                            class Decoder(nn.Module):
                                def __init__(self, layer, n):
                                    super.__init__
                                    self.layers = clones(layer, n)
                                    self.norm = LayerNorm(layer.size)

                                    def forward(self, x, memory, source_mask, target_mask):
                                        for layer in self.layers:
                                            x = layer(x, memory, source_mask, target_mask)
                                            return self.norm(x)

                                        class Generator(nn.Module):
                                            def __init__(self, d_model, vocab_size):
                                                super.__init__
                                                self.project = nn.Linear(d_model, vocab_size)

                                                def forward(self, x):
                                                    # 训练配 NLLLoss，与 CrossEntropyLoss 等价但数值更稳
                                                    return F.log_softmax(self.project(x), dim=-1)

                                                class EncoderDecoder(nn.Module):
                                                    def __init__(self, encoder, decoder, src_embed, tgt_embed, generator):
                                                        super.__init__
                                                        self.encoder, self.decoder = encoder, decoder
                                                        self.src_embed, self.tgt_embed = src_embed, tgt_embed
                                                        self.generator = generator

                                                        def encode(self, source, source_mask):
                                                            return self.encoder(self.src_embed(source), source_mask)

                                                        def decode(self, memory, source_mask, target, target_mask):
                                                            return self.decoder(self.tgt_embed(target), memory, source_mask, target_mask)

                                                        def forward(self, source, target, source_mask, target_mask):
                                                            return self.generator(
                                                        self.decode(self.encode(source, source_mask), source_mask, target, target_mask)
                                                        )

                                                        def make_model(src_vocab, tgt_vocab, n=6, d_model=512, d_ff=2048, head=8, dropout=0.1):
                                                            c = copy.deepcopy
                                                            attn = MultiHeadedAttention(head, d_model, dropout)
                                                            ff = PositionwiseFeedForward(d_model, d_ff, dropout)
                                                            position = PositionalEncoding(d_model, dropout)
                                                            model = EncoderDecoder(
                                                            Encoder(EncoderLayer(d_model, c(attn), c(ff), dropout), n),
                                                            Decoder(DecoderLayer(d_model, c(attn), c(attn), c(ff), dropout), n),
                                                            nn.Sequential(Embeddings(d_model, src_vocab), c(position)),
                                                            nn.Sequential(Embeddings(d_model, tgt_vocab), c(position)),
                                                            Generator(d_model, tgt_vocab),
                                                            )
                                                            for p in model.parameters():
                                                                if p.dim > 1:
                                                                    nn.init.xavier_uniform_(p)
                                                                    return model

                                                                if __name__ == "__main__":
                                                                    batch, src_len, tgt_len, vocab = 2, 5, 6, 100
                                                                    model = make_model(vocab, vocab, n=2, d_model=64, d_ff=256, head=8)
                                                                    src = torch.randint(1, vocab, (batch, src_len))
                                                                    tgt = torch.randint(1, vocab, (batch, tgt_len))
                                                                    src_mask = torch.ones(batch, 1, src_len).to(torch.uint8)
                                                                    tgt_mask = subsequent_mask(tgt_len) # [1,tgt_len,tgt_len]

                                                                    out = model(src, tgt, src_mask, tgt_mask)
                                                                    print("输出形状:", out.shape) # [2, 6, 100]
                                                                    print(subsequent_mask(4).squeeze(0)) # 验证 look-ahead mask
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「掩码、Encoder / Decoder 与整体拼装」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
