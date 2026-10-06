---
article_id: kp-8fb0a9c768bc5c38
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 11
learning_objective: 理解并验证：P-Tuning 项目里的数据处理差异
---

# P-Tuning 项目里的数据处理差异

> **学习目标**：能够解释「P-Tuning 项目里的数据处理差异」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · P-Tuning 详解：可学习软模板

## 本次只学这一点

和 PET 工程对比，P-Tuning 的数据处理有两个关键不同：

**① 不再需要 `prompt.txt`。** 模板由「伪 token 个数 `p_embedding_num`」这个超参决定，而不是一段文字。

**② `attention_mask` 必须重算。** 因为输入序列是手工拼出来的，`[unused*]` 这些 token 在词表里 id 很小（不是 0），分词器自带的 attention mask 可能把它们当成 padding 抹掉，于是 prompt 就"消失了"。因此需要显式重算：

```python
def get_attention_mask(input_ids):
    """根据 id 是否为 padding(0) 重算 attention mask。"""
    import numpy as np
    return np.where(np.array(input_ids) > 0, 1, 0).tolist()
```

输入拼接顺序（本文工程的做法）：

```
input_ids = p_tokens_ids + [CLS] + mask_ids + 正文 + [SEP]
```

`mask_positions` 相应地要整体右移 `p_embedding_num` 位。这也是一个经典 bug：伪 token 插进去了但 mask 位置没加偏移，训练能跑但 loss 完全不降。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「P-Tuning 项目里的数据处理差异」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
