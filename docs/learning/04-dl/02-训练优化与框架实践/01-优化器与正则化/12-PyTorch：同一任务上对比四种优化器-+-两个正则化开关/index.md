---
article_id: kp-79bad2c44eb66017
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-4c30cd2983ea
learning_sourceId: 4c30cd2983ea
learning_order: 11
learning_objective: 理解并验证：PyTorch：同一任务上对比四种优化器 + 两个正则化开关
---

# PyTorch：同一任务上对比四种优化器 + 两个正则化开关

> **学习目标**：能够解释「PyTorch：同一任务上对比四种优化器 + 两个正则化开关」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：梯度下降与反向传播、链式法则、Hessian 矩阵与半正定、期望与方差、Softmax 与交叉熵、PyTorch 的 `nn.Module` / `optim` / `scheduler` 基本用法。
>
> **所属主题**：-优化器与正则化 · 可运行示例

## 本次只学这一点

在同一个二维二分类任务（两轮交错半月形，噪声 0.35，800 训练 / 800 验证 / 两层 256 宽 MLP）上分别跑 SGD / Momentum / RMSprop / Adam，并对 Adam 开关 Dropout 与 weight decay。为保证可比性：固定种子、**先打散再切分**、只用训练集统计量标准化、统一余弦衰减与梯度截断。

```python
"""优化器与正则化对比。依赖 torch / numpy / matplotlib，CPU 约 2 分钟。
实测(150 epoch, torch 2.x) val_loss：SGD .2803 / Momentum .2815 / RMSprop .3150 / Adam .3163；
Adam 加 dropout=0.3 后 .2954（明显更好）；weight_decay=1e-2 几乎无变化（系数偏小，可试 1e-1）。"""
import numpy as np, torch, torch.nn as nn
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt # 无显示器也能存图

torch.manual_seed(0)
rng, n = np.random.default_rng(0), 800
t1, t2 = rng.uniform(0, np.pi, n), rng.uniform(0, np.pi, n)
X = np.concatenate([np.stack([np.cos(t1), np.sin(t1)], 1), # 上半圆
np.stack([1 - np.cos(t2), .5 - np.sin(t2)], 1)]) # 下半圆
X = torch.tensor(X + rng.normal(0, .35, X.shape), dtype=torch.float32)
Y = torch.tensor(np.concatenate([np.zeros(n), np.ones(n)]), dtype=torch.long)
p = torch.randperm(len(X), generator=torch.Generator.manual_seed(1))
X, Y = X[p], Y[p] # 必须先打散，否则切出的训练集只有一类
Xtr, Ytr, Xva, Yva = X[:800], Y[:800], X[800:], Y[800:]
mu, sd = Xtr.mean(0, keepdim=True), Xtr.std(0, keepdim=True) # 只用训练集统计量
Xtr, Xva = (Xtr - mu) / sd, (Xva - mu) / sd

class MLP(nn.Module):
    def __init__(self, p_drop=0., hidden=256):
        super.__init__
        self.f = nn.Sequential(nn.Linear(2, hidden), nn.ReLU, nn.Dropout(p_drop),
        nn.Linear(hidden, hidden), nn.ReLU, nn.Dropout(p_drop),
        nn.Linear(hidden, 2)) # 输出 logits，配 CrossEntropyLoss
        def forward(self, x):
            return self.f(x)

        LR = {"SGD": .1, "Momentum": .02, "RMSprop": .002, "Adam": .003}

        def build(name, model, wd):
            """权重衰减只作用在权重矩阵上，偏置不衰减（常规做法）。"""
            dec = [q for k, q in model.named_parameters if not k.endswith("bias")]
            nod = [q for k, q in model.named_parameters if k.endswith("bias")]
            g = [{"params": dec, "weight_decay": wd}, {"params": nod, "weight_decay": 0.}]
            if name == "SGD": return torch.optim.SGD(g, lr=LR[name])
            if name == "Momentum": return torch.optim.SGD(g, lr=LR[name], momentum=.9, nesterov=True)
            if name == "RMSprop": return torch.optim.RMSprop(g, lr=LR[name], alpha=.99) # α=平方梯度衰减率
            return torch.optim.AdamW(g, lr=LR[name], betas=(.9, .999), eps=1e-8) # AdamW=解耦权重衰减

        def run(name, p_drop=0., wd=0., epochs=150, bs=64):
            torch.manual_seed(0) # 各次运行初始化一致，对比才公平
            model, crit = MLP(p_drop), nn.CrossEntropyLoss
            opt = build(name, model, wd)
            sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
            gen, hist = torch.Generator.manual_seed(0), {"train": [], "val": []}
            for _ in range(epochs):
                model.train # 开启 Dropout 的训练行为
                perm, tot, cnt = torch.randperm(len(Xtr), generator=gen), 0., 0
                for i in range(0, len(Xtr), bs):
                    idx = perm[i:i + bs]
                    opt.zero_grad(set_to_none=True)
                    loss = crit(model(Xtr[idx]), Ytr[idx])
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 5.) # 必须在 step 之前
                    opt.step; tot += loss.item * len(idx); cnt += len(idx)
                    sch.step
                    model.eval # 关 Dropout；BN 改用移动平均统计量
                    with torch.no_grad:
                        hist["train"].append(tot / cnt)
                        hist["val"].append(crit(model(Xva), Yva).item)
                        model.eval
                        with torch.no_grad:
                            acc = (model(Xva).argmax(1) == Yva).float.mean.item
                            return hist, acc

                        fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
                        for name in ["SGD", "Momentum", "RMSprop", "Adam"]:
                            h, acc = run(name)
                            print(f"{name:9s} val_loss={h['val'][-1]:.4f} val_acc={acc:.4f}")
                            ax[0].plot(h["val"], label=name); ax[0].plot(h["train"], ls=":", lw=1) # 点线=训练
                            for lab, p_drop, wd in [("none", 0., 0.), ("dropout .3", .3, 0.),
                            ("wd 1e-2", 0., 1e-2), ("dropout+wd", .3, 1e-2)]:
                                h, acc = run("Adam", p_drop, wd)
                                print(f"{lab:12s} val_loss={h['val'][-1]:.4f} val_acc={acc:.4f}")
                                ax[1].plot(h["val"], label=lab)
                                for a, t in zip(ax, ["optimizers", "regularization"]):
                                    a.set_xlabel("epoch"); a.set_ylabel("loss"); a.legend(fontsize=8); a.set_title(t)
                                    fig.tight_layout; fig.savefig("optimizer_regularization.png", dpi=120)
```

图里能看到两件事：左图中 **Adam/RMSprop 前期下降最快**（自适应学习率 + 动量），SGD 配余弦衰减在后期追上来且验证损失更低；右图中**加 Dropout 后验证损失明显更低**，同时训练损失变高——训练损失升高正是正则化在起作用的信号。而 `weight_decay=1e-2` 在这个规模下几乎看不出差别，说明**正则系数要跟着模型容量与数据量调**，通常在对数尺度上试 $10^{-4}\sim10^{-1}$。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「PyTorch：同一任务上对比四种优化器 + 两个正则化开关」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/04-优化器与正则化.md)
