---
article_id: kp-a20394721c000e32
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-ae2a0b64784b
learning_sourceId: ae2a0b64784b
learning_order: 2
learning_objective: 理解并验证：PyTorch 核心抽象一览
---

# PyTorch 核心抽象一览

> **学习目标**：能够解释「PyTorch 核心抽象一览」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会 Python（类、`with`、装饰器）；知道张量与矩阵乘法；了解前向传播、损失函数、梯度下降与链式法则（参见本目录 01 反向传播与计算图、02 优化与训练技巧）。
>
> **所属主题**：-深度学习框架实践 · 核心思想

## 本次只学这一点

| 抽象 | 一句话职责 | 常见 API | 容易踩的细节 |
| --- | --- | --- | --- |
| `torch.Tensor` | 多维数组 + 设备 + dtype + `grad_fn` | `torch.tensor/zeros/ones/randn/arange` | 默认 dtype `float32`；整数张量不能求导 |
| `autograd` | 记录计算图、反向算梯度 | `requires_grad`、`.backward()`、`.grad`、`torch.no_grad()` | `.grad` 是**累加**的，不清零等于放大学习率 |
| `nn.Module` / `nn.functional` | 可组合层/模型容器；无状态函数式算子 | `nn.Linear`、`nn.Sequential`、`F.relu`、`F.cross_entropy` | 子模块必须赋给 `self.xxx`；`F.dropout` 要手动传 `training=self.training` |
| `torch.optim` | 按 `.grad` 更新参数 | `SGD`、`Adam`、`AdamW`、`lr_scheduler` | 必须在 `backward()` 前创建，且传 `model.parameters()` |
| `Dataset` / `DataLoader` | 单样本访问 → 批量化迭代 | `__len__`、`__getitem__`、`batch_size/shuffle/num_workers` | Windows 上 `num_workers>0` 需配合 `if __name__ == '__main__'` |
| `torch.save` / `load`、`device` | 序列化参数；决定张量/模型在 CPU 还是 GPU | `torch.save`、`load_state_dict`、`torch.device('cuda')`、`.to(device)` | 只存 `state_dict` 最稳；模型与数据必须同设备，否则 device mismatch |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PyTorch 核心抽象一览」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)
