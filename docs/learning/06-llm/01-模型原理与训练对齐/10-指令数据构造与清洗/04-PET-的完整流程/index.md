---
article_id: kp-40349bcb9cf7d4f9
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 3
learning_objective: 理解并验证：PET 的完整流程
---

# PET 的完整流程

> **学习目标**：能够解释「PET 的完整流程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · PET 详解：把分类任务改写成完形填空

## 本次只学这一点

PET（Pattern-Exploiting Training）出自论文《Exploiting Cloze Questions for Few Shot Text Classification and Natural Language Inference》，整体是四步：

```
① 人工设计 Pattern：      这是一条{MASK}{MASK}评论：{textA}。
② 人工设计 Verbalizer：   手机 → 手机 ；水果 → 苹果/香蕉/橘子
③ 把训练样本全部改写：    手机\t这个手机也太卡了。  →  "这是一条[MASK][MASK]评论：这个手机也太卡了。"
④ 用 MLM 目标微调：      只在 MASK 位置上算交叉熵，标签 = 标签词的 token id
```

推理时反过来：模型在 MASK 位置输出词表上的概率分布 → 取 argmax 得到预测词 → 用 Verbalizer 反向查表得到类别。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PET 的完整流程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
