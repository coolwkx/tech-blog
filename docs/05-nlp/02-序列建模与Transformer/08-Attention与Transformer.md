# 08 Attention 与 Transformer

> **一句话总结**：用「Query-Key 相似度加权 Value」替代 RNN 的逐步递归，让序列建模第一次可以大规模并行。
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。

> 1. 手写 Scaled Dot-Product Attention 与 Multi-Head Attention，并解释除以 $\sqrt{d_k}$ 的数学原因。
> 2. 说清 Encoder Block 与 Decoder Block 的结构差异，以及 padding mask 与 look-ahead mask 各自防的是什么。
> 3. 从零搭出一个可前向传播的 Transformer，并解释位置编码为什么用三角函数、embedding 为什么要乘 $\sqrt{d_{model}}$。

## 1. 核心概念

### 1.1 为什么需要 Transformer

2017 年 Transformer 被提出，2018 年 BERT 让它成为主流。它的两大优势正是 seq2seq + RNN 两大缺陷的对症药：

| seq2seq（RNN 版）的缺陷 | 后果 | Transformer 的改进 |
|---|---|---|
| Encoder 把整个源句压缩成一个固定长度向量 | 长句信息严重损耗 | Multi-Head Attention 让解码器直接看到编码器每个位置，不再依赖单一向量 |
| 时间步必须串行递归 | 训练慢，长序列尤其慢 | Encoder 端可完全并行（矩阵运算一次算完所有时间步） |

「并行」有两个层次：**结构层面** Encoder 可并行、Decoder 只在训练时并行（预测时第 $t$ 步依赖第 $t-1$ 步输出，天然串行）；**算子实现层面** self-attention 通过矩阵乘法一次算完所有 token，但 token 之间仍有计算依赖，并非各 token 独立。Embedding、Feed Forward、Add & Norm 都是逐位置独立的，可完全并行。

### 1.2 整体架构四大件

| 部分 | 组成 | 作用 |
|------|------|------|
| 输入部分 | Word Embedding + Positional Encoding | 把 token 变成向量并注入位置信息 |
| 编码器部分 | $N$ 个 Encoder Layer 堆叠 | 每层 2 个子层：多头自注意力、前馈全连接 |
| 解码器部分 | $N$ 个 Decoder Layer 堆叠 | 每层 3 个子层：掩码多头自注意力、Encoder-Decoder 注意力、前馈全连接 |
| 输出部分 | Linear + softmax（实现上用 `log_softmax`） | 把 $d_{model}$ 维隐状态映射到词表维度 |

论文 base 配置：$N=6$、$d_{model}=512$、$d_{ff}=2048$、$head=8$、$dropout=0.1$。注意 $d_{ff}=4\times d_{model}$ 是经验上的 4 倍关系。

### 1.3 每个子模块的职责

| 子模块 | 位置 | 关键点 |
|--------|------|--------|
| Scaled Dot-Product Attention | Encoder / Decoder 内部 | $Q=K=V$ 时是 self-attention；$Q\neq K=V$ 时是 cross-attention |
| Multi-Head Attention | 同上 | 把 $d_{model}$ 切成 $h$ 份并行做 attention 再 concat，多个子空间关注不同信息 |
| Feed Forward | 每个 Block 内 | 两个线性层夹一个 ReLU，$d_{model}\to d_{ff}\to d_{model}$，增强拟合能力 |
| Add & Norm | 每个子层之后 | Add = 残差连接（信息无损耗地传得更深）；Norm = LayerNorm（防参数过大过小、收敛变慢） |
| Positional Encoding | 输入部分 | 三角函数计算，周期函数不受长度限制，值域 $[-1,1]$ 有助于梯度计算 |

### 1.4 掩码（mask）与注意力类型

| 掩码类型 | 防的问题 | 使用位置 |
|------|----------|----------|
| Padding Mask | 补齐用的 PAD 参与注意力，稀释真实信息 | Encoder/Decoder 的 self-attention 与 cross-attention |
| Sequence / Look-ahead Mask | 解码时提前看到未来 token，训练与预测行为不一致 | 仅 Decoder 的 self-attention |

约定：mask 由 0/1 组成，用 `masked_fill(mask == 0, -1e9)` 把被掩位置的分数压成负无穷，softmax 后权重归零；目标端两种 mask 要**按位与**合并。

按 $Q,K,V$ 的来源区分三种注意力，这是最容易混的地方：

| | Q | K | V | mask |
|---|---|---|---|---|
| Encoder self-attention | Encoder 上一层输出 | 同 Q | 同 Q | 仅 padding mask |
| Decoder masked self-attention | Decoder 上一层输出 | 同 Q | 同 Q | padding + look-ahead |
| Decoder cross-attention | Decoder 上一层输出 | Encoder 输出 memory | 同 K | 仅 source padding mask |

一句话：self-attention 是 $Q=K=V$，cross-attention 是 $Q\neq K=V$。cross-attention 是编码器信息流向解码器的唯一通道，取代了 seq2seq 中固定长度的 context vector，因此无需 look-ahead mask——目标端尚未生成的部分与源端无关，源端信息整体可见。

## 2. 方法细节

### 2.1 Scaled Dot-Product Attention 的公式与流程

$$
\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

流程（对应 attention 函数的五步）：

1. 求 $d_k$：`d_k = query.size[-1]`，即每个 head 的特征维度。
2. 打分：`scores = matmul(query, key.transpose(-2,-1)) / sqrt(d_k)`，形状 $[B,h,L,L]$。
3. 掩码：`scores = scores.masked_fill(mask == 0, -1e9)`。
4. 归一化：`p_attn = softmax(scores, dim=-1)`。
5. 加权求和：`matmul(p_attn, value)`，形状回到 $[B,h,L,d_k]$。

符号含义：$Q$ 是当前查询表示（$L_q\times d_k$），$K$ 是被查询的键（$L_k\times d_k$），$V$ 是被聚合的值（$L_k\times d_v$）。

### 2.2 为什么要除以 $\sqrt{d_k}$

softmax 对输入的数量级极其敏感：输入一大，它几乎把全部概率分配给最大值分量，输出近似 one-hot，此时雅可比矩阵接近零矩阵，反向传播梯度消失。

设 $q,k$ 各分量独立、均值 0、方差 1，则点积 $q\cdot k=\sum_{i=1}^{d_k}q_i k_i$ 满足

$$
\mathbb{E}[q\cdot k]=0,\qquad \operatorname{Var}[q\cdot k]=d_k
$$

即维度越大、点积方差越大（标准差 $\sqrt{d_k}$），数量级失控。除以 $\sqrt{d_k}$ 后方差恢复为 1，softmax 输入回到合理区间。注意 $d_k$ 是**每个 head** 的维度（$d_{model}/h$），不是 $d_{model}$。

### 2.3 Multi-Head Attention 的计算方式

设 $h$ 个头、$d_{model}\%h==0$，则 $d_k=d_{model}/h$。

1. 用 3 个独立线性层把 $Q,K,V$ 投影到 $d_{model}$。
2. 切头：$[B,L,d_{model}]\to[B,L,h,d_k]\to[B,h,L,d_k]$（`view` + `transpose(1,2)`），让句长与每头特征维度相邻，更利于捕捉特征。
3. 每个头独立做 Scaled Dot-Product Attention，得 $[B,h,L,d_k]$。
4. 合并：`transpose(1,2).contiguous.view(B,-1,h*d_k)` 回到 $[B,L,d_{model}]$。
5. 过第 4 个线性层 $W^O$ 融合输出。

为什么要多头：单个 head 只有一种相似度度量，多个 head 相当于把表示投影到多个子空间，可同时关注不同方面（如一个头关注句法、一个头关注指代），最后综合。多头并不显著增加计算量，因为总维度固定、每头维度缩小为 $d_{model}/h$。

### 2.4 位置编码

Transformer 丢弃了递归结构，不加位置信息则打乱词序结果不变。编码用三角函数：

$$
PE_{(pos,2i)}=\sin\!\left(\frac{pos}{10000^{2i/d_{model}}}\right),\qquad
PE_{(pos,2i+1)}=\cos\!\left(\frac{pos}{10000^{2i/d_{model}}}\right)
$$

实现上用 `div_term = exp(arange(0, d_model, 2) * -(log(10000.0)/d_model))` 一次算出分母，偶数列赋 sin、奇数列赋 cos。用三角函数的理由：

1. 同一词汇随位置不同，位置嵌入会变化，从而携带位置信息。
2. sin/cos 值域 $[-1,1]$，控制嵌入数值大小，有助于梯度计算。
3. 由和角公式可得 $PE_{pos+k}$ 是 $PE_{pos}$ 的线性函数，模型因此能学到相对位置关系；且周期函数不受序列长度限制。

### 2.5 Embedding 为什么要乘 $\sqrt{d_{model}}$

```python
return self.lut(x) * math.sqrt(self.d_model)
```

词嵌入参数初始化方差很小，而位置编码值域是 $[-1,1]$，两者量纲差距大。若直接相加，位置编码会「盖住」词嵌入携带的语义信息。乘 $\sqrt{d_{model}}$ 放大词嵌入，使二者量级相当，并让分布更接近标准正态，有利于后续层学习。

### 2.6 子层连接结构与 LayerNorm

$$
\text{output}=x+\text{Dropout}\big(\text{Sublayer}(\text{LayerNorm}(x))\big)
$$

这是 Pre-LN 写法：先 LayerNorm，再进子层，再 Dropout，最后与原始 $x$ 残差相加。现代大模型普遍采用 Pre-LN（训练更稳定、对 warmup 依赖更小）；Post-LN 的备选写法是 `x + dropout(norm(sublayer(x)))`。

LayerNorm 在**最后一维**（特征维）上求均值方差，并保留可学习的缩放 $\gamma$ 与平移 $\beta$：

$$
y=\gamma\cdot\frac{x-\mu}{\sigma+\epsilon}+\beta
$$

这里的 `*` 是逐元素相乘，不是矩阵乘法。

### 2.7 完整数据流

```
source ──► Embedding×√d_model ──┐
 ├─► Add ──► Encoder Layer × N ──► memory
source ──► Positional Encoding ─┘
 │
target ──► Embedding + PE ──► Decoder Layer × N ──► Generator(Linear+log_softmax) ──► logits
 ▲ ▲
 target_mask source_mask
```

`EncoderDecoder.forward` 三步：`encode(source, source_mask)` → `decode(memory, source_mask, target, target_mask)` → `generator(...)`。

## 3. 可运行示例

依赖：`pip install torch numpy`。下面是一份最小可跑的 Transformer 核心组件实现，已去掉代码里的调试残留。

### 3.1 Attention 与 Multi-Head Attention

```python
# 依赖: pip install torch numpy
import copy
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

def attention(query, key, value, mask=None, dropout=None):
    """Scaled Dot-Product Attention
    query/key/value: [B, h, L, d_k]；mask 需可广播到 [B, h, L, L]
    返回: 加权结果 [B, h, L, d_k]、注意力权重 [B, h, L, L]
    """
    d_k = query.size(-1)
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k) # 1) 打分并缩放
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9) # 2) 掩码
        p_attn = F.softmax(scores, dim=-1) # 3) 归一化
        if dropout is not None:
            p_attn = dropout(p_attn)
            return torch.matmul(p_attn, value), p_attn # 4) 加权求和

        def clones(module, n):
            """深拷贝 n 份，得到相互独立的层"""
            return nn.ModuleList([copy.deepcopy(module) for _ in range(n)])

        class MultiHeadedAttention(nn.Module):
            def __init__(self, head, embedding_dim, dropout=0.1):
                super.__init__
                assert embedding_dim % head == 0, "特征维度必须能被头数整除"
                self.d_k = embedding_dim // head
                self.head = head
                self.linears = clones(nn.Linear(embedding_dim, embedding_dim), 4) # Q,K,V,O
                self.dropout = nn.Dropout(p=dropout)
                self.attn = None

                def forward(self, query, key, value, mask=None):
                    if mask is not None:
                        mask = mask.unsqueeze(0) # [B,L,L] -> [1,B,L,L]，广播到 head 维
                        batch_size = query.size(0)
                        # 线性投影 + 切头: [B,L,d_model] -> [B,L,h,d_k] -> [B,h,L,d_k]
                        query, key, value = [
                        lin(x).view(batch_size, -1, self.head, self.d_k).transpose(1, 2)
                        for lin, x in zip(self.linears, (query, key, value))
                        ]
                        x, self.attn = attention(query, key, value, mask=mask, dropout=self.dropout)
                        # 合并头: [B,h,L,d_k] -> [B,L,h,d_k] -> [B,L,d_model]
                        x = x.transpose(1, 2).contiguous.view(batch_size, -1, self.head * self.d_k)
                        return self.linears[-1](x) # 输出投影 W^O
```

### 3.2 位置编码、前馈层、LayerNorm、子层连接

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

### 3.3 掩码、Encoder / Decoder 与整体拼装

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

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| `assert embedding_dim % head == 0` 报错 | $d_{model}$ 无法被头数整除 | 调整 $d_{model}$ 或头数，如 $512/8\Rightarrow d_k=64$ |
| `view` 报 "shape invalid for input of size ..." | `transpose` 后内存不连续 | 先 `.contiguous` 再 `.view`，或改用 `.reshape` |
| loss 正常下降，预测却像「抄答案」 | look-ahead mask 漏加或方向反了 | 确认是**下三角为 1**：`1 - triu(ones, diagonal=1)` |
| 样本越长效果越差，attention 分散 | 只加了 look-ahead mask，漏了 padding mask | 两种 mask 按位与：`pad_mask & subsequent_mask` |
| softmax 接近 one-hot、梯度消失、loss 不降 | 忘除以 $\sqrt{d_k}$ | 打分时除以 $\sqrt{d_k}$，注意是每头维度而非 $d_{model}$ |
| 打乱词序输出不变 | 位置编码漏加，或漏乘 $\sqrt{d_{model}}$ 导致位置信息被淹没 | 确认顺序为 `Embedding → ×√d_model → + PE` |
| `model.to(device)` 后报设备不一致 | 用普通属性存 `pe`，未随模型迁移 | 用 `self.register_buffer("pe", pe)` |
| 输出层 softmax 后又接 `CrossEntropyLoss` | 概率再取 log 导致数值下溢 | `log_softmax + NLLLoss` 或 `logits + CrossEntropyLoss`，二选一 |
| 深层模型 loss 震荡、不收敛 | 用了 Post-LN，对 warmup 极敏感 | 改用 Pre-LN：`x + sublayer(norm(x))` |
| 长序列显存爆炸 | self-attention 时间与显存复杂度为 $O(L^2)$ | 减小 batch/长度，或用 FlashAttention、稀疏/线性注意力 |

## 5. 面试问答

**Q1. attention 为什么必须除以 $\sqrt{d_k}$？不除会怎样？**

<details><summary>参考答案</summary>

softmax 的输出分布对输入数量级极其敏感：输入一大，它几乎把全部概率给最大值分量，输出退化成近似 one-hot，此时雅可比矩阵接近零矩阵，反向传播梯度消失，参数更新停滞。

而点积的数量级本身随维度增长。设 $q,k$ 各分量独立同分布、均值 0 方差 1，则

$$\mathbb{E}[q\cdot k]=0,\quad \operatorname{Var}[q\cdot k]=d_k$$

即点积标准差是 $\sqrt{d_k}$，维度越大打分越极端。除以 $\sqrt{d_k}$ 后方差归一化为 1，softmax 输入回到合理区间。

两个易错点：$d_k$ 是**每个 head 的维度**（$d_{model}/h$）而非 $d_{model}$；缩放必须在 softmax **之前**，与 mask 的先后顺序则无所谓（$-1e9$ 除以正数仍是极小值）。

</details>

**Q2. Multi-Head Attention 相比单头注意力，本质收益是什么？头数越多越好吗？**

<details><summary>参考答案</summary>

本质收益是**表示子空间的多样性**。单个 head 只有一种相似度度量，只能学到一种对齐模式；$h$ 个 head 把 $d_{model}$ 投影到 $h$ 个 $d_k$ 维子空间并行计算，让模型同时从多个角度观察序列。经验研究显示不同 head 确实会分工（关注相邻词、句法依赖、指代关系等），最后 concat 并过 $W^O$ 融合。

多头并不显著增加计算量：总维度固定、每头维度缩为 $d_{model}/h$，$QK^\top$ 的总计算量基本持平。

但不是越多越好：① 必须 $d_{model}\%h==0$；② 头太多则 $d_k$ 过小，单头表征能力不足，收益递减甚至变差，经验上 $d_k$ 不低于 32–64；③ 切分/拼接与输出投影有额外开销。因此 base 取 $h=8,d_k=64$ 是平衡点。

</details>

**Q3. Decoder 在训练和预测阶段的输入有什么区别？为什么训练能并行而预测不能？**

<details><summary>参考答案</summary>

**训练阶段**把完整目标序列右移一位（teacher forcing）一次性送入最底层 Decoder Block。所谓「右移一位」是指每个 time step 的输入是「上一个 time step 的输入 + 真实标签序列向后移一位」，因此输入序列随 time step 越来越长。真实实现里不真的逐步拼接，而是**一次送入完整序列 + look-ahead mask 模拟「只能看到当前及之前位置」**，于是一次矩阵运算等价于所有 time step，实现并行。

**预测阶段**没有 ground truth，从 `time step=0` 开始，每步把之前所有 time step 的**预测值**累积拼接作为输入，逐步自回归生成。第 $t$ 步依赖第 $t-1$ 步输出，天然串行。

核心差异是「不断拼进来的是 ground truth 还是预测值」，由此带来 **exposure bias**：训练时只看过正确前缀，推理时一旦前面出错，误差会逐步累积放大。

</details>

## 6. 自测题

**1. 写出 Scaled Dot-Product Attention 公式；当 $Q,K,V$ 形状为 $[2,8,4,64]$ 时，输出与注意力权重各是什么形状？**

<details><summary>参考答案</summary>

$$\text{Attention}(Q,K,V)=\text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

对 $[B,h,L,d_k]=[2,8,4,64]$：

- `key.transpose(-2,-1)` → $[2,8,64,4]$
- `matmul(query, key^T)` → $[2,8,4,4]$（每个样本每个 head 一个 $4\times4$ 相似度矩阵）
- softmax 后 $p_{attn}$ → $[2,8,4,4]$
- `matmul(p_attn, value)`：$[2,8,4,4]\times[2,8,4,64]$ → $[2,8,4,64]$

所以输出形状 $[2,8,4,64]$，注意力权重 $[2,8,4,4]$。Multi-Head 拼接后输出变回 $[2,4,512]$（$8\times64=512$）。

</details>

**2. `subsequent_mask(4)` 输出什么矩阵？它和 padding mask 如何组合？**

<details><summary>参考答案</summary>

```
[[1, 0, 0, 0],
 [1, 1, 0, 0],
 [1, 1, 1, 0],
 [1, 1, 1, 1]]
```

即下三角矩阵：位置 $i$ 只能看到 $j\le i$，实现方式 `1 - triu(ones, diagonal=1)`。

与 padding mask 的组合是**按位与**：设 `pad_mask` 形状 $[B,1,L]$（真实 token 为 1、PAD 为 0），则

```python
tgt_mask = pad_mask & subsequent_mask(L) # 广播后 [B, L, L]
```

语义是「既排除 PAD 位置，又排除未来位置」。缺任一都会出问题：漏 padding mask 会让 PAD 参与加权稀释真实信息；漏 look-ahead mask 会让模型训练时看到答案，推理时性能崩塌。

</details>

**3. 位置编码为什么用 sin/cos，而不是直接用位置序号 0,1,2,...？**

<details><summary>参考答案</summary>

直接用序号有三个问题：

1. **数值范围不受控**：序号可无限大，与归一化的词嵌入量纲悬殊，梯度易出问题；sin/cos 值域固定在 $[-1,1]$。
2. **无法外推**：序号编码在 `max_len` 之外没有定义；三角函数是周期函数，不受序列长度限制。
3. **无法表达相对位置**：由和角公式可推出 $PE_{pos+k}$ 是 $PE_{pos}$ 的线性函数，模型因此能学到「相对距离」概念。

另外，不同频率（$i$ 从 0 到 $d_{model}/2$）的 sin/cos 组合相当于给每个位置一个多分辨率「指纹」，使模型能同时区分近距与远距位置。

</details>

**4. Transformer 相比 RNN 的两大优势是什么？为什么说 self-attention 层本身并非「完全并行」？**

<details><summary>参考答案</summary>

两大优势：① **并行计算**——RNN 必须按时间步串行递归，Transformer 的 Encoder 端所有位置同时计算；② **特征提取能力强**——self-attention 中任意两位置之间路径长度为 $O(1)$，可直接建模长距离依赖，不像 RNN 需逐步传递而产生损耗。

为什么不是「完全并行」：从结构看，每个 token 的注意力输出依赖**所有** token 的 $K,V$，token 之间存在计算依赖，不是各自独立。看起来并行是因为实现上用矩阵乘法一次性算完所有 $QK^\top$——这是**算子实现层面**的并行。同理 Decoder 的两种 attention 训练时可借矩阵运算一次算完，但预测时必须逐 time step 串行。

</details>

## 7. 延伸阅读

- 原始论文《Attention Is All You Need》(Vaswani et al., 2017)：https://arxiv.org/abs/1706.03762
- The Annotated Transformer（Harvard NLP，逐行讲解本文代码）：https://nlp.seas.harvard.edu/annotated-transformer/
- The Illustrated Transformer（图解 Q/K/V、多头、位置编码）：https://jalammar.github.io/illustrated-transformer/
- PyTorch 官方 `nn.MultiheadAttention` 文档：https://pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html
- PyTorch 官方 Transformer （`nn.Transformer` 完整示例）：https://pytorch.org/tutorials/beginner/transformer_tutorial.html
- Pre-LN 与 Post-LN 稳定性对比《On Layer Normalization in the Transformer Architecture》：https://arxiv.org/abs/2002.04745

---

[⬅️ 返回 NLP 目录](README.md)
