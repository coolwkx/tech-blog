---
article_id: kp-04600890e6f5eca3
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 6
learning_objective: 理解并验证：训练：只在 MASK 位置算损失
---

# 训练：只在 MASK 位置算损失

> **学习目标**：能够解释「训练：只在 MASK 位置算损失」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · PET 详解：把分类任务改写成完形填空

## 本次只学这一点

PET 训练时的损失计算不是普通的 `CrossEntropyLoss(logits, labels)`，而是「先按 mask 位置把 logits 抠出来、再和标签词的 token id 对齐」。以下逻辑照搬自完整的 PET 工程实现：

```python
def mlm_loss(logits, mask_positions, sub_mask_labels, criterion, device):
    """只在 MASK 位置计算交叉熵，并对同一类别的多个子标签取平均。

    logits:          (batch, seq_len, vocab_size)
    mask_positions:  (batch, mask_label_num)
    sub_mask_labels: 变长 list，形如 [ [[2398,3352]], [[2398,3352],[3819,3861]] ]
                     —— 外层是 batch，中层是该类别的子标签，内层是 token id
    """
    batch_size, seq_len, vocab_size = logits.size()
    loss = None
    for single_logits, single_sub, single_pos in zip(logits, sub_mask_labels, mask_positions):
        mask_logits = single_logits[single_pos]                    # (mask_num, vocab)
        mask_logits = mask_logits.repeat(len(single_sub), 1, 1)    # (sub_num, mask_num, vocab)
        mask_logits = mask_logits.reshape(-1, vocab_size)          # (sub_num*mask_num, vocab)

        targets = torch.LongTensor(single_sub).to(device).reshape(-1)
        cur = criterion(mask_logits, targets) / len(targets)       # ① 按 token 数归一
        loss = cur if loss is None else loss + cur
    return loss / batch_size                                       # ② 按 batch 归一
```

三个值得记的细节：

1. **`repeat` 是「标签平滑」的替代品**：同一类别有 `k` 个子标签时，MASK 位置的同一份 logits 会被复制 `k` 份，分别对 `k` 个子标签算交叉熵。等价于告诉模型「填苹果、香蕉、橘子都算对」。
2. **不能直接在 `logits` 上做常规 CE**。因为标签不是「每个位置一个类别 id」，而是「只有 mask 位置有答案」，非 mask 位置的标签是无效的，必须显式抠出来。
3. **归一化方式影响梯度尺度**。这里先除以 token 数、再除以 batch 数，如果你换成「先 sum 再平均」，小样本下学习率要同步下调，否则会震荡。

推理阶段则用 `argmax` 解码：

```python
def convert_logits_to_ids(logits, mask_positions):
    """把 (batch, seq, vocab) 在 mask 位置上的 argmax 取出来，形状 (batch, mask_num)。"""
    label_length = mask_positions.size()[1]
    batch_size, seq_len, _ = logits.size()
    flat_index = [b * seq_len + p
                  for b, pos in enumerate(mask_positions.cpu().numpy().tolist())
                  for p in pos]
    tokens = logits.reshape(batch_size * seq_len, -1)[flat_index].argmax(dim=-1)
    return tokens.reshape(-1, label_length)
```

注意 `mask_positions` 里可能包含 padding 产生的额外 `[MASK]`（当标签词只有 1 个 token 而 `max_label_len=2` 时），解码后要先把 `[PAD]` 与补位 `[MASK]` 去掉，再拼成字符串去做字典查询。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「训练：只在 MASK 位置算损失」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
