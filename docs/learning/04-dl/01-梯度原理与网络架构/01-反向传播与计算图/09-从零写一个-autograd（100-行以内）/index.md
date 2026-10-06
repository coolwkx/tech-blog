---
article_id: kp-5eaf11d8e9366231
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 8
learning_objective: 理解并验证：从零写一个 autograd（100 行以内）
---

# 从零写一个 autograd（100 行以内）

> **学习目标**：能够解释「从零写一个 autograd（100 行以内）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 深入机制

## 本次只学这一点

核心只有三件事：**前向时建图并注册局部反向规则；反向时按逆拓扑序调用；所有梯度用 `+=` 累加。**

```text
"""极简标量 autograd，纯标准库，可直接运行。"""
import math
import random

class Value:
 """一个标量自动微分节点（对标 PyTorch 的 Tensor + 计算图）。"""

 def __init__(self, data, _children=, _op=""):
 self.data = float(data)
 self.grad = 0.0 # dL/d(self)，由 backward 填充
 self._backward = lambda: None # 局部反向规则，默认空操作
 self._prev = set(_children) # 上游节点（图的边）

 # ---------- 前向：建图 + 注册局部的 backward 规则 ----------
 def __add__(self, other):
 other = other if isinstance(other, Value) else Value(other)
 out = Value(self.data + other.data, (self, other), "+")

 def _backward:
 self.grad += out.grad * 1.0 # 加法：梯度原样分发
 other.grad += out.grad * 1.0

 out._backward = _backward
 return out

 def __mul__(self, other):
 other = other if isinstance(other, Value) else Value(other)
 out = Value(self.data * other.data, (self, other), "*")

 def _backward:
 self.grad += out.grad * other.data # 乘法：梯度乘对方的「前向值」
 other.grad += out.grad * self.data

 out._backward = _backward
 return out

 def __pow__(self, k):
 out = Value(self.data ** k, (self,), f"**{k}")

 def _backward:
 self.grad += out.grad * k * (self.data ** (k - 1))

 out._backward = _backward
 return out

 def relu(self):
 out = Value(max(0.0, self.data), (self,), "relu")

 def _backward:
 self.grad += out.grad * (1.0 if out.data > 0 else 0.0)

 out._backward = _backward
 return out

 # ---------- 反向：拓扑排序 + 逆序调用局部规则 ----------
 def backward(self):
 topo, visited = [], set

 def build(v):
 if v not in visited:
 visited.add(v)
 for child in v._prev:
 build(child)
 topo.append(v) # 后序：保证父在子之后

 build(self)
 self.grad = 1.0 # dL/dL = 1，反向起点
 for v in reversed(topo): # 逆拓扑序 = 反向传播顺序
 v._backward

 # ---------- 语法糖 ----------
 def __neg__(self):
 return self * -1.0

 def __sub__(self, other):
 return self + (-other)

 def __radd__(self, other):
 return self + other

 def __rmul__(self, other):
 return self * other

 def __truediv__(self, other):
 other = other if isinstance(other, Value) else Value(other)
 return self * (other ** -1)

if __name__ == "__main__":
 a, b = Value(2.0), Value(-3.0)
 ((a * b + a ** 2) / 2.0).backward() # df/da = 0.5, df/db = a/2 = 1.0
 assert abs(a.grad - 0.5) < 1e-9 and abs(b.grad - 1.0) < 1e-9

 x = Value(3.0)
 (x * x + x).backward() # 两条路径累加：2x + 1 = 7
 assert abs(x.grad - 7.0) < 1e-9

 z = Value(-2.0)
 (z.relu * 3.0).backward() # 负区间导数为 0
 assert abs(z.grad - 0.0) < 1e-9
 print("引擎自检通过")
```

**为什么必须逆拓扑序**：一个节点可能有多个下游消费者（例如 $A_1$ 同时喂给 $W_2$ 的乘法和 $b_2$ 的加法）。只有等所有下游都把梯度累加进 `v.grad`，才能用完整的它调用 `v._backward`。**为什么用 `+=`**：同一个 `Value` 可能出现在多个位置，每条路径都要贡献，用 `=` 会丢掉先到的贡献。

用它训练（把上一段存成 `engine.py`）：

```python
"""依赖：engine.py（上面的 Value 类）。两层 MLP (2 -> 4 -> 1) 拟合 y = sin(3x)。"""
import math
import random
from engine import Value

def mse_loss(preds, targets):
    return sum((p - t) ** 2 for p, t in zip(preds, targets)) * (1.0 / len(preds))

random.seed(42)
vals = [i / 20.0 for i in range(-20, 21)]
X = [[Value(v), Value(v ** 2)] for v in vals]
Y = [math.sin(3 * v) for v in vals]

n_in, n_hid, n_out = 2, 4, 1 # 2 -> 4 -> 1
W1 = [[Value(random.uniform(-1, 1)) for _ in range(n_in)] for _ in range(n_hid)]
b1 = [Value(0.0) for _ in range(n_hid)]
W2 = [[Value(random.uniform(-1, 1)) for _ in range(n_hid)] for _ in range(n_out)]
b2 = [Value(0.0) for _ in range(n_out)]
params = [p for row in W1 for p in row] + b1 + [p for row in W2 for p in row] + b2

def mlp(x):
    h = [sum((W1[j][i] * x[i] for i in range(n_in)), b1[j]).relu for j in range(n_hid)]
    return [sum((W2[k][j] * h[j] for j in range(n_hid)), b2[k]) for k in range(n_out)]

for step in range(400):
    loss = mse_loss([mlp(x)[0] for x in X], Y)
    for p in params:
        p.grad = 0.0 # 对应 optimizer.zero_grad()
        loss.backward() # 一行完成 4.1 节的全部公式
        for p in params:
            p.data -= 0.05 * p.grad # 对应 optimizer.step
            if step % 200 == 0:
                print(f"step {step:3d} loss={loss.data:.6f}")
                # 本机实测：loss 0.638394 -> 0.033850 -> 0.008748
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从零写一个 autograd（100 行以内）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
