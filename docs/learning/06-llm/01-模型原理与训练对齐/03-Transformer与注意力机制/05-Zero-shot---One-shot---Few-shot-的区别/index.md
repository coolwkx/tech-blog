---
article_id: kp-3931e8af0a4f6370
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 4
learning_objective: 理解并验证：Zero-shot / One-shot / Few-shot 的区别
---

# Zero-shot / One-shot / Few-shot 的区别

> **学习目标**：能够解释「Zero-shot / One-shot / Few-shot 的区别」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 核心概念

## 本次只学这一点

以「英译法」为例：

| 方式 | 做法 | 效果（GPT-3 论文结论） |
|---|---|---|
| Zero-shot | 只给任务描述，直接给测试数据 | 最差 |
| One-shot | 任务描述 + 1 个示例 | 次之 |
| Few-shot | 任务描述 + N 个示例 | 最佳 |

**In-context learning（ICL，情境学习/提示学习）** 与 fine-tuning 的核心区别：

| 对比项 | Fine-tuning | In-context learning |
|---|---|---|
| 是否更新参数 | 更新（有梯度回传） | **不更新**，只做前向推理 |
| 需要数据量 | 大（任务相关标注集） | 小（约 10~100 条示例） |
| 新任务适应 | 需重新训练、每个任务一套权重 | 改 prompt 即可 |
| 本质 | 把任务知识写进参数 | 让模型从上下文「读出」任务模式 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Zero-shot / One-shot / Few-shot 的区别」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
