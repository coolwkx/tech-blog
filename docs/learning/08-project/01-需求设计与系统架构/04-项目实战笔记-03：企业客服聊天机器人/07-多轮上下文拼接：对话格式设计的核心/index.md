---
article_id: kp-bccfc63dcc5d9991
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 7
learning_objective: 理解并验证：多轮上下文拼接：对话格式设计的核心
---

# 多轮上下文拼接：对话格式设计的核心

> **学习目标**：能够解释「多轮上下文拼接：对话格式设计的核心」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
# interact.py（精简）
history = [] # 每个元素 = 一轮 utterance 的 token id 列表

while True:
    text = input("user:")
    samples_file.write("user:{}\n".format(text))

    text_ids = tokenizer.encode(text, add_special_tokens=False)
    history.append(text_ids)

    # 每个 input 以 [CLS] 开头，然后依次拼接最近 N 轮，每轮后跟 [SEP]
    input_ids = [tokenizer.cls_token_id]
    for history_utr in history[-pconf.max_history_len:]: # max_history_len = 3
        input_ids.extend(history_utr)
        input_ids.append(tokenizer.sep_token_id)

        input_ids = torch.tensor(input_ids, dtype=torch.long, device=device).unsqueeze(0)
```

**三处关键决策**：

1. **为什么要 `history[-max_history_len:]`**：模型 `n_ctx=1024`，而 `max_len=300` 是单次生成上限。如果无限累加历史，迟早超出上下文窗口，且越早的内容对当前话题越不重要。滑窗是最简单有效的截断策略。
2. **为什么 `add_special_tokens=False`**：`BertTokenizerFast.encode` 默认会在句首尾加 `[CLS]/[SEP]`。我们手工管理这些符号，必须关掉，否则序列里会出现重复的特殊符，模型会把它们当成真实语义。
3. **为什么 `[SEP]` 在两处语义不同**：训练时它是"话轮边界"，推理时它同时是"生成结束信号"。这个一符两用让解码循环的停止条件变得极其简单——不需要额外定义 EOS。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多轮上下文拼接：对话格式设计的核心」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
