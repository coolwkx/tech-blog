---
article_id: kp-84462d7bf52fd608
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 10
learning_objective: 理解并验证：PET 的 MLM 损失：变长子标签的处理
---

# PET 的 MLM 损失：变长子标签的处理

> **学习目标**：能够解释「PET 的 MLM 损失：变长子标签的处理」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

全项目最绕的一段，逐行拆解：

```python
def mlm_loss(logits, mask_positions, sub_mask_labels, cross_entropy_criterion, device):
    """
    logits: (batch, seq_len, vocab_size) = (8, 256, 21128)
    mask_positions: (batch, mask_label_num) = (8, 2)
    sub_mask_labels: 变长 list，e.g. [[[2398,3352]], [[2398,3352], [3819,3861]]]
    """
    batch_size, seq_len, vocab_size = logits.size
    loss = None

    for single_logits, single_sub_mask_labels, single_mask_positions in \
    zip(logits, sub_mask_labels, mask_positions):

        # ① 取出 mask 位置的 logits：(mask_label_num, vocab_size)
        single_mask_logits = single_logits[single_mask_positions]
        # ② 复制 sub_label_num 份：(sub_label_num, mask_label_num, vocab_size)
        single_mask_logits = single_mask_logits.repeat(len(single_sub_mask_labels), 1, 1)
        # ③ 拉平：(sub_label_num * mask_label_num, vocab_size)
        single_mask_logits = single_mask_logits.reshape(-1, vocab_size)

        # ④ 标签同样拉平
        single_sub_mask_labels = torch.LongTensor(single_sub_mask_labels).to(device)
        single_sub_mask_labels = single_sub_mask_labels.reshape(-1, 1).squeeze

        # ⑤ 交叉熵，按 token 数归一化（消除子标签个数差异带来的量纲差）
        cur_loss = cross_entropy_criterion(single_mask_logits, single_sub_mask_labels)
        cur_loss = cur_loss / len(single_sub_mask_labels)

        loss = cur_loss if loss is None else loss + cur_loss

        return loss / batch_size
```

**核心思想**：一个主标签可能对应多个子标签（"水果" → 苹果/香蕉/橘子）。模型的 2 个 `[MASK]` 位置应该**同时倾向于所有这些子标签**，而不是只倾向某一个。实现手法是把 mask 位置的 logits **复制 N 份**（N = 子标签个数），与所有子标签 token 一起算交叉熵——**只要预测的是任一合法子标签，loss 都低**。

**`cur_loss / len(single_sub_mask_labels)` 这一步容易漏**：不归一化的话，子标签多的类别（"水果"有 3 个）算出的 loss 天然是子标签少的类别的 3 倍，相当于给类别加了隐式权重。除以 token 数把量纲拉平，batch 平均才有意义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PET 的 MLM 损失：变长子标签的处理」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
