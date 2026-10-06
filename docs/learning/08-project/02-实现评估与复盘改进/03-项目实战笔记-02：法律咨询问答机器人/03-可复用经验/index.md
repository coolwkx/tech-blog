---
article_id: kp-7ffa9472cdcaa6b6
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 12
learning_objective: 理解并验证：可复用经验
---

# 可复用经验

> **学习目标**：能够解释「可复用经验」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 可复用经验

## 本次只学这一点

1. **"数据 → Dataset → collate_fn → 训练循环"这条管线是所有 NLP 训练项目的骨架。** 换成 BERT 分类、NER、摘要，形状会变，但"tokenize 缓存 → 变长填充 → shift 对齐 → mask 忽略"这套思想不变。手写过一次，就再也不会被 `Trainer` 的参数名绕晕。
2. **`collate_fn` 是处理变长序列的唯一正确位置。** 不要在 `__getitem__` 里 padding（会把整个数据集撑成 max_len 大小），也不要在模型里 padding（污染模型职责）。
3. **`-100` 是"不算 loss"的通用暗号。** 从 `CrossEntropyLoss(ignore_index=-100)` 到 `DataCollatorWithPadding`，整个 PyTorch/HF 生态都用它，记住它。
4. **梯度累积的本质是"把 batch 拆开、把 loss 除一下、攒够步数再更新"。** 它不改数学结果（近似），只改显存占用，是消费级显卡训练大模型的唯一出路。
5. **生成任务调优的优先级**：先保证训练对齐没错（acc 能到合理值）→ 再调解码策略（重复惩罚 / top-k / 温度）→ 最后才考虑换模型或加数据。
6. **特殊 token 可以承载语义。** 本项目把 `[SEP]` 同时用作"话轮分隔符"和"生成终止符"，零成本实现了对话边界管理。设计自己的对话格式时，尽量复用已有的特殊符号，而不是随便新造一个 token。
7. **训练一定要存两类 checkpoint**：按指标最优（`min_ppl_model_bj`）+ 按固定间隔（`bj_epoch{n}`）。生成任务里"指标最优"经常不是"人看着最好"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可复用经验」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
