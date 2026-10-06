---
article_id: kp-ad44a3cf09140e29
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 11
learning_objective: 理解并验证：踩坑与解决
---

# 踩坑与解决

> **学习目标**：能够解释「踩坑与解决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 踩坑与解决

## 本次只学这一点

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| 语料被切成 1 段 / 段落数量异常 | 语料是 CRLF 换行，代码只切 `"\n\n"` | 先判断 `if "\r\n" in data` 再选分隔符 | 处理跨平台文本文件时，**永远先统一换行符**（`data.replace("\r\n", "\n")`）再切分，比到处写 if 更干净 |
| tokenize 后序列里出现大量 `[CLS]/[SEP]` | `tokenizer.encode` 默认 `add_special_tokens=True`，与手写拼接重复 | 传 `add_special_tokens=False` | 手写特殊符号时，一定要显式关掉 tokenizer 的自动添加 |
| 训练几个 epoch 后 loss 不降 / 学习率变 0 | `t_total` 忘除 `gradient_accumulation_steps`，调度器提前走完 | `t_total = len(dl) // accum * epochs` | 手写训练循环时，**先打印 `scheduler.get_last_lr` 逐 step 观察曲线**，再开始长时间训练 |
| 模型输出大量 `[PAD]` 或空回答 | label 的 pad 用了 0，loss 把 pad 位置也算了；或输入/标签没有 shift 对齐 | labels 用 `padding_value=-100`；训练用 `labels=` 让模型内部 shift | 记住 PyTorch 的约定：**忽略位永远用 -100**，输入 pad 用 0 |
| 生成的回答反复重复同一句 | 采样时同一 token 被反复抽中 | `repetition_penalty=10.0`，对已出现 token 降权；再用 top-k 截断尾部 | 生成质量差时，优先怀疑"没有重复惩罚 + 解码策略是贪心" |
| Loss 突然 NaN | 学习率过高导致梯度爆炸 | `clip_grad_norm_(params, max_grad_norm=4.0)` + warmup | 梯度裁剪和 warmup 是 transformer 训练的默认配置，不是可选项 |
| 训练 OOM | batch_size=4 且序列最长 300，12 层模型对显存要求高 | 梯度累积（4 步等效 batch 16）+ 调小 `max_len` | 显存不够时，第一反应应该是"梯度累积"，而不是立刻砍 batch（会伤效果） |
| `assert model.config.vocab_size == tokenizer.vocab_size` 失败 | 用了 `vocab2.txt`（更大词表）但 config.json 里还是旧 vocab_size | 让 config 与 vocab 文件严格配对 | 词表换了，**config.json 的 `vocab_size` 必须同步改**，否则 lm_head 尺寸对不上 |
| 验证 loss 越低生成越差 | 交叉熵低 ≠ 人读起来好（语料是"分号罗列"风格） | 同时保存"困惑度最低"和"固定间隔"的 checkpoint，人工对比 | 生成任务的评估必须**人看**，自动指标只能做粗筛 |
| Flask 每次请求都很慢 | 在请求处理函数内部加载模型 | 模型在模块顶层加载一次，`model.eval` | 服务化第一原则：**重资源只初始化一次** |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「踩坑与解决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
