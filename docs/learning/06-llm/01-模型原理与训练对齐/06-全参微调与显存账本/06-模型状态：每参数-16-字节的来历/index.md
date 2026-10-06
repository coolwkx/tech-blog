---
article_id: kp-3c6ddc36b8c11db3
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 5
learning_objective: 理解并验证：模型状态：每参数 16 字节的来历
---

# 模型状态：每参数 16 字节的来历

> **学习目标**：能够解释「模型状态：每参数 16 字节的来历」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

先看**纯 fp32**（无混合精度、Adam）：

$$
B_{\text{权重}} = 4P_{\text{train}},\quad
B_{\text{梯度}} = 4P_{\text{train}},\quad
B_{\text{Adam}} = 2\times 4P_{\text{train}} = 8P_{\text{train}}
$$

合计 $16\,P_{\text{train}}$ 字节/参数。

再看**混合精度（AMP）+ Adam**，这是实际训练中最常见的配置：

| 项 | 精度 | 每参数字节 |
| --- | --- | --- |
| 模型权重（前向/反向用的低精度副本） | bf16 / fp16 | 2 |
| 梯度（低精度副本） | bf16 / fp16 | 2 |
| fp32 主权重（master weights，更新在这里做） | fp32 | 4 |
| Adam 一阶动量 $m$ | fp32 | 4 |
| Adam 二阶动量 $v$ | fp32 | 4 |
| **合计** | | **16** |

$$
\boxed{B_{\text{模型状态}} = 16\,P_{\text{train}}\ \text{字节} \quad(\text{AMP} + \text{Adam})}
$$

**7B 算例（推导）**：$7\times10^9 \times 16 = 112\times10^9$ 字节 $= 112\times10^9 / 1024^3 \approx 104.3$ GiB（按 1 GiB $=1024^3$ 字节），或按厂商口径 $112$ GB（$10^9$ 字节）。

> 这个 16 B/参数 的结论与 DeepSpeed ZeRO 文档中对"模型状态"的拆分一致（参见 [DeepSpeed ZeRO 教程](https://www.deepspeed.ai/tutorials/zero/) 与 [ZeRO 论文 arXiv:1910.02054](https://arxiv.org/abs/1910.02054)）。本文的推导过程如上表所示。

**注意**：这 112 GB **不含激活值**。所以"7B 全参微调至少要 8×80GB"这个经验说法的来源就是它——8 卡分片后模型状态降到约 14 GB/卡，剩下的余量留给激活。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「模型状态：每参数 16 字节的来历」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
