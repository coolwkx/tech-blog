---
article_id: kp-52a57b713fd7323b
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 7
learning_objective: 理解并验证：掩码的两种实现路径
---

# 掩码的两种实现路径

> **学习目标**：能够解释「掩码的两种实现路径」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

| 路径 | 做法 | 优点 | 风险 |
| --- | --- | --- | --- |
| **前缀长度法**（通用） | 对每个 assistant 轮次，用 `apply_chat_template(messages[:i], add_generation_prompt=True)` 渲染出 prompt 前缀，tokenize 得到长度 $L$，把 `labels[:L] = -100` | 不依赖模板细节，几乎所有模型可用 | 需要保证前缀渲染与完整渲染的前缀部分逐 token 一致（绝大多数模板满足） |
| **模板自带掩码**（推荐，若支持） | `apply_chat_template(..., return_assistant_tokens_mask=True)`，模板中用 `{% generation %}` 块标记需要计算 loss 的部分 | 精确、无需二次渲染 | 只对带 `{% generation %}` 的模板生效，否则 mask 全 0 |

一个**必须检查**的点：`return_assistant_tokens_mask` 生成的掩码是否包含 assistant 结尾的 EOS/`<|im_end|>`/`<|eot_id|>`。结尾 token **应该**参与 loss（要教模型"什么时候停"），如果被掩掉，模型可能不会正常结束。相关的修复讨论可参考 TRL 仓库中关于"训练模板必须保留 stop token 在 loss mask 中"的 issue/PR（例如 [huggingface/trl#5988](https://github.com/huggingface/trl/pull/5988)）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「掩码的两种实现路径」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
