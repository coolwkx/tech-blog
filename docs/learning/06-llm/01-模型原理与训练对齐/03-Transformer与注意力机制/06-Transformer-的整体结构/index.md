---
article_id: kp-7c2226403fa8a099
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 5
learning_objective: 理解并验证：Transformer 的整体结构
---

# Transformer 的整体结构

> **学习目标**：能够解释「Transformer 的整体结构」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

原始 Transformer = encoder 堆叠 + decoder 堆叠，每个 block 由「注意力子层 + 前馈子层」再加残差与归一化构成。

| 模块 | 组成 | 作用 |
|---|---|---|
| Encoder Block | Multi-Head Self-Attention + Feed Forward | 双向编码输入序列 |
| Decoder Block | Masked Multi-Head Self-Attention + Cross-Attention + Feed Forward | 因果生成，并参考 encoder 输出 |

**GPT 对 Decoder Block 的裁剪**：取消了第二个 encoder-decoder attention 子层，只保留
Masked Multi-Head Attention 与 Feed Forward。GPT-1 用了 12 个 Decoder Block（原始 Transformer 用 6 个）。

**BERT 的三大模块**：

| 模块 | 说明 |
|---|---|
| Embedding 模块 | Token Embeddings + Segment Embeddings + Position Embeddings，三者**直接相加**；首 token 是 `[CLS]`，可用于分类 |
| 双向 Transformer | 只使用经典 Transformer 的 Encoder 部分，完全舍弃 Decoder；两个预训练任务都体现在这里 |
| 预微调模块 | 按任务调整：句级分类直接取 `[CLS]` 的最后一层隐状态加全连接层后 softmax |

（BERT-Base 关键参数：12 层、12 个 head、特征维度 768、总参数量 1.15 亿；训练数据为
BooksCorpus（800M words）+ English Wikipedia（2500M words）。）

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Transformer 的整体结构」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
