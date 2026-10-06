---
article_id: kp-3f905d3725a5c6a6
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 1
learning_objective: 理解并验证：项目级数据结构总览
---

# 项目级数据结构总览

> **学习目标**：能够解释「项目级数据结构总览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · 核心概念

## 本次只学这一点

| 文件 / 模块 | 作用 | 关键内容 |
|---|---|---|
| `data/train.txt` | 训练集 | 每行 `标签\t文本`，本文示例为 63 条 |
| `data/dev.txt` | 验证集 | 每行 `标签\t文本`，本文示例为 590 条 |
| `data/prompt.txt` | 硬模板 | 单行，如 `这是一条{MASK}评论：{textA}。` |
| `data/verbalizer.txt` | 标签词映射 | 每行 `主标签\t子标签1,子标签2,...` |
| `template.py` | 模板解析与编码 | `HardTemplate` 类 |
| `data_preprocess.py` | 样本 → 张量 | `convert_example()` |
| `verbalizer.py` | 标签 ↔ 子标签互转 | `Verbalizer` 类 |
| `common_utils.py` | 损失与解码 | `mlm_loss()`、`convert_logits_to_ids()` |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「项目级数据结构总览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
