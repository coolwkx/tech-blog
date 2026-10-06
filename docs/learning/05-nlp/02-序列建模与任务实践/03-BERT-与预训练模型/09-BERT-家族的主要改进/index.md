---
article_id: kp-693effe9d50d0969
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 8
learning_objective: 理解并验证：BERT 家族的主要改进
---

# BERT 家族的主要改进

> **学习目标**：能够解释「BERT 家族的主要改进」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 方法细节

## 本次只学这一点

| 模型 | 改进点 | 关键细节 |
|------|--------|----------|
| **ALBERT** | ① 词嵌入参数因式分解 ② 隐藏层参数共享 ③ 去掉 NSP 换 SOP ④ 去掉 dropout ⑤ MLM 任务优化 | 嵌入参数量从 $30000\times768\approx2300$ 万降到 $30000\times128+128\times768\approx48$ 万；Block 参数量降至 BERT 的 1/12 或 1/24；90% 的 steps 用长度 512 的长句（BERT 是 90% 用 128 短句）；预测 N-gram 片段而非单个 token。`albert-tiny` 仅 4 层、1.8M 参数，训练与推理提速约 10 倍，LCQMC 相似度测试达 85.4%（比 bert-base 仅低 1.5%） |
| **RoBERTa** | 六点训练细节优化 | ① More data：16GB → 160GB ② Larger batch：256 → 最大 8000 ③ Training longer ④ **No NSP** ⑤ **Dynamic masking**（每个 epoch 重新生成 mask，而非预处理时固定）⑥ **Byte-level BPE**（词表从 3 万增到 5 万） |
| **MacBERT** | 面向中文的改进 | ① MLM 用**近义词替换**代替 `[MASK]`：全词 mask + n-gram mask，1–4 字遮掩比例 40%/30%/20%/10%；用 Word2Vec 找近义词替换，避免 exposure bias ② 删除 NSP 换成 SOP。在阅读理解等中文任务上表现优秀 |
| **SpanBERT** | Span 级掩码 + SBO 目标 | ① **Span Masking**：按几何分布随机选 span 长度（平均约 3.8）、再均匀分布选起始位置；② **Span Boundary Objective (SBO)**：用 span 前后边界两个词的向量 + span 内位置向量预测原词，与 MLM 损失相加共同训练 |

WWM（Whole Word Masking）的思路也值得记住：中文场景下原版 BERT 是字级 MASK，会把本该强相关的连续字词割裂；WWM 改为**整词遮掩**：

```
原始输入: 使用语言模型来预测下一个词的概率
原始 BERT: 使用语言[MASK]型来[MASK]测下一个词的[MASK]率
BERT-WWM: 使用语言[MASK][MASK]来[MASK][MASK]下一个词的[MASK][MASK]
```

延伸：百度的 ERNIE 直接引入命名实体等外部知识，做**整个实体**的遮掩训练。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 家族的主要改进」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
