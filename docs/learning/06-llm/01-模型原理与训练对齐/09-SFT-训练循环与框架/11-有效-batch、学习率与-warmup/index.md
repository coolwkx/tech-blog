---
article_id: kp-cf31e28e9f901e8d
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b7b8e8f583cb
learning_sourceId: b7b8e8f583cb
learning_order: 10
learning_objective: 理解并验证：有效 batch、学习率与 warmup
---

# 有效 batch、学习率与 warmup

> **学习目标**：能够解释「有效 batch、学习率与 warmup」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型的训练目标；tokenizer 与特殊 token（BOS/EOS/PAD）；交叉熵损失；LoRA 的注入方式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）与显存账本（见 [02 篇](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)）。
>
> **所属主题**：SFT 训练循环与框架 · 关键机制

## 本次只学这一点

$$
B_{\text{有效}} = b_{\text{micro}} \times n_{\text{accum}} \times N_{\text{卡数}}
$$

学习率与有效 batch 大致成**亚线性**关系：把有效 batch 扩大 $k$ 倍，常用做法是把学习率放大 $\sqrt{k}$ 倍（线性放大 $\times k$ 往往过大）。这也是"小 batch 用大学习率、大 batch 用相对小学习率"的经验来源。

**warmup 的作用**：训练初期 Adam 的二阶动量估计方差很大，直接上大学习率容易发散或掉进坏区域。warmup 的步数常取总步数的 3%～10%。在 `Trainer` 里用 `warmup_ratio` 或 `warmup_steps` 指定。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「有效 batch、学习率与 warmup」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/05-SFT训练循环与框架.md)
