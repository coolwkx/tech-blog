---
article_id: kp-f75f910f38c7648e
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 5
learning_objective: 理解并验证：机器学习核心概念与偏差方差分解：最小可运行示例
---

# 机器学习核心概念与偏差方差分解：最小可运行示例

> **学习目标**：能够解释「机器学习核心概念与偏差方差分解：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 最小可运行示例

## 本次只学这一点

下面代码把期望泛化误差真正测出来：对同一分布重复采样 200 个训练集，在每个训练集上拟合多项式回归，然后统计**平均预测**（算 Bias²）与**预测抖动**（算 Variance）。真实函数 $f(x)=\sin(1.5\pi x)$，$x\sim U(0,1)$，噪声 $\varepsilon\sim\mathcal N(0,0.3^2)$。**第 4 节的其余代码块都复用这段定义的函数，放在同一个脚本里即可依次运行。**

```python
import numpy as np

SIGMA = 0.3 # 噪声标准差，sigma^2 = 0.09 是不可约项

def true_f(x):
    return np.sin(1.5 * np.pi * x)

def raw_design(x, degree):
    """[1, z, z^2, ..., z^d]，z = 2x-1 把输入压到 [-1, 1] 以改善数值条件。"""
    z = 2.0 * np.asarray(x, float) - 1.0
    return np.column_stack([np.ones_like(z)] + [z ** k for k in range(1, degree + 1)])

def fit_poly(x, y, degree, lam=0.0):
    """列标准化后最小二乘；lam > 0 时是岭回归（不惩罚截距）。"""
    X = raw_design(x, degree)
    mu, sd = X.mean(axis=0), X.std(axis=0) # 标准化统计量只能来自训练集
    sd[sd < 1e-12] = 1.0
    mu[0], sd[0] = 0.0, 1.0
    Xs = (X - mu) / sd
    if lam == 0.0:
        w = np.linalg.lstsq(Xs, y, rcond=None)[0]
    else:
        P = lam * np.eye(Xs.shape[1])
        P[0, 0] = 0.0 # 不惩罚截距
        w = np.linalg.solve(Xs.T @ Xs + P, Xs.T @ y)
        return w, mu, sd

    def predict(x, w, mu, sd, degree): # 用训练集的 mu/sd 变换测试点
        return ((raw_design(x, degree) - mu) / sd) @ w

    def bias_variance(degree, n=30, reps=200, grid=200, seed=0):
        rng = np.random.default_rng(seed)
        xg = np.linspace(0.0, 1.0, grid) # 固定的评估网格
        fg = true_f(xg)
        preds = np.empty((reps, grid))
        for r in range(reps): # 重复采样 reps 个训练集 D
            x = rng.uniform(0.0, 1.0, n)
            y = true_f(x) + rng.normal(0.0, SIGMA, n) # 每个 D 都是同一分布的新抽样
            w, mu, sd = fit_poly(x, y, degree)
            preds[r] = predict(xg, w, mu, sd, degree)
            mean_pred = preds.mean(axis=0) # E_D[f_hat(x)] 的蒙特卡洛估计
            return np.mean((mean_pred - fg) ** 2), np.mean(preds.var(axis=0))

        for d in (1, 9):
            b, v = bias_variance(d)
            print(f"degree={d}: bias^2={b:.4f} variance={v:.4f} "
            f"bias^2+var+sigma^2={b + v + SIGMA ** 2:.4f}")
```

实测输出（numpy 2.x，无其他依赖）：

```text
degree=1: bias^2=0.1838 variance=0.0235 bias^2+var+sigma^2=0.2973
degree=9: bias^2=0.0017 variance=8.4640 bias^2+var+sigma^2=8.5557
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `SIGMA = 0.3` | 定义不可约噪声的标准差 | $\sigma^2=0.09$ 是误差下界，任何模型都压不到它下面 |
| `raw_design` | 构造 $[1,z,z^2,\dots,z^d]$ 多项式基 | 直接用 $x\in[0,1]$ 的幂次会让高阶设计矩阵条件数爆炸；$z=2x-1$ 只改善数值，不改变模型族 |
| `mu, sd = X.mean(0), X.std(0)` | 列标准化，弱化共线性 | **必须用训练集统计量去变换验证/测试集**，否则等于信息泄漏 |
| `np.linalg.lstsq` | 数值稳定的最小二乘（MSE 的解析解） | 不要写 `inv(X.T @ X) @ X.T @ y`，病态矩阵会放大误差 |
| `P[0, 0] = 0.0` | 岭回归不惩罚截距 | 惩罚截距等于把预测整体拉向 0，会凭空制造偏差 |
| `preds[r] = ...` | 保存第 $r$ 个训练集的整条预测曲线 | 关键是**每个训练集都换一批噪声**，只换特征不换噪声测不出 variance |
| `preds.var(axis=0)` | 蒙特卡洛估计 $\mathrm{Var}_D[\hat f(x)]$ | 用默认的 `ddof=0` 与理论分解一致；1 阶 bias² 主导（0.184 ≫ 0.024）、9 阶 variance 主导（8.46 ≫ 0.002） |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「机器学习核心概念与偏差方差分解：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
