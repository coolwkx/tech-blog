---
article_id: kp-6aadc9ffd4e7862f
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-b5f5d873a117
learning_sourceId: b5f5d873a117
learning_order: 6
learning_objective: 理解并验证：激活值：真正会爆炸的一项
---

# 激活值：真正会爆炸的一项

> **学习目标**：能够解释「激活值：真正会爆炸的一项」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：反向传播与计算图；PyTorch 的优化器状态概念；Transformer 层的结构（注意力矩阵的形状 $b\times a\times s\times s$）；LoRA 的参数量公式（见 [03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)）。
>
> **所属主题**：全参微调与显存账本 · 关键机制

## 本次只学这一点

激活值由两部分构成：

1. **逐层线性/归一化的中间输出**，形状为 $b\times s\times h$，每层若干份；
2. **注意力矩阵**，形状为 $b\times a\times s\times s$——这一项对 $s$ 是**平方**关系。

先给一个最简推导（只看注意力矩阵，fp16，$b=1$）：

$$
B_{\text{attn}} \approx L\cdot a\cdot s^2\cdot b\cdot 2\ \text{字节}
$$

代入 $L=32,\ a=32,\ s=2048,\ b=1$：

$$
32\times32\times2048^2\times1\times2 = 8.59\times10^9\ \text{字节} \approx 8.6\ \text{GB}
$$

已经 8.6 GB 了。而完整的激活开销还要加上 LayerNorm、MLP 中间层、残差等。工业界广泛引用的是 Megatron-LM 系列给出的**逐层激活估算式**（*Reducing Activation Recomputation in Large Transformer Models*, [arXiv:2205.05198](https://arxiv.org/abs/2205.05198)）：

$$
B_{\text{激活, 每层}} \approx s\,b\,h\left(34 + 5\,\frac{a\,s}{h}\right)\ \text{字节} \quad(\text{fp16，无重计算，TP}=1)
$$

其中常数 34 对应 LayerNorm/残差/MLP 等按 $sbh$ 线性增长的部分，$5as/h$ 这一项就是注意力矩阵及其副本带来的二次项。

**7B 全参激活算例（推导，按上式）**：$s=2048,\ b=1,\ h=4096,\ a=32,\ L=32$

$$
s b h = 2048\times1\times4096 = 8.39\times10^6
$$

$$
34 + 5\frac{as}{h} = 34 + 5\times\frac{32\times2048}{4096} = 34 + 80 = 114
$$

$$
B_{\text{激活, 每层}} = 8.39\times10^6\times114 \approx 9.57\times10^8\ \text{字节} \approx 0.89\ \text{GiB}
$$

$$
B_{\text{激活}} = 32\times0.89 \approx 28.5\ \text{GiB}
$$

**结论**：$b=1,\ s=2048$ 时激活约 28.5 GiB；若 $b=4$，激活线性放大到约 114 GiB；若 $s$ 翻倍到 4096，那个 $5as/h$ 项继续放大，激活还会更陡。这就是"序列长度是显存杀手"的定量来源。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「激活值：真正会爆炸的一项」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/02-全参微调与显存账本.md)
