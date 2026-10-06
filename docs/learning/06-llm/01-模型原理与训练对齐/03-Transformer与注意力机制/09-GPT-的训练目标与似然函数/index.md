---
article_id: kp-3dc865edf16f2f0c
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 8
learning_objective: 理解并验证：GPT 的训练目标与似然函数
---

# GPT 的训练目标与似然函数

> **学习目标**：能够解释「GPT 的训练目标与似然函数」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

给定句子 $U=[u_1,u_2,\dots,u_n]$，GPT-1 的预训练目标是最大化：

$$L_1(U)=\sum_{i}\log P(u_i \mid u_{i-k},\dots,u_{i-1};\Theta)$$

其中 $k$ 是上文的窗口大小——$k$ 越大，模型可获取的上文信息越充足，能力越强（但计算成本上升）。
输入经过 embedding（$W_e$ 形状 $[vocab\_size, embedding\_dim]$）加位置编码（$W_p$ 形状 $[max\_seq\_len, embedding\_dim]$）
得到 $h_0$，再经多层 Decoder Block 得到 $h_t$，最后用语言模型头预测下一个词。

微调阶段则是把下游任务的输入改造成 token 序列 $[x_1,\dots,x_n]$，用最后一层隐状态 $h_t$ 接一个输出层 $W_y$ 预测标签 $y$：

$$L_2(C)=\sum_{(x,y)}\log P(y\mid x_1,\dots,x_n)$$

**最终优化目标是两者加权和**；适配下游任务分两步：① 按任务定义不同的输入构造方式；② 为不同任务增加不同的分类层。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GPT 的训练目标与似然函数」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
