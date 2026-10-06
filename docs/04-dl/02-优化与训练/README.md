---
article_id: "26f53ca6b2f1"
learning_kind: "guide"
learning_category: "04-dl"
---

# ② 优化与训练

> 本章共 3 篇笔记。

## 本节目录

| 笔记 | 难度 | 预计用时 | 状态 |
| --- | --- | --- | --- |
| [2.1 激活函数与损失函数](02-激活函数与损失函数.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [2.2 优化器与正则化](04-优化器与正则化.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [2.3 深度学习框架实践](07-深度学习框架实践.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |

## 本章要回答的问题

**2.1 激活函数与损失函数**
- 用 MSE 训练分类器
- `CrossEntropyLoss` 前又加 `Softmax`
- `nn.NLLLoss` 前忘 `log_softmax`

**2.2 优化器与正则化**
- 把"局部最小"当主要敌人、忽略鞍点
- 大 batch 直接配大学习率
- 忘记 `model.eval`

**2.3 深度学习框架实践**
- 忘记 `optimizer.zero_grad()`
- 用 `loss.item()` 去 backward
- 在 `no_grad()` 里算 loss 后 backward

状态说明：✅ 已完成 ｜ 🚧 编写中 ｜ 📝 计划中

---

[⬅️ 返回本区目录](../README.md)
