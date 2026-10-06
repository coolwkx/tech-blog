---
article_id: kp-fe7549c29cd22037
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-531018f7b810
learning_sourceId: 531018f7b810
learning_order: 9
learning_objective: 理解并验证：与 PyTorch 对照
---

# 与 PyTorch 对照

> **学习目标**：能够解释「与 PyTorch 对照」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：偏导数与梯度、单变量链式法则、矩阵乘法与转置、Python 闭包与递归。
>
> **所属主题**：反向传播与计算图 · 深入机制

## 本次只学这一点

```python
"""依赖：pip install torch（本机验证版本 2.11.0+cpu）。"""
import torch

def forward(x, W1, b1, W2, b2):
 h = torch.relu(x @ W1.T + b1) # (B,2)@(2,H) -> (B,H)
 return h @ W2.T + b2, h # (B,H)@(H,1) -> (B,1)

torch.manual_seed(0)
B, D_in, H, D_out = 8, 2, 4, 1
x, y = torch.randn(B, D_in), torch.randn(B, D_out)
W1, b1 = torch.randn(H, D_in, requires_grad=True), torch.zeros(H, requires_grad=True)
W2, b2 = torch.randn(D_out, H, requires_grad=True), torch.zeros(D_out, requires_grad=True)
params = [W1, b1, W2, b2]

y_hat, h = forward(x, W1, b1, W2, b2)
loss = ((y_hat - y) ** 2).mean
loss.backward() # 触发反向，填充叶子节点的 .grad
assert all(p.grad.shape == p.shape for p in params) # 形状必须与参数一致

# ---- 手写解析梯度（4.1 节公式），与 autograd 逐元素比对 ----
delta2 = 2 * (y_hat - y) / B # (B,O)
dW2 = delta2.T @ h # (O,B)@(B,H) -> (O,H) == W2 形状
db2 = delta2.sum(0) # (O,)
delta1 = (delta2 @ W2) * (h > 0).float # (B,O)@(O,H) -> (B,H)
dW1 = delta1.T @ x # (H,B)@(B,D_in) -> (H,D_in)
db1 = delta1.sum(0) # (H,)
for manual, auto in [(dW1, W1.grad), (db1, b1.grad), (dW2, W2.grad), (db2, b2.grad)]:
 assert (manual - auto).abs.max.item < 1e-6
print("手写梯度与 autograd 一致")

# ---- no_grad 不建图；detach 把张量从图上摘成新的叶子 ----
with torch.no_grad:
 assert not forward(x, W1, b1, W2, b2)[0].requires_grad
assert h.requires_grad and not h.detach.requires_grad

# ---- 标准训练循环 ----
opt = torch.optim.SGD(params, lr=0.05)
for step in range(50):
 loss = ((forward(x, W1, b1, W2, b2)[0] - y) ** 2).mean
 opt.zero_grad() # 必须：清空上一轮梯度
 loss.backward()
 opt.step # 内部在 no_grad 下做 p.add_(grad, alpha=-lr)
print(f"final loss = {loss.item:.6f}")
```

| 手写引擎 | PyTorch | 说明 |
| --- | --- | --- |
| `Value(data)` | `torch.tensor(data, requires_grad=True)` | 是否建图由 `requires_grad` 决定 |
| `loss.backward()` | `loss.backward()` | 都以 `grad=1` 起步，走逆拓扑序 |
| `v.grad` | `v.grad` | 都是累加语义（首次反向前置 `None`） |
| `p.grad = 0.0` | `opt.zero_grad()` | PyTorch 默认 `set_to_none=True`，更快更省内存 |
| `p.data -= lr * p.grad` | `opt.step` | 更新在 `no_grad` 下进行，不污染图 |
| `_backward` 闭包 | `autograd.Function.backward()` | 局部 VJP 规则；一个手写闭包 = 一个 Function 节点 |
| 手动拓扑排序 | 引擎按依赖计数调度 | PyTorch 用 task queue 实现 |
| 图随对象生命周期回收 | 反向结束即释放 saved tensors | 故二次反向要 `retain_graph=True` |
| 只支持标量 | 支持任意形状张量 | 每条 VJP 都在张量层面实现 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「与 PyTorch 对照」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/01-反向传播与计算图.md)
