---
article_id: kp-bfe259399388eea4
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-563344f304a7
learning_sourceId: 563344f304a7
learning_order: 4
learning_objective: 理解并验证：Soft Prompt 的信息流
---

# Soft Prompt 的信息流

> **学习目标**：能够解释「Soft Prompt 的信息流」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT 与 MLM 预训练目标（见《02-Transformer与注意力机制》）、Python 与 HTTP 基础、PyTorch 训练循环。
>
> **所属主题**：-大模型API与调用实践 · 关键机制

## 本次只学这一点

以「$p$ 个伪 token + 输入」为例，前向过程分四步：

| 步骤 | 操作 | 张量形状 |
|---|---|---|
| ① | $n$ 个 token $x_1,\dots,x_n$ 经预训练模型的 embedding table 映射为向量 | $n \times e$ |
| ② | 把连续模板中的每个伪标记 $v_i$ 视为参数，通过另一个 embedding table 得到 $p$ 个伪 token 的向量矩阵 | $p \times e$ |
| ③ | 将文本与 prompt 拼接得到新输入 | $(p+n)\times e \to \mathbb{R}^{(p+n)\times e}$ |
| ④ | 新的输入喂入模型，得到新的表征；**只有 prompt 对应的向量表征参数
 $\mathbf{P}\in\mathbb{R}^{p\times e}$ 随训练更新** | — |

关键结论：**整个过程中预训练的大模型参数被冻结**，只有 $\mathbf{P}$ 在更新。

**提示**：Prompt Tuning 的 embedding 前缀是加在开头的，看起来更像"模仿 Instruction 指令"，
而 P-Tuning 添加的位置不固定；Prompt Tuning 不需要额外的 MLP 来初始化，而 P-Tuning 需要
LSTM + MLP 做初始化。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Soft Prompt 的信息流」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md)
