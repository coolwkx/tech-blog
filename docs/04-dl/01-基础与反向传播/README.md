---
article_id: "093d3b1848bc"
learning_kind: "guide"
learning_category: "04-dl"
---

# ① 基础与反向传播

> 本章共 3 篇笔记。

## 本节目录

| 笔记 | 难度 | 预计用时 | 状态 |
| --- | --- | --- | --- |
| [1.1 反向传播与计算图](01-反向传播与计算图.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [1.2 神经网络基础](01-神经网络基础.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |
| [1.3 反向传播与梯度下降](03-反向传播与梯度下降.md) | ⭐⭐⭐ | 25min | ✅ 已完成 |

## 本章要回答的问题

**1.1 反向传播与计算图**
- 说清 reverse-mode AD 与数值微分的差异，以及它为什么对「多输入单输出」最省算力
- 手推两层 MLP 的 $\partial L/\partial W_1,\ \partial L/\partial W_2$，并用形状标注自查
- 从零写出支持 `+ * ** relu` 的 `Value` 类并跑通训练

**1.2 神经网络基础**
- 在两个 `nn.Linear` 之间忘记加激活函数
- `CrossEntropyLoss` 前又手动做 softmax
- 训练循环里忘记 `optimizer.zero_grad()`

**1.3 反向传播与梯度下降**
- batch 梯度忘记除以 batch size
- Softmax 前不减去每行最大值
- ReLU 导数用错对象或乘法顺序写反

状态说明：✅ 已完成 ｜ 🚧 编写中 ｜ 📝 计划中

---

[⬅️ 返回本区目录](../README.md)
