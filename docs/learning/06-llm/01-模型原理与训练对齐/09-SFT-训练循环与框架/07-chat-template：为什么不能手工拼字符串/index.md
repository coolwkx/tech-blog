---
article_id: kp-eb176603871884f0
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 6
learning_objective: 理解并验证：chat template：为什么不能手工拼字符串
---

# chat template：为什么不能手工拼字符串

> **学习目标**：能够解释「chat template：为什么不能手工拼字符串」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

`apply_chat_template` 做的事是：把 messages 列表按模型自带的 Jinja 模板渲染成**与预训练时完全一致**的格式。不同模型的格式差异极大，例如：

```text
# 一类模板（ChatML 风格）
<|im_start|>system
你是一个助手<|im_end|>
<|im_start|>user
你好<|im_end|>
<|im_start|>assistant
你好，有什么可以帮你？<|im_end|>

# 另一类模板（特殊 token 分隔，注意 header 后的空行）
<|begin_of_text|><|start_header_id|>user<|end_header_id|>

你好<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

手工拼接的风险：少一个换行、把 `<|im_end|>` 写成 `<|endoftext|>`、忘记在 assistant 前加空格——这些都可能让模型进入"非训练分布"的格式，表现为回答质量暴跌却不报错。

**正确姿势**：

```python
text = tokenizer.apply_chat_template(messages, tokenize=False)
ids = tokenizer(text, add_special_tokens=False)["input_ids"]
```

注意 `tokenize=True` 也可以直接用，但做 masking 时我们往往需要同时拿到"带生成前缀的 prompt 长度"和"完整序列"，所以模式上更常见的是先渲染成字符串（见 3 节的实现）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「chat template：为什么不能手工拼字符串」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
