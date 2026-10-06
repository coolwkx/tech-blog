---
article_id: kp-867dc398c1d1471b
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-ae2a0b64784b
learning_sourceId: ae2a0b64784b
learning_order: 7
learning_objective: 理解并验证：张量运算速查（已在本机实跑）
---

# 张量运算速查（已在本机实跑）

> **学习目标**：能够解释「张量运算速查（已在本机实跑）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会 Python（类、`with`、装饰器）；知道张量与矩阵乘法；了解前向传播、损失函数、梯度下降与链式法则（参见本目录 01 反向传播与计算图、02 优化与训练技巧）。
>
> **所属主题**：-深度学习框架实践 · 可运行示例

## 本次只学这一点

```python
import torch

x = torch.arange(24, dtype=torch.float32)
print(x.view(2, 3, 4).shape, x.reshape(4, 6).shape) # (2,3,4) 要求连续；(4,6) 非连续时拷贝
print(x.reshape(4, 6).data_ptr() == x.data_ptr()) # True：连续时 reshape 不拷贝
t = torch.arange(12).view(3, 4).t() # 转置后非连续
print(t.is_contiguous()) # False
try:
 t.view(12) # RuntimeError: view size is not compatible
except RuntimeError:
 print("view 失败，改用 reshape:", t.reshape(12).shape)
pd = torch.ones(1, 6)
print(pd.unsqueeze(0).shape, pd.expand(4, 6).shape) # [1,1,6] 插维；[4,6] 0 步长视图
p, q = torch.ones(3, 4), torch.arange(4, dtype=torch.float32)
print((p + q).shape) # (3,4)：(4,) 广播成 (1,4) 再扩到 (3,4)
A = torch.arange(6, dtype=torch.float32).view(2, 3)
print((A * A).shape, (A @ A.t()).shape) # (2,3) 元素级相乘；(2,2) 矩阵乘
print(torch.equal(A.mm(A.t()), A @ A.t())) # True：mm 只吃 2D，@ 支持批量与广播
u, v = torch.zeros(2, 3), torch.ones(2, 3)
print(torch.cat([u, v], 0).shape, torch.stack([u, v], 0).shape) # (4,3) 拼接；(2,2,3) 新维
```

广播规则：**从最右维逐维比对，每维要么相等、要么其中一个是 1（或该张量没有这一维），否则报错**——所以 `(3,4)+(4,)` 合法而 `(3,2)+(3,4)` 报错。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「张量运算速查（已在本机实跑）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)
