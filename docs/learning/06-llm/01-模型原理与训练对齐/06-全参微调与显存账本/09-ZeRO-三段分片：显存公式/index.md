---
article_id: kp-a4505772c94d8389
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 8
learning_objective: 理解并验证：ZeRO 三段分片：显存公式
---

# ZeRO 三段分片：显存公式

> **学习目标**：能够解释「ZeRO 三段分片：显存公式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

设数据并行度为 $N$，模型状态在 AMP + Adam 下每参数 16 字节（2 权重 + 2 梯度 + 12 优化器）。分片后**每卡的模型状态显存**为：

| 阶段 | 分片对象 | 每卡模型状态（字节/参数） | 7B、$N=8$ 算例（推导，GB $=10^9$ 字节） |
| --- | --- | --- | --- |
| 基线（DDP） | 无 | $2+2+12 = 16$ | $16\times7 = 112$ GB（单卡放不下） |
| ZeRO-1 | 优化器状态（$12$ B/参数） | $4+\dfrac{12}{8} = 5.5$ | $5.5\times7 = 38.5$ GB |
| ZeRO-2 | 优化器状态 + 梯度（$14$ B/参数） | $2+\dfrac{14}{8} = 3.75$ | $3.75\times7 = 26.25$ GB |
| ZeRO-3 | 全部（$16$ B/参数） | $\dfrac{16}{8} = 2.0$ | $2.0\times7 = 14.0$ GB |

逐步验算（$N=8$，注意"字节/参数"要乘以 $7\times10^9$ 再换算成 GB）：

- **ZeRO-1**：权重与梯度不分片 $(2+2)\times7 = 28$ GB，优化器状态 $\frac{12\times7}{8} = 10.5$ GB，合计 **38.5 GB/卡**。
- **ZeRO-2**：权重不分片 $2\times7 = 14$ GB，梯度与优化器状态 $\frac{(2+12)\times7}{8} = 12.25$ GB，合计 **26.25 GB/卡**。
- **ZeRO-3**：$\frac{16\times7}{8} = $ **14.0 GB/卡**。

三档的差别可以概括为：

$$
B_{\text{ZeRO-}k} = \underbrace{2P}_{\text{fp16 权重}} + \frac{\left(2P + 4P + 4P + 4P\right)\ \text{中被切分的部分}}{N}
$$

- ZeRO-1 切 $\{4P+4P+4P\}=12P$；
- ZeRO-2 再切 $2P$ 梯度，共 $14P$；
- ZeRO-3 连 $2P$ 权重一起切，共 $16P$。

**FSDP** 在 PyTorch 里是 ZeRO-3 思路的原生实现：参数按 flat parameter 分组分片，前向时 all-gather 当前层需要的分片，用完即释放，反向时再 all-gather 并 reduce-scatter 梯度。FSDP2 进一步用 `fully_shard` 的逐模块 API 替代了 FSDP1 的 flat-parameter 包装（参见 [PyTorch FSDP 文档](https://docs.pytorch.org/docs/stable/fsdp.html) 与 [FSDP2 教程](https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html)）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「ZeRO 三段分片：显存公式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
