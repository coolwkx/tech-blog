---
article_id: kp-3d47453105709453
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 5
learning_objective: 理解并验证：数据处理：把对话压成一条 token 序列
---

# 数据处理：把对话压成一条 token 序列

> **学习目标**：能够解释「数据处理：把对话压成一条 token 序列」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 核心实现

## 本次只学这一点

```python
# data_preprocess/preprocess.py（精简）
tokenizer = BertTokenizerFast('vocab/vocab.txt', sep_token="[SEP]",
pad_token="[PAD]", cls_token="[CLS]")
sep_id, cls_id = tokenizer.sep_token_id, tokenizer.cls_token_id

with open(train_txt_path, 'rb') as f:
    data = f.read.decode("utf-8")

    # 关键：区分 Windows / Linux 换行符，否则整个语料会被切成 1 段
    train_data = data.split("\r\n\r\n") if "\r\n" in data else data.split("\n\n")

    dialogue_list = []
    for dialogue in tqdm(train_data):
        sequences = dialogue.split("\r\n") if "\r\n" in dialogue else dialogue.split("\n")
        input_ids = [cls_id] # 每段以 [CLS] 开头
        for sequence in sequences:
            input_ids += tokenizer.encode(sequence, add_special_tokens=False)
            input_ids.append(sep_id) # 每句后加 [SEP]
            dialogue_list.append(input_ids)

            with open(train_pkl_path, "wb") as f:
                pickle.dump(dialogue_list, f)
```

产出的单条序列形如：

```text
[CLS] 租房 押金 不退 怎么办 ？ [SEP] 协商 退还 ； 向 住建 部门 投诉 ； 留存 转账 凭证 [SEP]
```

**设计要点**：`add_special_tokens=False` 必须开。否则 `BertTokenizerFast.encode` 会往每句首尾塞 `[CLS]/[SEP]`，和手写的拼接逻辑冲突，序列里会满是噪声。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据处理：把对话压成一条 token 序列」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
