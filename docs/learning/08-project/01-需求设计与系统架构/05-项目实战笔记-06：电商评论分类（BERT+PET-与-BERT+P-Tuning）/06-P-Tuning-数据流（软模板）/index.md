---
article_id: kp-fbbb15ba692e6b86
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 5
learning_objective: 理解并验证：P-Tuning 数据流（软模板）
---

# P-Tuning 数据流（软模板）

> **学习目标**：能够解释「P-Tuning 数据流（软模板）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 技术架构

## 本次只学这一点

软模板和硬模板的差别全在"序列是怎么拼出来的"这一步，这张图把它拆成九步：

```mermaid
flowchart TD
    IN["convert_example(p_embedding_num=6, max_label_len=2, max_seq_len=512)"]
    IN --> S1["① tokenizer(content) → input_ids（含 [CLS] … [SEP]）"]
    S1 --> S2["② 生成 2 个 [MASK]"]
    S2 --> S3["③ 生成 6 个伪 token：[unused1] … [unused6] 对应的 id"]
    S3 --> S4["④ 裁剪正文：max_seq_len 减去 mask、伪 token 与 [SEP] 的位置"]
    S4 --> S5["⑤ 在 [CLS] 之后（position=1）插入 [MASK][MASK]"]
    S5 --> S6["⑥ 6 个伪 token 拼到最前面"]
    S6 --> LAYOUT["最终序列布局（位置 0 → 511）<br/>[u1][u2][u3][u4][u5][u6] [CLS] [MASK][MASK] 正文 … [SEP][PAD]<br/>前 6 位是伪 token（软模板），第 7、8 位是预测目标"]
    LAYOUT --> S7["⑦ mask_positions = [len(p_tokens) + 1 + i for i in range(2)] = [7, 8]"]
    S7 --> S8["⑧ attention_mask 必须重算：np.where(input_ids > 0, 1, 0)"]
    S8 --> S9["⑨ mask_labels = tokenizer(label)['input_ids'][1:-1]，截断 / pad 到 2"]
    S9 --> OUT["输出：input_ids、attention_mask、mask_positions、mask_labels"]
```

**读图要点**：

| 观察 | 含义 |
| --- | --- |
| 伪 token 拼在最前面，`[MASK]` 插在 `[CLS]` 之后 | 位置一旦被手工改动，所有依赖位置的量都要跟着重推 |
| `④` 裁剪正文时就预留了伪 token 的位置 | 先算预算再插入，避免插完才发现超过 `max_seq_len` 把 `[SEP]` 挤掉 |
| `⑦` 的位置是**手算**的（伪 token 个数 + 1） | 与 PET 的 `np.where` 反查相反，这是本流程最脆弱的一处：伪 token 数一变就必须同步改公式 |
| `⑧` 必须重算 `attention_mask` | tokenizer 不知道自己前面被塞了 token，沿用旧 mask 会把伪 token 当 padding 忽略，软模板静默失效 |
| 出口与 PET 略有不同 | PET 多传 `token_type_ids`，P-Tuning 只关心 `input_ids` 与 mask，其余交给模型默认值 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「P-Tuning 数据流（软模板）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
