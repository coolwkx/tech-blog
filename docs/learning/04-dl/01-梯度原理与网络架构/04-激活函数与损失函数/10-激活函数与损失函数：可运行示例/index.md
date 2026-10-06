---
article_id: kp-da1a41d4f5778a17
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-93c70b02b9e5
learning_sourceId: 93c70b02b9e5
learning_order: 9
learning_objective: 理解并验证：-激活函数与损失函数：可运行示例
---

# -激活函数与损失函数：可运行示例

> **学习目标**：能够解释「-激活函数与损失函数：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：线性判别函数、Logistic/Softmax 回归、梯度下降、链式法则与反向传播、伯努利分布与交叉熵。
>
> **所属主题**：-激活函数与损失函数 · 可运行示例

## 本次只学这一点

代码做三件事：(1) 验证 `CrossEntropyLoss` 等价于手写 `log_softmax` + NLL；(2) 证明 MSE+Sigmoid 在饱和区梯度塌缩而交叉熵不会；(3) 用同一份数据训练两个分类器，观察 MSE 收敛更慢。

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)

# ===== 1. CrossEntropyLoss == log_softmax + NLL == 手写公式 =====
logits = torch.tensor([[2.0, 0.5, -1.0], [-0.3, 1.2, 0.1], [0.0, 0.0, 3.0]])
target = torch.tensor([0, 2, 2]) # 类别索引，不是 one-hot

loss_api = nn.CrossEntropyLoss(logits, target)
loss_manual = F.nll_loss(F.log_softmax(logits, dim=1), target)
loss_formula = (torch.logsumexp(logits, 1)
- logits.gather(1, target[:, None]).squeeze(1)).mean
print(f"[1] CrossEntropyLoss={loss_api:.6f} NLL={loss_manual:.6f} 手写={loss_formula:.6f}")
assert torch.allclose(loss_api, loss_manual) and torch.allclose(loss_api, loss_formula)

loss_wrong = nn.CrossEntropyLoss(F.softmax(logits, dim=1), target) # 误用：又乘了一次 softmax
print(f" [误用] 对概率再算 CE = {loss_wrong:.6f} <- 值不对, 梯度被压平")

# ===== 2. 饱和区梯度对比: MSE vs 交叉熵 =====
y = torch.tensor([1.0])
z = torch.tensor([-6.0], requires_grad=True) # 真值 1, 但模型自信地错
loss_mse = 0.5 * (torch.sigmoid(z) - y) ** 2
g_mse = torch.autograd.grad(loss_mse, z)[0]

z2 = torch.tensor([-6.0], requires_grad=True)
loss_bce = F.binary_cross_entropy_with_logits(z2, y)
g_bce = torch.autograd.grad(loss_bce, z2)[0]

print(f"\n[2] z=-6, y=1 (饱和区, 自信地错)")
print(f" MSE loss={loss_mse.item:.6f} dL/dz={g_mse.item:.6f} <- 梯度几乎为 0")
print(f" BCE loss={loss_bce.item:.6f} dL/dz={g_bce.item:.6f} <- 梯度 = p - y")
print(f" 手算 p - y = {torch.sigmoid(torch.tensor(-6.0)).item - 1:.6f}")

# ===== 3. 同一份数据: CrossEntropy 收敛快于 MSE =====
def make_data(n=1024, d=20, seed=42):
    g = torch.Generator.manual_seed(seed)
    X, w = torch.randn(n, d, generator=g), torch.randn(d, 3, generator=g)
    return X, (X @ w).argmax(dim=1)

def train(use_mse, steps=300, lr=0.1):
    X, y = make_data
    model = nn.Sequential(nn.Linear(20, 32), nn.Tanh, nn.Linear(32, 3))
    opt = torch.optim.SGD(model.parameters(), lr=lr)
    onehot = F.one_hot(y, 3).float
    for _ in range(steps):
        opt.zero_grad()
        out = model(X)
        if use_mse: # 关键: MSE 作用在 softmax 概率上, 梯度带 softmax 的饱和因子
            loss = 0.5 * ((torch.softmax(out, 1) - onehot) ** 2).sum(1).mean
        else:
            loss = F.cross_entropy(out, y) # 直接吃 logits
            loss.backward()
            opt.step
            with torch.no_grad:
                final = model(X)
                # 统一用交叉熵度量泛化前的拟合程度, 这样两种训练目标的数字才可比
                ce = F.cross_entropy(final, y).item
                acc = (final.argmax(1) == y).float.mean.item
                return ce, acc

            print
            for name, flag in [("CrossEntropy", False), ("MSE", True)]:
                for lr in (0.1, 1.0):
                    ce, a = train(flag, lr=lr)
                    print(f"[3] {name:12s} lr={lr:<4} 统一CE={ce:.4f} train acc={a:.4f}")
```

**参考输出**（在 torch 2.11 CPU 上实测；因框架版本不同，`sigmoid` 的浮点细节会让 `[2]` 的末位略有差异）：

```
[1] CrossEntropyLoss=0.626118 NLL=0.626118 手写=0.626118
 [误用] 对概率再算 CE = 0.852121 <- 值不对, 梯度被压平

[2] z=-6, y=1 (饱和区, 自信地错)
 MSE loss=0.497530 dL/dz=-0.002460 <- 梯度几乎为 0
 BCE loss=6.002476 dL/dz=-0.997527 <- 梯度 = p - y
 手算 p - y = -0.997527

[3] CrossEntropy lr=0.1 统一CE=0.1246 train acc=0.9873
[3] CrossEntropy lr=1.0 统一CE=0.0156 train acc=1.0000
[3] MSE lr=0.1 统一CE=0.3150 train acc=0.9688
[3] MSE lr=1.0 统一CE=0.0627 train acc=0.9990
```

**怎么读这三段输出**：`[1]` 说明 `CrossEntropyLoss` 的数值与手写 log-sum-exp 完全一致（`allclose` 通过），而对概率再算一次 CE 会得到错误的 `0.852`。`[2]` 直接展示核心差异：同在饱和区犯大错，MSE 的梯度只有 $-0.0025$（几乎不动），交叉熵的梯度是 $-0.9975$（几乎满格）。`[3]` 用**同一个统一指标**（都取 `F.cross_entropy`，否则 MSE 与 CE 的数值不可比）对比两种训练目标：lr=0.1 时 MSE 的 CE 为 0.315、准确率 96.88%，交叉熵的 CE 为 0.125、准确率 98.73%；lr=1.0 时前者 0.0627/99.90%，后者 0.0156/100%。**MSE 收敛更慢不是"loss 数值更大"，而是"同等步数下达不到同样的拟合程度"**——步数加到几千步差距会缩小，但在大模型、小学习率下会显著放大。二分类推荐写法：`nn.BCEWithLogitsLoss(logit, label.float)`，而非 `nn.BCELoss(torch.sigmoid(logit), label.float)`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-激活函数与损失函数：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/02-激活函数与损失函数.md)
