---
article_id: kp-7cde5d1c8fbd6d7c
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 10
learning_objective: 理解并验证：梯度检验（gradient check）
---

# 梯度检验（gradient check）

> **学习目标**：能够解释「梯度检验（gradient check）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 深入机制

## 本次只学这一点

解析梯度写错时最典型的现象是**训练照样跑、loss 照样降**（只是慢或降不到底），所以必须单独检验一次。

```python
"""依赖：numpy。中心差分检验解析梯度。"""
import numpy as np

def f(x, y, w, b):
 return float(((w * x + b - y) ** 2).mean)

def analytic_grad(x, y, w, b):
 diff = w * x + b - y
 return 2 * (diff * x).mean, 2 * diff.mean

def numeric_grad(x, y, w, b, eps=1e-6):
 """中心差分；必须用 float64，否则相减会灾难性抵消。"""
 w, b = np.float64(w), np.float64(b)
 gw = (f(x, y, w + eps, b) - f(x, y, w - eps, b)) / (2 * eps)
 gb = (f(x, y, w, b + eps) - f(x, y, w, b - eps)) / (2 * eps)
 return gw, gb

x = np.linspace(-2, 2, 11)
y = np.sin(x)
aw, ab = analytic_grad(x, y, 0.7, -0.2)
nw, nb = numeric_grad(x, y, 0.7, -0.2)
for name, a, n in [("w", aw, nw), ("b", ab, nb)]:
 rel = abs(a - n) / (abs(a) + abs(n) + 1e-12)
 print(f"{name}: analytic={a:+.8f} numeric={n:+.8f} rel={rel:.2e}")
 assert rel < 1e-6, name
print("梯度检验通过")
```

| 原则 | 原因 |
| --- | --- |
| 用 `float64` / `torch.float64` | `float32` 下 $f(\theta+\epsilon)-f(\theta-\epsilon)$ 灾难性抵消，误差可能比梯度本身还大 |
| $\epsilon$ 取 $10^{-5}\sim10^{-6}$，不是越小越好 | 太小被浮点误差淹没，太大被截断误差主导；中心差分误差为 $O(\epsilon^2)$ |
| 用**相对误差**，双精度下要求 $<10^{-6}$ | 绝对误差没有可比性 |
| 避开 ReLU 折点（$z\approx0$） | 折点不可导，任何差分都不可信；换几组随机输入 |
| 优先用 `torch.autograd.gradcheck` | 它已处理好 map 结构、非光滑点与双精度 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「梯度检验（gradient check）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
