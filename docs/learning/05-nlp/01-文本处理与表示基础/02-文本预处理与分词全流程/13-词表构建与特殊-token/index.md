---
article_id: kp-5aed156079303386
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 12
learning_objective: 理解并验证：词表构建与特殊 token
---

# 词表构建与特殊 token

> **学习目标**：能够解释「词表构建与特殊 token」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 深入机制

## 本次只学这一点

| Token | 作用 | 备注 |
| --- | --- | --- |
| `[UNK]` | 词表外兜底 | byte-level / `byte_fallback` 之后基本用不到 |
| `[CLS]` | BERT 句首；其输出向量做句表示 | 只有 BERT 系（encoder-only）用 |
| `[SEP]` | 句子 / 片段分隔，句对任务的关键 | 句对输入为 `[CLS] A [SEP] B [SEP]` |
| `[PAD]` | 补齐到定长 | **必须让 `attention_mask` 屏蔽**，否则 attention 会算进无意义位置 |
| `[MASK]` | MLM 掩码占位 | 训练专用；推理阶段不应出现 |
| BOS / EOS | 生成起点 / 终点 | decoder-only 通常只用 BOS，或干脆不加 |

不同模型的约定差异（写代码时别硬编码）：

| 模型 | 句首 / 句尾 | 特殊 token 长相 |
| --- | --- | --- |
| BERT | `[CLS]` … `[SEP]` | `[CLS]` / `[SEP]` / `[PAD]` / `[MASK]` / `[UNK]` |
| RoBERTa | `<s>` … `</s>` | 没有 `[CLS]`，用 `<s>` 的向量做句表示 |
| GPT-2 | 无 BOS/EOS | 没有 `[PAD]`，需手动 `tokenizer.pad_token = tokenizer.eos_token` |
| T5 | 无 BOS，`</s>` 结尾 | 用 `<extra_id_0>` 做 span 掩码 |
| Llama-3 | `<\|begin_of_text\|>` | 对话模板里还有 `<\|start_header_id\|>` 等 |
| Qwen | `<\|im_start\|>` / `<\|im_end\|>` | Chat 模板必须走 `apply_chat_template` |

**词表构建流程**：领域语料（尽量贴近线上分布）→ 归一化（与推理一致）→ 训练 tokenizer（`vocab_size` / `min_frequency` / `special_tokens`）→ 评估（平均 token/词、OOV 率、长尾覆盖率）→ 保存（`tokenizer.json` / `vocab.txt` / `merges.txt` / `sentencepiece.model`）→ 与 checkpoint 一起版本化。

要点：**`vocab_size` 是取舍**，小词表导致序列长、注意力开销大，大词表导致 embedding 参数多、长尾 token 训练不足，30k ~ 128k 是当前常见区间；**特殊 token 的 id 必须固定**且不会被切碎（`tokenizers` 里用 `AddedToken` 注册并在训练前占位）；**改词表要同步改模型**，加了 token 必须 `model.resize_token_embeddings(len(tokenizer))`，且新 token 的 embedding 需要继续训练才有效。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「词表构建与特殊 token」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
