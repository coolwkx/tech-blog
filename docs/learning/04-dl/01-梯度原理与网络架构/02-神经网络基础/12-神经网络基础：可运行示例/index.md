---
article_id: kp-6d2ad573798a40b1
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-80865e5a5b8b
learning_sourceId: 80865e5a5b8b
learning_order: 11
learning_objective: 理解并验证：-神经网络基础：可运行示例
---

# -神经网络基础：可运行示例

> **学习目标**：能够解释「-神经网络基础：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性代数（矩阵乘法、转置、Frobenius 范数）、微积分（链式法则、偏导、Taylor 展开）、Logistic 回归与 Softmax 回归、梯度下降与交叉熵损失。
>
> **所属主题**：-神经网络基础 · 可运行示例

## 本次只学这一点

下面用 PyTorch 的 `nn.Linear` / `nn.Sequential` 搭一个 MLP，在一个**线性不可分**的 two-moons 数据集上训练。同时手工复算第一层，验证"仿射变换 + 非线性变换"这一理解，并与单层线性模型对比说明隐藏层的价值。

```python
import numpy as np
import torch
from torch import nn

# ---------- 1. 造一个非线性可分的数据集（two moons） ----------
def make_two_moons(n_samples=800, noise=0.1, seed=0):
 rng = np.random.default_rng(seed)
 n_out = n_samples // 2
 n_in = n_samples - n_out
 t_out = np.linspace(0.0, np.pi, n_out)
 t_in = np.linspace(0.0, np.pi, n_in)
 outer = np.stack([np.cos(t_out), np.sin(t_out)], axis=1) # 外弧
 inner = np.stack([1.0 - np.cos(t_in), 1.0 - np.sin(t_in) - 0.5], axis=1) # 内弧
 X = np.concatenate([outer, inner], axis=0)
 y = np.concatenate([np.zeros(n_out, dtype=np.int64), np.ones(n_in, dtype=np.int64)])
 X = X + rng.normal(0.0, noise, size=X.shape) # 加噪声，避免"太干净"
 idx = rng.permutation(n_samples)
 return X[idx].astype(np.float32), y[idx]

torch.manual_seed(0)
X_np, y_np = make_two_moons
X = torch.from_numpy(X_np) # (N, 2) float32
y = torch.from_numpy(y_np) # (N,) int64 —— CrossEntropyLoss 要求 long
X_train, y_train = X[:600], y[:600]
X_test, y_test = X[600:], y[600:]

# ---------- 2. 单层线性模型（等价于 Logistic 回归，作为 baseline） ----------
linear = nn.Linear(2, 2) # 无隐藏层：只有仿射变换
opt = torch.optim.Adam(linear.parameters(), lr=0.05)
crit = nn.CrossEntropyLoss
for _ in range(300):
 opt.zero_grad() # 必须清零，否则梯度会累加
 loss = crit(linear(X_train), y_train) # 直接喂 logits，不要再手动 softmax
 loss.backward()
 opt.step
with torch.no_grad:
 acc_linear = (linear(X_test).argmax(dim=1) == y_test).float.mean.item

# ---------- 3. 两层隐藏层的 MLP：仿射 + 非线性，反复复合 ----------
model = nn.Sequential(
 nn.Linear(2, 16), nn.ReLU, # 第 1 个隐藏层
 nn.Linear(16, 16), nn.ReLU, # 第 2 个隐藏层
 nn.Linear(16, 2), # 输出层：2 个神经元，配 CrossEntropyLoss(=Softmax+对数似然)
)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4) # L2 -> 结构风险
criterion = nn.CrossEntropyLoss
for epoch in range(300):
 model.train
 optimizer.zero_grad()
 logits = model(X_train) # (N, 2)，未归一化的净输入 z^(L)
 loss = criterion(logits, y_train) # 内部自动做 log_softmax + NLL
 loss.backward() # 反向传播，PyTorch 自动微分
 optimizer.step

model.eval
with torch.no_grad:
 logits = model(X_test)
 prob = logits.softmax(dim=1) # 只有推理/看概率时才手动 softmax
 acc_mlp = (logits.argmax(dim=1) == y_test).float.mean.item
print(f"linear baseline acc = {acc_linear:.3f}")
print(f"MLP acc = {acc_mlp:.3f}")
print("params =", sum(p.numel for p in model.parameters()))

# ---------- 4. 手工复算第一层，验证 z = Wx + b, a = f(z) ----------
W1, b1 = model[0].weight, model[0].bias # (16, 2), (16,)
with torch.no_grad:
 z1_manual = X_test @ W1.t + b1 # 仿射变换
 a1_manual = torch.relu(z1_manual) # 非线性变换
 z1_module = model[0](X_test)
 a1_module = model[1](z1_module)
 print("z1 一致:", torch.allclose(z1_manual, z1_module, atol=1e-6))
 print("a1 一致:", torch.allclose(a1_manual, a1_module, atol=1e-6))
```

**几个必须理解的细节**

1. `nn.Linear(in_features, out_features)` 内部存的是 $\boldsymbol W\in\mathbb{R}^{\text{out}\times\text{in}}$，前向是 `x @ W.t + b`，正好对应 $\boldsymbol z=\boldsymbol W\boldsymbol a+\boldsymbol b$；参数总量是 `in*out + out`（每个输出神经元一个偏置）。
2. `nn.Sequential` 只负责按顺序串起子模块，**非线性必须自己显式加**（`nn.ReLU`）。`nn.Linear` 连着 `nn.Linear` 等于一个大的仿射变换，这正是 2.2 节的结论。
3. `nn.CrossEntropyLoss` = `log_softmax` + `NLLLoss`，输入必须是 **logits**、标签必须是 **`int64` 类别下标**。手动再套一层 softmax 或把标签做成 one-hot float 都会出错。
4. `optimizer.zero_grad()` 每个 step 都要调用；`weight_decay` 是 L2 正则，对应 2.5 节的结构风险项（PyTorch 的 `Adam` 把 L2 直接加在 loss 梯度上，`AdamW` 则是解耦的 weight decay，两者并不等价）。
5. 单层模型准确率明显低于 MLP，是因为两类数据不是线性可分的——**非线性激活函数带来的隐藏层特征变换 $\phi(\boldsymbol x)$ 才是收益来源**。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-神经网络基础：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-神经网络基础.md)
