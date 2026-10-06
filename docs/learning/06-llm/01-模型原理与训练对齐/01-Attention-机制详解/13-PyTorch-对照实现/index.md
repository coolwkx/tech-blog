---
article_id: kp-0258b4b94fddd2ff
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-c3d60ecbbf7d
learning_sourceId: c3d60ecbbf7d
learning_order: 12
learning_objective: 理解并验证：PyTorch 对照实现
---

# PyTorch 对照实现

> **学习目标**：能够解释「PyTorch 对照实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、reshape/transpose）；概率（softmax、期望与方差、熵）；微积分（链式法则、梯度消失）；本仓库 [Transformer 架构总览](../../../../../06-llm/01-架构与预训练/README.md)。
>
> **所属主题**：Attention 机制详解 · 深入机制

## 本次只学这一点

生产代码不要手写，用融合好的算子：

```python
# 依赖: pip install torch (本机验证于 torch 2.11.0+cpu)
import torch
import torch.nn.functional as F

torch.manual_seed(0)
B, h, n, d_head = 2, 4, 6, 8
q = torch.randn(B, h, n, d_head, dtype=torch.float64)
k = torch.randn(B, h, n, d_head, dtype=torch.float64)
v = torch.randn(B, h, n, d_head, dtype=torch.float64)

# 一行搞定：融合实现，自动选 flash / memory-efficient / math 后端
out = F.scaled_dot_product_attention(q, k, v, is_causal=True)

# 手写参照：显式构造因果掩码，验证等价
mask = torch.triu(torch.full((n, n), float("-inf"), dtype=torch.float64), diagonal=1)
p = torch.softmax(q @ k.transpose(-1, -2) / (d_head ** 0.5) + mask, dim=-1)
manual = p @ v

print((out - manual).abs.max.item) # 6.66e-16，仅浮点误差
```

- 输入形状是 **`[B, h, n, d_head]`**，不是 `[B, n, d_model]`；拆头要自己做。
- `is_causal=True` 由算子内部生成掩码，比在外面构造 `[n,n]` 掩码**更省显存**（朴素实现要额外分配 $n^2$ 掩码张量，长序列下本身就很贵）。
- `attn_mask` 与 `is_causal` 可同时传，语义是**叠加**，混用容易出错，建议分开测。
- 用 `torch.nn.attention.sdpa_kernel` 上下文管理器可强制指定后端，用于对比数值与性能。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PyTorch 对照实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-Attention机制详解.md)
