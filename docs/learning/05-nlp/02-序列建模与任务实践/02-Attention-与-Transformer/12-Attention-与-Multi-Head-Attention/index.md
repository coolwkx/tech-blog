---
article_id: kp-2fb2e1967c346443
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cbc77f3ab05c
learning_sourceId: cbc77f3ab05c
learning_order: 11
learning_objective: 理解并验证：Attention 与 Multi-Head Attention
---

# Attention 与 Multi-Head Attention

> **学习目标**：能够解释「Attention 与 Multi-Head Attention」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 07 篇 RNN / LSTM / seq2seq、PyTorch 的 `nn.Linear` 与张量 `view/transpose/matmul`、softmax 与交叉熵。
>
> **所属主题**：Attention 与 Transformer · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Attention 与 Multi-Head Attention」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/08-Attention与Transformer.md)
