---
article_id: kp-5b0d18542fd89138
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-0ff9cceb3f3d
learning_sourceId: 0ff9cceb3f3d
learning_order: 9
learning_objective: 理解并验证：-反向传播与梯度下降：可运行示例
---

# -反向传播与梯度下降：可运行示例

> **学习目标**：能够解释「-反向传播与梯度下降：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：矩阵与向量求导（分母布局、Jacobian）、多元链式法则、Logistic/Tanh/ReLU 的导数、Softmax 与交叉熵、Frobenius 范数与 $\ell_2$ 正则化、凸/非凸优化与局部最优的基本概念。
>
> **所属主题**：-反向传播与梯度下降 · 可运行示例

## 本次只学这一点

下面用**纯 numpy** 从零实现一个两层 MLP（ReLU 隐层 + Softmax 交叉熵），手写完整的前向与反向传播，用**中心差分**数值梯度逐元素校验解析梯度，最后跑 Mini-batch SGD。整段代码可直接运行。

```python
import numpy as np

rng = np.random.default_rng(42)


# ---------- 数据：3 类、2 维扇形区域（线性不可分，必须靠隐层） ----------
def make_data(n_per_class=40, seed=0):
    r = np.random.default_rng(seed)
    X, y = [], []
    for c in range(3):
        radius = r.uniform(0.6, 1.0, n_per_class)
        angle = r.uniform(c * 2 * np.pi / 3, (c + 1) * 2 * np.pi / 3, n_per_class)
        X.append(np.stack([radius * np.cos(angle), radius * np.sin(angle)], axis=1))
        y.append(np.full(n_per_class, c))
        return np.concatenate(X), np.concatenate(y)


    X, y = make_data()
    N, D = X.shape
    K = int(y.max()) + 1
    H = 16

    # ---------- He 初始化（ReLU 隐层用 sqrt(2 / fan_in)） ----------
    W1 = rng.normal(0.0, np.sqrt(2.0 / D), size=(D, H)); b1 = np.zeros(H)
    W2 = rng.normal(0.0, np.sqrt(2.0 / H), size=(H, K)); b2 = np.zeros(K)


    def softmax(z):
        z = z - z.max(axis=1, keepdims=True) # 每行减最大值：数值稳定，不改变结果
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)


    def forward(X, W1, b1, W2, b2):
        z1 = X @ W1 + b1 # (N, H) 净输入
        a1 = np.maximum(z1, 0.0) # (N, H) ReLU
        z2 = a1 @ W2 + b2 # (N, K) logits
        p = softmax(z2) # (N, K) 预测概率
        return p, (X, z1, a1, z2, p) # 缓存供反向使用


    def cross_entropy(p, y):
        return -np.log(p[np.arange(p.shape[0]), y] + 1e-12).mean()


    def backward(cache, y, W2):
        """返回 dW1, db1, dW2, db2（batch 平均后的梯度）"""
        X, z1, a1, z2, p = cache
        n = X.shape[0]
        Y = np.zeros_like(p)
        Y[np.arange(n), y] = 1.0
        dz2 = (p - Y) / n # Softmax + 交叉熵：dL/dz2 = (p - Y)/n
        dW2 = a1.T @ dz2 # (H, K) = delta2 * a1^T
        db2 = dz2.sum(axis=0) # (K,) = delta2
        da1 = dz2 @ W2.T # (N, H) 回传到隐层输出
        dz1 = da1 * (z1 > 0.0) # (N, H) 乘 ReLU 导数
        dW1 = X.T @ dz1 # (D, H) = delta1 * x^T
        db1 = dz1.sum(axis=0) # (H,) = delta1
        return dW1, db1, dW2, db2


    # ---------- 数值梯度（中心差分）校验解析梯度 ----------
    def loss_of(params, X, y):
        W1_, b1_, W2_, b2_ = params
        p, _ = forward(X, W1_, b1_, W2_, b2_)
        return cross_entropy(p, y)


    def numeric_grad(params, X, y, eps=1e-5):
        grads = []
        for P in params:
            g = np.zeros_like(P)
            for idx in np.ndindex(P.shape):
                old = P[idx]
                P[idx] = old + eps; lp = loss_of(params, X, y)
                P[idx] = old - eps; lm = loss_of(params, X, y)
                P[idx] = old # 必须还原，否则后续差分全错
                g[idx] = (lp - lm) / (2.0 * eps)
                grads.append(g)
                return grads


            params = [W1, b1, W2, b2]
            p, cache = forward(X, W1, b1, W2, b2)
            ana = backward(cache, y, W2)
            num = numeric_grad(params, X, y)

            print("=== gradient check (central difference, eps=1e-5) ===")
            print(f"initial loss = {cross_entropy(p, y):.6f}")
            for name, ga, gn in zip(["W1", "b1", "W2", "b2"], ana, num):
                rel = np.abs(ga - gn) / np.maximum(np.abs(ga) + np.abs(gn), 1e-12)
                print(f"{name:>3}: shape={str(ga.shape):>8} ||g||={np.linalg.norm(ga):.4e} "
                f"max_rel_err={rel.max():.3e} ok={rel.max() < 1e-6}")
                # 期望输出：四项 max_rel_err 均在 1e-10 ~ 1e-8 量级、ok=True


                # ---------- Mini-batch SGD 训练（正则只作用于 W） ----------
                def train(X, y, W1, b1, W2, b2, lr=0.5, batch_size=16, epochs=300, lam=1e-4, seed=1):
                    r = np.random.default_rng(seed)
                    n = X.shape[0]
                    for ep in range(epochs):
                        order = r.permutation(n) # 每个 epoch 重新打乱
                        for s in range(0, n, batch_size):
                            idx = order[s:s + batch_size] # 最后一批可能不足 batch_size
                            xb, yb = X[idx], y[idx]
                            _, cache = forward(xb, W1, b1, W2, b2)
                            dW1, db1, dW2, db2 = backward(cache, yb, W2)
                            W1 -= lr * (dW1 + lam * W1) # 正则只加在权重上
                            b1 -= lr * db1
                            W2 -= lr * (dW2 + lam * W2)
                            b2 -= lr * db2
                            if (ep + 1) % 100 == 0:
                                pf, _ = forward(X, W1, b1, W2, b2)
                                print(f"epoch {ep + 1:3d} loss={cross_entropy(pf, y):.4f} "
                                f"acc={(pf.argmax(axis=1) == y).mean():.3f}")
                                return W1, b1, W2, b2


                            print("\n=== mini-batch SGD training ===")
                            W1, b1, W2, b2 = train(X, y, W1, b1, W2, b2)
                            pf, _ = forward(X, W1, b1, W2, b2)
                            print(f"final accuracy = {(pf.argmax(axis=1) == y).mean():.3f}")
```

实测输出（float64、$\epsilon=10^{-5}$）：`W1`/`b1`/`W2`/`b2` 的最大相对误差分别为 6.9e-09、2.8e-09、1.1e-08、1.1e-10，全部 `ok=True`；训练 300 个 epoch 后 loss 从 1.23 降到 0.02 左右、准确率 0.99 以上。几个值得对照上一节的点：

1. `dz2 = (p - Y) / n` 就是 $\boldsymbol{\delta}^{(L)}=\hat{\boldsymbol{y}}-\boldsymbol{y}$ 再除以 batch 大小（损失取 mean），漏掉 `/n` 是最经典的梯度错误；
2. `dW2 = a1.T @ dz2` 正是 $\nabla_{\boldsymbol{W}^{(l)}}=\boldsymbol{\delta}^{(l)}(\boldsymbol{a}^{(l-1)})^\top$ 的批量形式——把 $N$ 个样本的 $\boldsymbol{\delta}\boldsymbol{a}^\top$ 外积求和，写成矩阵乘就是 `a1.T @ dz2`；
3. `dz1 = da1 * (z1 > 0.0)` 对应 $f'(\boldsymbol{z}^{(l)})\odot\big((\boldsymbol{W}^{(l+1)})^\top\boldsymbol{\delta}^{(l+1)}\big)$：`da1 = dz2 @ W2.T` 算加权和，`* (z1 > 0)` 才是乘激活函数导数——**先加权求和、再逐元素乘 $f'$**，顺序弄反或忘乘，校验误差会到 $10^{-1}$ 量级；
4. 梯度校验用中心差分 $\frac{f(\theta+\epsilon)-f(\theta-\epsilon)}{2\epsilon}$（误差 $O(\epsilon^2)$，比前向差分精确得多），$\epsilon=10^{-5}$ 是实践中很好用的折中；更新时 `W1 -= lr * (dW1 + lam * W1)` 对应"正则化项只包含权重、不包含偏置"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-反向传播与梯度下降：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/01-基础与反向传播/03-反向传播与梯度下降.md)
