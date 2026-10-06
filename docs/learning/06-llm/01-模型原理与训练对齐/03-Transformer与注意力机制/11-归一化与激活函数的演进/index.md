---
article_id: kp-32dc0aabd155be1f
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-a3491ff89088
learning_sourceId: a3491ff89088
learning_order: 10
learning_objective: 理解并验证：归一化与激活函数的演进
---

# 归一化与激活函数的演进

> **学习目标**：能够解释「归一化与激活函数的演进」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵乘法与张量维度、softmax、点积的几何含义、PyTorch/NumPy 基础。
>
> **所属主题**：-Transformer与注意力机制 · 关键机制

## 本次只学这一点

| 方案 | 相比前代的变化 | 为什么 |
|---|---|---|
| LayerNorm | 在每个样本的特征维度上计算均值/方差并标准化，含可学习参数 $\gamma,\beta$ | 训练稳定，不依赖 batch 大小 |
| Pre-LayerNorm | 把 LN 放到 Self-Attention 与 Feed Forward **之前**（GPT-2 起） | 随层数加深，梯度消失/爆炸风险增大，前置 LN 减小层间方差波动，梯度更稳 |
| RMSNorm | 去掉减去均值的部分，只用均方根归一化 | 计算更高效；不去除均值成分，更好保留信号 |
| DeepNorm | 残差连接加缩放因子 $\alpha>1$：`LayerNorm(αx + Sublayer(x))` | 专为极深 Transformer 设计，平衡残差以提升训练稳定性 |
| ReLU → GELU | 引入高斯分布特性，负输入处更平滑 | 提升性能与训练效率 |
| GLU 系列：GeGLU / SwiGLU | 在 GLU 门控结构上把激活换成 GELU / Swish(βx) | 门控 + 平滑激活，提升表达能力，主流大模型普遍采用 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「归一化与激活函数的演进」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/02-Transformer与注意力机制.md)
