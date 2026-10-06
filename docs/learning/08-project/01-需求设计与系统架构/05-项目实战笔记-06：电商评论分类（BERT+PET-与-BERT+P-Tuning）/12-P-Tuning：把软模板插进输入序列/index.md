---
article_id: kp-7c25dd0935dc89e8
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-314d719df758
learning_sourceId: 314d719df758
learning_order: 12
learning_objective: 理解并验证：P-Tuning：把软模板插进输入序列
---

# P-Tuning：把软模板插进输入序列

> **学习目标**：能够解释「P-Tuning：把软模板插进输入序列」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM（掩码语言模型）预训练目标、`[MASK]` token 的语义、`AutoModelForMaskedLM` 与 `AutoTokenizer`、HuggingFace `datasets.map(batched=True)`、PyTorch 训练循环与 `CrossEntropyLoss`。
>
> **所属主题**：项目实战笔记 06：电商评论分类（BERT+PET 与 BERT+P-Tuning） · 核心实现

## 本次只学这一点

```python
def convert_example(examples, tokenizer, max_seq_len, max_label_len,
p_embedding_num=6, train_mode=True):
    tokenized_output = {'input_ids': [], 'attention_mask': [],
    'mask_positions': [], 'mask_labels': []}

    for example in examples['text']:
        start_mask_position = 1 # 将 prompt token(s) 插在 [CLS] 之后

        label, content = example.strip.split('\t', 1) # ★ 限制只切一刀
        encoded_inputs = tokenizer(text=content, truncation=True,
        max_length=max_seq_len, padding='max_length')
        input_ids = encoded_inputs['input_ids']

        # ① 生成 MASK tokens（个数 = 标签长度）
        mask_ids = tokenizer.convert_tokens_to_ids(['[MASK]'] * max_label_len)
        # ② 构建伪 token
        p_tokens_ids = tokenizer.convert_tokens_to_ids(
        ["[unused{}]".format(i + 1) for i in range(p_embedding_num)])

        # ③ 按预算裁剪正文长度：[CLS] + MASK + 正文 + [SEP] + 伪 token
        tmp_input_ids = input_ids[:-1] # 先去 [SEP]
        tmp_input_ids = tmp_input_ids[:max_seq_len - len(mask_ids) - len(p_tokens_ids) - 1]
        # ④ 在 [CLS] 之后插入 [MASK]
        tmp_input_ids = (tmp_input_ids[:start_mask_position] + mask_ids
        + tmp_input_ids[start_mask_position:])
        input_ids = tmp_input_ids + [input_ids[-1]] # 补回 [SEP]
        input_ids = p_tokens_ids + input_ids # 伪 token 拼到最前

        # ⑤ 记录 MASK 位置（伪 token 占位导致整体右移）
        mask_positions = [len(p_tokens_ids) + start_mask_position + i
        for i in range(max_label_len)]

        tokenized_output['input_ids'].append(input_ids)
        tokenized_output['attention_mask'].append(get_attention_mask(input_ids)) # ★
        tokenized_output['mask_positions'].append(mask_positions)

        if train_mode:
            mask_labels = tokenizer(text=label)['input_ids'][1:-1] # 剥 [CLS]/[SEP]
            mask_labels = mask_labels[:max_label_len]
            mask_labels += [tokenizer.pad_token_id] * (max_label_len - len(mask_labels))
            tokenized_output['mask_labels'].append(mask_labels)
```

**（1）为什么 `attention_mask` 要重新算？**

```python
def get_attention_mask(alist):
 return np.where(np.array(alist) > 0, 1, 0).tolist()
```

伪 token `[unused1]`~`[unused6]` 在中文 BERT 词表里是 id 1~99（`> 0`），它们是**真实存在、需要参与注意力**的位置；尾部补的 `[PAD]` 才是 id 0。而 `tokenizer` 返回的 `attention_mask` **不知道你手工往前面塞了 token**，直接用会把伪 token 当 padding 忽略掉，**软模板就完全失效了**。

代码注释里留了痕迹，这本身就是一条踩坑记录：

```python
# 不修改位置（结果指标较低）
# tokenized_output['attention_mask'].append(encoded_inputs['attention_mask'])
```

**静默失效是最难查的 bug 类型**——它不报错、只是掉点。更稳的写法是**不依赖"id > 0"这个隐式约定**，而是显式基于长度构造：

```python
seq_len = len(input_ids)
attention_mask = [1] * seq_len + [0] * (max_seq_len - seq_len)
```

**（2）为什么 `split('\t', 1)` 要限制切分次数？** 评论内容里完全可能出现制表符（从网页复制粘贴的文本常带）。不限次数的话 `split('\t')` 会返回 3 个以上元素，直接 `ValueError: too many values to unpack`。加 `maxsplit=1` 只按第一个制表符切成"标签"和"其余全部"，天然健壮。

**对照 PET 的 `data_preprocess.py` 写的是 `split('\t')`（不限次数）——这是一处真实存在的健壮性差距。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「P-Tuning：把软模板插进输入序列」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/06-项目-电商评论分类（BERT+PET与P-Tuning）.md)
