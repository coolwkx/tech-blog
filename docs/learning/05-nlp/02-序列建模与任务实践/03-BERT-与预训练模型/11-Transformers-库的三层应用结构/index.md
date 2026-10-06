---
article_id: kp-8b52317db1b2eade
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 10
learning_objective: 理解并验证：Transformers 库的三层应用结构
---

# Transformers 库的三层应用结构

> **学习目标**：能够解释「Transformers 库的三层应用结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

Hugging Face 的 Transformers 库提供三个抽象层次，从简到繁：

| 层次 | API | 特点 | 何时用 |
|------|-----|------|--------|
| 管道（Pipeline） | `pipeline(task=..., model=...)` | 高度集成，几行代码完成一个任务 | 快速验证、Demo、推理服务 |
| 自动模型（AutoModel） | `AutoTokenizer` + `AutoModelForXxx` | 可载入并使用 BERTology 系列模型，自动匹配结构 | 需要自定义前向逻辑（如取特定层输出） |
| 具体模型（SpecificModel） | `BertModel` / `BertForSequenceClassification` 等 | 显式指定模型类与参数 | 需要精细控制（改结构、改初始化、接自定义头） |

`pipeline` 支持的任务与对应中文模型示例（用的本地路径）：

| task | 任务 | 说明 |
|------|------|------|
| `text-classification` / `sentiment-analysis` | 文本分类 / 情感分析 | 输出 `{'label': ..., 'score': ...}` |
| `feature-extraction` | 特征抽取 | 输出每个 token 的向量，需与其他模型配合 |
| `fill-mask` | 完形填空（遮蔽语言建模） | 输入必须含 `[MASK]`（大写），**一次只能预测一个 MASK** |
| `question-answering` | 抽取式问答 | 输入 `context` + `question`，输出 `answer` 与 `start/end` |
| `summarization` | 文本摘要 | 输入长文输出短摘要 |
| `ner` | 命名实体识别 | 输出实体片段与类型 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Transformers 库的三层应用结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
