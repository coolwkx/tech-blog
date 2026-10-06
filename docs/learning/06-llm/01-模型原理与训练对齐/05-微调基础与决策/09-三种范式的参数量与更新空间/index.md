---
article_id: kp-56fffdea11e0afcb
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-9bc2a0f8b073
learning_sourceId: 9bc2a0f8b073
learning_order: 8
learning_objective: 理解并验证：三种范式的参数量与更新空间
---

# 三种范式的参数量与更新空间

> **学习目标**：能够解释「三种范式的参数量与更新空间」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer 与注意力机制；预训练语言模型的 MLM / CLM 目标；LoRA 的公式（见《03-LoRA原理与工程实践》）；基本的 PyTorch 训练循环概念。
>
> **所属主题**：微调基础与决策 · 关键机制

## 本次只学这一点

设模型总参数量为 $P$。

**全参微调**：可训练参数 $P_{\text{train}} = P$，更新空间是整个 $\mathbb{R}^{P}$。

**LoRA**：对每一个被选中的权重矩阵 $W\in\mathbb{R}^{d\times k}$（约 $d=k$），注入

$$
W' = W + \frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k}
$$

单个矩阵的新增参数量为

$$
\Delta P_{\text{layer}} = r(d+k) \approx 2dr \quad (d=k)
$$

若模型有 $L$ 个被适配的矩阵，则

$$
P_{\text{train}}^{\text{LoRA}} \approx 2Ldr
$$

而全参是 $P \approx L\cdot c\cdot d^2$（$c$ 为每层里 $d\times d$ 矩阵的个数，Transformer 中典型 $c\ge 4$）。因此占比约为

$$
\frac{P_{\text{train}}^{\text{LoRA}}}{P}\approx \frac{2r}{c\,d}
$$

代入 $r=8,\ d=4096,\ c=4$：$\frac{16}{4\times 4096}\approx 0.098\%$，与实践中"LoRA 可训练参数占 0.1% 量级"的观察一致（**推导**：[03 篇](../../../../../06-llm/02-微调与对齐/03-LoRA原理与工程实践.md)会给出更细的逐矩阵算法）。

**提示微调**：只训练输入侧的嵌入向量或前缀。设前缀长度为 $p$、隐藏维度为 $d$，且只在**输入层**加（Prompt Tuning）：

$$
P_{\text{train}}^{\text{PromptTuning}} = p\cdot d
$$

若在**每一层**都加前缀（Prefix-Tuning / P-Tuning v2），则

$$
P_{\text{train}}^{\text{Prefix}} = p\cdot d\cdot L\cdot c_{\text{prefix}}
$$

其中 $c_{\text{prefix}}$ 是该层注入位置的个数（典型 K/V 两处，部分实现含注意力输出）。这解释了 Prefix-Tuning 的参数量会随层数线性放大，而 Prompt Tuning 不会。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三种范式的参数量与更新空间」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/01-微调基础与决策.md)
