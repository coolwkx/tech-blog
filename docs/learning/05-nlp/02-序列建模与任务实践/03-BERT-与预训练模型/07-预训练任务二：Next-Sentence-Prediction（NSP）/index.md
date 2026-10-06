---
article_id: kp-5aac7769e4874b8a
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 6
learning_objective: 理解并验证：预训练任务二：Next Sentence Prediction（NSP）
---

# 预训练任务二：Next Sentence Prediction（NSP）

> **学习目标**：能够解释「预训练任务二：Next Sentence Prediction（NSP）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

QA、NLI 这类任务需要理解**两个句子之间的关系**，因此 BERT 引入 NSP：输入句子对 (A, B)，预测 B 是否是 A 的真实下一句。

- 所有语句都被选作句子 A；
- 50% 的 B 是原文中真实跟随 A 的下一句（`IsNext`，正样本）；
- 50% 的 B 是从原文随机抽取的一句（`NotNext`，负样本）；
- 该任务在上测试集能取得 97%–98% 的准确率。

**后续反思**（重要，面试常问）：NSP 后来被广泛质疑「太简单」。RoBERTa 直接取消 NSP；ALBERT 用 SOP（Sentence Order Prediction，把 `[A,B]` 作为正样本、`[B,A]` 作为负样本）替代。原因是「随机句 vs 下一句」往往主题就完全不同，模型靠主题匹配就能答对，学不到真正的语序/连贯性知识。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「预训练任务二：Next Sentence Prediction（NSP）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
