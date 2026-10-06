---
article_id: kp-fb6c08044205d364
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 0
learning_objective: 理解并验证：显存的五个组成部分
---

# 显存的五个组成部分

> **学习目标**：能够解释「显存的五个组成部分」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 核心概念

## 本次只学这一点

训练时的显存不是"一个数字"，而是五块互不相同的开销，优化时必须对症下药：

| 组成 | 内容 | 与什么成正比 | 主要削减手段 |
| --- | --- | --- | --- |
| 模型权重（parameters） | 当前模型参数的存储 | 参数量 $P$ × 每参数字节 | 混合精度、ZeRO-3/FSDP 分片 |
| 梯度（gradients） | 每个可训练参数的梯度 | 可训练参数量 × 每梯度字节 | 混合精度、ZeRO-2/3 分片、LoRA（只对部分参数有梯度） |
| 优化器状态（optimizer states） | Adam 的一阶动量 $m$、二阶动量 $v$；混合精度下还有 fp32 主权重副本 | 可训练参数量 × 每状态字节 | ZeRO-1/2/3 分片、8-bit Adam、Adafactor、CPU offload |
| 激活值（activations） | 前向保存、反向使用的中间张量 | batch × 序列长度 × 隐藏维度 × 层数 | gradient checkpointing、更小 micro-batch、序列并行、FlashAttention |
| 临时缓冲与碎片 | 通信 buffer、CUDA 内核工作区、缓存分配器碎片 | 实现相关 | `expandable_segments`、调整 `PYTORCH_CUDA_ALLOC_CONF`、避免动态 shape |

**关键直觉**：这五项里，前三项在混合精度 + Adam 下是"每参数 16 字节"的刚性开销（推导见 2.2），而**激活值才是真正会随 batch size 和序列长度爆炸的那一项**。很多人算完权重 + 优化器状态觉得"能跑"，一开训练就 OOM，原因几乎都是漏了激活。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「显存的五个组成部分」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
