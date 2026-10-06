---
article_id: kp-c359df2df5ebc9cf
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 8
learning_objective: 理解并验证：准确率统计：对齐 shift 与忽略 pad
---

# 准确率统计：对齐 shift 与忽略 pad

> **学习目标**：能够解释「准确率统计：对齐 shift 与忽略 pad」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```python
# functions_tools.py
def calculate_acc(logit, labels, ignore_index=-100):
 # 与语言模型一致：用前 n-1 个位置预测后 n-1 个位置
 logit = logit[:, :-1, :].contiguous.view(-1, logit.size(-1))
 labels = labels[:, 1:].contiguous.view(-1)

 _, logit = logit.max(dim=-1) # 取 argmax

 non_pad_mask = labels.ne(ignore_index) # pad 位置为 False
 n_correct = logit.eq(labels).masked_select(non_pad_mask).sum.item
 n_word = non_pad_mask.sum.item
 return n_correct, n_word
```

这个函数浓缩了三个必须做对的细节：**shift（`[:-1]` 对 `[1:]`）、flatten（`view(-1)`）、mask（`ne(-100)`）**。少任何一个，算出来的 acc 都是错的（通常是虚高）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「准确率统计：对齐 shift 与忽略 pad」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
