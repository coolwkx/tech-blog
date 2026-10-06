---
article_id: kp-fbcb9b6654e20b11
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 2
learning_objective: 理解并验证：数据流
---

# 数据流

> **学习目标**：能够解释「数据流」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 技术架构

## 本次只学这一点

这张图回答的是"一份纯文本语料怎么变成能训练的批次，训完又怎么被拿去生成"：

```mermaid
flowchart TD
    RAW["data/legal_qa_train.txt<br/>纯文本，空行分段，段内换行分句"] --> PRE["preprocess.py<br/>① 二进制读取 → utf-8 解码<br/>② 按空行切成对话段（同时兼容 CRLF 与 LF 两种换行符）<br/>③ 段内按换行切成 utterance<br/>④ 每段拼成 [CLS] utt1 [SEP] utt2 [SEP] … [SEP]"]
    PRE --> PKL["data/legal_qa_train.pkl（list[list[int]]，序列化的 token id）"]
    PKL --> DS["dataset.py：MyDataset(input_list, max_len=300)<br/>单条样本截断到 300 以内 → torch.LongTensor"]
    DS --> COLL["dataloader.py：collate_fn<br/>input_ids = pad_sequence(batch, padding_value=0)<br/>labels = pad_sequence(batch, padding_value=-100)"]
    COLL --> TRAIN["train.py：train_epoch<br/>model(input_ids, labels=labels) → logits 与 loss<br/>梯度累积 4 步 → clip_grad_norm_(4.0) → optimizer.step → scheduler.step"]
    TRAIN --> SAVE["save_model/bj_epoch{n}/（每 10 个 epoch 存一次）<br/>save_model/min_ppl_model_bj/（验证 loss 创新低时存）"]
    SAVE --> INF["interact.py / flask_predict.py<br/>拼 [CLS] + history[-3:] + [SEP] … → 逐 token 自回归生成<br/>重复惩罚 + top-k(4) 过滤 + 屏蔽 [UNK]"]
    INF --> OUT["控制台对话 / Flask Web 页面 / sample/samples.txt 聊天记录"]
```

**读图要点**：

| 观察 | 含义 |
| --- | --- |
| 管线是"文本 → pkl → 张量 → batch"四段 | 每个环节有明确的输入输出格式，出问题时能立刻定位到是哪一段的形状不对 |
| tokenize 结果被缓存成 pkl | 分词只做一次，训练时不再重复；代价是换词表必须重新生成 pkl |
| 输入 pad 用 0、标签 pad 用 -100 | 前者要喂给模型，后者要被 loss 忽略，同一个张量不能身兼两职 |
| 训练与推理在 `SAVE` 处分叉 | 保存的 checkpoint 被 `interact.py` 和 `flask_predict.py` 共用，生成逻辑只有一份 |
| 推理侧的拼接与训练侧完全同构 | `[CLS] + history[-3:] + [SEP]` 就是训练时见过的序列形状，这也是"训练与推理口径必须一致"的体现 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据流」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
