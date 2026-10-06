---
article_id: kp-b3d017781f5e9236
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 10
learning_objective: 理解并验证：为什么直接训 embedding 不够：prompt encoder 的作用
---

# 为什么直接训 embedding 不够：prompt encoder 的作用

> **学习目标**：能够解释「为什么直接训 embedding 不够：prompt encoder 的作用」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · P-Tuning 详解：可学习软模板

## 本次只学这一点

P-Tuning 论文指出，直接把伪 token 的 embedding 当成参数、用梯度去更新，会碰到两个麻烦：

1. **Discreteness（不连续性）**：正常文本的 embedding 是预训练学出来的，分布很规整；而随机初始化的伪 token embedding 在优化初期是完全孤立的点，梯度很难把它推到一个「语言模型认得的」位置，容易陷局部最优。
2. **Association（关联性缺失）**：多个伪 token 之间应该相互关联（它们共同构成一个短语），但独立更新每个 embedding 无法建模这种关系。

P-Tuning 的解法是加一个 **prompt encoder**：把伪 token embedding 序列先送进一个「MLP + LSTM」的小网络，用它的输出作为真正的 prompt 向量。

```python
# -*- coding: utf-8 -*-
"""P-Tuning 的可学习软模板 + prompt encoder（MLP+LSTM）。依赖：torch, transformers"""
import torch
import torch.nn as nn


class PromptEncoder(nn.Module):
    """把伪 token 的 embedding 序列变换成真正喂给模型的 prompt 向量。

    论文中是 MLP + LSTM：先逐位置做非线性变换，再用 LSTM 建模伪 token
    之间的相互依赖。训练完成后只需保留编码后的向量，编码器本身可以丢弃。
    """

    def __init__(self, hidden_size: int, prompt_len: int, mid_size: int = None):
        super().__init__()
        mid_size = mid_size or hidden_size
        self.prompt_len = prompt_len
        self.mlp = nn.Sequential(nn.Linear(hidden_size, mid_size), nn.ReLU(),
                                 nn.Linear(mid_size, hidden_size))
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers=2,
                            batch_first=True, bidirectional=True)
        self.proj = nn.Linear(hidden_size * 2, hidden_size)

    def forward(self, prompt_embeds: torch.Tensor) -> torch.Tensor:
        """Args: (batch, prompt_len, hidden) -> Returns: (batch, prompt_len, hidden)"""
        h, _ = self.lstm(self.mlp(prompt_embeds))
        return self.proj(h)


class SoftPrompt(nn.Module):
    """软模板：用词表预留的 [unused*] 位做伪 token。布局：[p1]..[pn] [CLS] [MASK]*k 正文 [SEP]"""

    def __init__(self, model_name: str, prompt_len: int = 6, mask_len: int = 2):
        super().__init__()
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.encoder = AutoModelForMaskedLM.from_pretrained(model_name)
        self.prompt_len, self.mask_len = prompt_len, mask_len
        hidden = self.encoder.config.hidden_size

        # 借用词表中的 [unused*] 作为伪 token 占位
        self.prompt_ids = [self.tokenizer.convert_tokens_to_ids(f"[unused{i + 1}]")
                           for i in range(prompt_len)]
        if any(i is None or i == self.tokenizer.unk_token_id for i in self.prompt_ids):
            raise ValueError("词表中缺少足够的 [unused*] token，无法构造软模板。")

        self.prompt_embeddings = nn.Parameter(
            self.encoder.get_input_embeddings().weight[self.prompt_ids].clone().detach())
        self.prompt_encoder = PromptEncoder(hidden, prompt_len)
        for p in self.encoder.parameters():          # 冻结主干
            p.requires_grad = False

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor,
                mask_positions: torch.Tensor):
        """手动拼 embedding：伪 token 走 encoder，正文走冻结的词嵌入表。"""
        emb_layer = self.encoder.get_input_embeddings()
        prompt_embeds = self.prompt_encoder(self.prompt_embeddings.unsqueeze(0))
        inputs_embeds = torch.cat(
            [prompt_embeds.expand(input_ids.size(0), -1, -1), emb_layer(input_ids)], dim=1)
        prefix = torch.ones(input_ids.size(0), self.prompt_len,
                            dtype=attention_mask.dtype, device=attention_mask.device)
        logits = self.encoder(inputs_embeds=inputs_embeds,
                              attention_mask=torch.cat([prefix, attention_mask], dim=1)).logits
        return logits, mask_positions + self.prompt_len     # 位置整体右移，别忘了
```

> **依赖说明**：`torch` + `transformers` + 本地 `bert-base-chinese`。本机无 GPU、未安装 `transformers`，以上代码仅做静态逻辑核对，**未实测运行**。

几点工程注解：

- **伪 token 用什么 id 无所谓，但必须保证它在词表里只有一个 token**。中文 BERT 的 `[unused1]` 是单 token，而你自己乱写的 `[p1]` 会被切成 `[`、`p`、`1`、`]` 四个 token，伪 token 个数就失控了。
- **P-Tuning 与 Prompt Tuning、Prefix-Tuning 的区别**（常考）：

| 方法 | 加在哪 | 是否用独立 encoder | 初始化 |
|---|---|---|---|
| Prompt Tuning | 只在输入层最前面，像一段 Instruction 前缀 | 否 | 直接随机/词向量 |
| P-Tuning v1 | 输入层，位置可前可后、不固定 | **是（MLP+LSTM）** | 随机或真实词 embedding |
| Prefix-Tuning | **每一层**都加前缀（KV 侧） | 是（MLP） | 随机，训练不稳定 |
| **P-Tuning v2** | **每一层**都加连续 prompt | 否（直接是每层的参数） | 随机 |

- **P-Tuning v2** 出自《P-Tuning v2: Prompt Tuning Can Be Comparable to Fine-tuning Universally Across Scales and Tasks》，核心改动是把连续 prompt 从「只在输入层」下沉到**每一层 Transformer**，同时去掉重参数化 encoder、改为直接优化每层的 prompt 参数。这样做的收益是：在小参数量模型（如 BERT-base）上，v1 明显弱于全参微调，而 v2 能追平甚至超过；代价是可训练参数变多（仍是全参的很小比例）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「为什么直接训 embedding 不够：prompt encoder 的作用」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
