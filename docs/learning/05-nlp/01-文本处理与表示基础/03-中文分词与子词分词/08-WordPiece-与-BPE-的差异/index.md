---
article_id: kp-b407d0193e0ba126
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a66bd7ad2f1
learning_sourceId: 3a66bd7ad2f1
learning_order: 7
learning_objective: 理解并验证：WordPiece 与 BPE 的差异
---

# WordPiece 与 BPE 的差异

> **学习目标**：能够解释「WordPiece 与 BPE 的差异」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理流水线、序列标注的基本概念、Python 正则与字典操作。
>
> **所属主题**：中文分词与子词分词 · 方法细节

## 本次只学这一点

WordPiece 表面流程与 BPE 一模一样（都是贪心合并相邻符号对），差异只在**选哪一对合并**：

$$
\text{score}(a,b) = \frac{\text{count}(ab)}{\text{count}(a)\times \text{count}(b)}
$$

即用**点互信息（PMI）式**的准则，而非纯频次。直觉：`e`+`s` 频次很高，但如果 `e` 和 `s` 本身就各自到处都是，它们的结合未必有信息量；WordPiece 更偏好「两者单独出现少、但一起出现多」的组合。BERT 用它训练出 30522 个 token 的英文词表，其中一个重要细节是**续接子词前缀 `##`**：`playing` → `play` + `##ing`，用 `##` 标记「这个词片段不是词首」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「WordPiece 与 BPE 的差异」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)
