---
article_id: kp-42ab444b26329fb6
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 7
learning_objective: 理解并验证：gradient checkpointing 的收益与代价
---

# gradient checkpointing 的收益与代价

> **学习目标**：能够解释「gradient checkpointing 的收益与代价」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

不做 checkpointing 时，激活随层数**线性**增长，即 $O(L)$。做**完全重计算**（每个 block 都重算前向）后，只需要保存每个 block 的**输入**：

$$
B_{\text{激活}}^{\text{ckpt}} \approx L\cdot 2\,s\,b\,h\ \text{字节}
$$

代入 7B：$32\times2\times2048\times1\times4096 = 5.37\times10^8$ 字节 $\approx 0.5$ GiB。相比 28.5 GiB，**下降约 57 倍**。

代价是**额外的前向计算**：反向时每个 block 要重算一次前向，整体训练时间通常增加约 20%～40%（具体取决于模型与硬件，取决于算力/带宽比）。

更精细的做法是**选择性重计算（selective activation recomputation）**：只对显存开销大的部分（注意力矩阵）做重计算，其余保留。Megatron 论文指出这样能把激活降到显著更低，同时重算带来的额外计算量远小于完全重计算（参见 [arXiv:2205.05198](https://arxiv.org/abs/2205.05198)）。

在 PyTorch 中启用：

```python
model.gradient_checkpointing_enable()
# 使用 Trainer 时：
# TrainingArguments(gradient_checkpointing=True, ...)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「gradient checkpointing 的收益与代价」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
