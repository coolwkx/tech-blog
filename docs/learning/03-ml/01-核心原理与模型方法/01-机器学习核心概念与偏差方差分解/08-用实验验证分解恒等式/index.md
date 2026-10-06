---
article_id: kp-d8dc9353578f3de1
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 7
learning_objective: 理解并验证：用实验验证分解恒等式
---

# 用实验验证分解恒等式

> **学习目标**：能够解释「用实验验证分解恒等式」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 深入机制

## 本次只学这一点

既然它恒等成立，我们就能**在同一点上重新采样 $y$** 估计左边，再与右边逐项相加对比。下面代码把 §3 的 `bias_variance` 扩展为同时给出经验期望误差与正则强度的版本：

```python
# 复用上面的 true_f / raw_design / fit_poly / predict / SIGMA

def decompose(degree, n, reps=300, grid=200, seed=0, lam=0.0):
    rng = np.random.default_rng(seed)
    xg = np.linspace(0.0, 1.0, grid)
    fg = true_f(xg)
    preds = np.empty((reps, grid))
    err = np.empty(reps)
    for r in range(reps):
        x = rng.uniform(0.0, 1.0, n)
        y = true_f(x) + rng.normal(0.0, SIGMA, n)
        w, mu, sd = fit_poly(x, y, degree, lam)
        preds[r] = predict(xg, w, mu, sd, degree)
        y_new = fg + rng.normal(0.0, SIGMA, grid) # 同一批 x 上重新采样一个 y
        err[r] = np.mean((y_new - preds[r]) ** 2) # 期望泛化误差的经验估计
        bias2 = np.mean((preds.mean(axis=0) - fg) ** 2)
        return bias2, np.mean(preds.var(axis=0)), err.mean

    header = f"{'degree':>6} | {'bias^2':>9} | {'variance':>9} | {'bias^2+var+noise':>16} | {'empirical EPE':>13}"
    print(header)
    print("-" * len(header))
    for d in (1, 2, 3, 5, 7, 9):
        b, v, e = decompose(d, n=30)
        print(f"{d:>6} | {b:>9.4f} | {v:>9.4f} | {b + v + SIGMA ** 2:>16.4f} | {e:>13.4f}")

        print("\n固定阶数，只改变训练样本量 n：")
        for d in (1, 9):
            for n in (20, 50, 200, 800):
                b, v, e = decompose(d, n)
                print(f" degree={d} n={n:>4} | bias^2={b:>8.4f} | variance={v:>9.4f} | test={e:>8.4f}")
```

实测输出：

```text
degree | bias^2 | variance | bias^2+var+noise | empirical EPE
-----------------------------------------------------------------
 1 | 0.1835 | 0.0229 | 0.2964 | 0.2968
 2 | 0.0328 | 0.0156 | 0.1384 | 0.1385
 3 | 0.0032 | 0.0161 | 0.1093 | 0.1090
 5 | 0.0003 | 0.0410 | 0.1313 | 0.1310
 7 | 0.0031 | 0.7238 | 0.8169 | 0.8186
 9 | 0.0733 | 37.9193 | 38.0826 | 38.0984
```

这张表同时验证两件事：**相加等于经验期望误差**（差值都在 $10^{-3}$ 量级的蒙特卡洛误差内），以及误差随容量呈 **U 型**——最低点在 3 阶（0.1093，已接近噪声地板 0.09 加残余偏差）。容量从 1 阶增到 3 阶买的是偏差下降（0.184 → 0.003，variance 几乎不变），从 5 阶增到 9 阶买到的却是方差失控（0.041 → 37.9）；并且阶数越高这两项估计越不稳（重尾），所以估方差时 `reps` 要够大，并换几个随机种子交叉验证。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用实验验证分解恒等式」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
