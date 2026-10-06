---
article_id: kp-a6d7c8625f21b4f5
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 6
learning_objective: 理解并验证：Dataset 与变长 batch 填充
---

# Dataset 与变长 batch 填充

> **学习目标**：能够解释「Dataset 与变长 batch 填充」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```python
# dataset.py
class MyDataset(Dataset):
    def __init__(self, input_list, max_len):
        self.input_list = input_list
        self.max_len = max_len

        def __len__(self):
            return len(self.input_list)

        def __getitem__(self, index):
            return torch.tensor(self.input_list[index][:self.max_len], dtype=torch.long)

        # dataloader.py
        def collate_fn(batch):
            # 输入填充 0（PAD id）
            input_ids = rnn_utils.pad_sequence(batch, batch_first=True, padding_value=0)
            # 标签填充 -100，让 CrossEntropyLoss 的 ignore_index 自动跳过
            labels = rnn_utils.pad_sequence(batch, batch_first=True, padding_value=-100)
            return input_ids, labels
```

**为什么输入和标签用不同的 padding 值**：`input_ids` 里的 pad 是要喂给模型做 attention mask 的（用 `padding_value=0` 即 `[PAD]` id）；`labels` 里的 pad 是要被 loss 忽略的（用 `-100`）。同一个张量不能身兼两职，所以 `collate_fn` 从同一批数据里生成两份。

> 注意：`GPT2LMHeadModel` 对 `padding_value=0` 的 pad token 默认不会屏蔽注意力（不像 Encoder-Decoder 会传 `attention_mask`）。严格来说应该同时传 `attention_mask`，本项目为简化未传，长序列+大量 pad 时会略微影响效果。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Dataset 与变长 batch 填充」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
