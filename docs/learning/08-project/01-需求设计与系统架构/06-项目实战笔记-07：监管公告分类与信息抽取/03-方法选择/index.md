---
article_id: kp-11c1d4fe4f3c9631
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-5ddeeee1c909
learning_sourceId: 5ddeeee1c909
learning_order: 2
learning_objective: 理解并验证：方法选择
---

# 方法选择

> **学习目标**：能够解释「方法选择」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：In-context Learning / Zero-shot / Few-shot 的基本概念、Chat 模型的 `messages` 结构（system / user / assistant）、JSON 与正则表达式、Ollama 本地模型调用。
>
> **所属主题**：项目实战笔记 07：监管公告分类与信息抽取 · 项目目标与业务背景

## 本次只学这一点

```text
模型：Qwen2.5:7b（本项目用 Ollama 本地调用）
 原使用 ChatGLM-6B（需 13G 显存，可量化加载）
方法：In-context Learning
 Zero-shot → 只给任务说明，不给例子
 Few-shot → 给任务说明 + 几个"输入→正确输出"的示例
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「方法选择」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/07-项目-监管公告分类与信息抽取.md)
