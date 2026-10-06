---
article_id: kp-546de528ef0ad4c3
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 11
learning_objective: 理解并验证：从 logits 取出预测：索引展平
---

# 从 logits 取出预测：索引展平

> **学习目标**：能够解释「从 logits 取出预测：索引展平」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```python
def convert_logits_to_ids(logits, mask_positions):
    """logits: (8, 512, 21128); mask_positions: (8, 2) -> 返回 (8, 2)"""
    label_length = mask_positions.size[1]
    batch_size, seq_len, vocab_size = logits.size

    # 把二维坐标 (batch, pos) 展平成一维索引 batch * seq_len + pos
    mask_positions_after_reshaped = []
    for batch, mask_pos in enumerate(mask_positions.detach.cpu.numpy.tolist()):
        for pos in mask_pos:
            mask_positions_after_reshaped.append(batch * seq_len + pos)

            logits = logits.reshape(batch_size * seq_len, -1) # 二维化
            mask_logits = logits[mask_positions_after_reshaped] # 取出 mask 位置
            predict_tokens = mask_logits.argmax(dim=-1)
            return predict_tokens.reshape(-1, label_length)
```

**为什么要手算 `batch * seq_len + pos`**：`logits[batch_idx, pos]` 这种高级索引对多维张量（尤其 pos 变长时）支持有限。展平成一维后用 Python 列表索引最稳妥、最不会出错。

代价是经过 `.cpu.numpy.tolist()`，意味着一次 GPU→CPU 同步拷贝。追求性能时应用 `torch.gather` 或 `logits.gather(1, mask_positions.unsqueeze(-1).expand(...))` 全程留在 GPU。对 63 条样本的项目，损耗可忽略。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从 logits 取出预测：索引展平」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
