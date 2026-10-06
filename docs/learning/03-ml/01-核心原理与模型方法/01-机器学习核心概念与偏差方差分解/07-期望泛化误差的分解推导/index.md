---
article_id: kp-86f5bda931d6b5ef
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 6
learning_objective: 理解并验证：期望泛化误差的分解推导
---

# 期望泛化误差的分解推导

> **学习目标**：能够解释「期望泛化误差的分解推导」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 深入机制

## 本次只学这一点

设 $y=f(x)+\varepsilon$，$E[\varepsilon]=0$，$\mathrm{Var}(\varepsilon)=\sigma^2$，$\varepsilon$ 独立于 $x$ 与训练集 $D$，记训练集上学到的模型为 $\hat f_D$，$\bar f(x)=E_D[\hat f_D(x)]$。对同一个测试点 $x$ 的**全部随机性**取期望。

**第一步，分离噪声。** 展开 $(f+\varepsilon-\hat f_D)^2$，交叉项因 $\varepsilon\perp(D,x)$ 而消失：

$$E_{D,\varepsilon}\big[(y-\hat f_D(x))^2\big]=\underbrace{E_D\big[(f(x)-\hat f_D(x))^2\big]}_{\text{模型误差}}+\underbrace{\sigma^2}_{\text{Noise}}$$

**第二步，对模型误差加一项减一项。** 因 $f-\bar f$ 对 $D$ 是常数，再次展开后交叉项为零：

$$E_D\big[(f-\hat f_D)^2\big]=(f-\bar f)^2+E_D\big[(\bar f-\hat f_D)^2\big]+2(f-\bar f)\underbrace{E_D[\bar f-\hat f_D]}_{=0}$$

**第三步，合并并对 $x$ 取期望**，得到本章的核心恒等式：

$$\boxed{\;E_{x,y,D}\big[(y-\hat f_D(x))^2\big]=\underbrace{E_x\big[\big(E_D[\hat f_D(x)]-f(x)\big)^2\big]}_{\mathrm{Bias}^2}+\underbrace{E_x\big[\mathrm{Var}_D\big(\hat f_D(x)\big)\big]}_{\mathrm{Variance}}+\underbrace{\sigma^2}_{\mathrm{Noise}}\;}$$

- **Bias²（偏差平方）**：模型"平均预测"与真值之间的系统性偏离，衡量假设空间 $\mathcal H$ 能否表达 $f$。它与 $n$ 无关，只由模型族、特征、正则强度决定。
- **Variance（方差）**：不同训练集学到的模型之间的抖动，衡量模型对训练噪声的敏感度。线性回归下 $\mathrm{Var}[\hat f(x)]=\sigma^2x^\top(X^\top X)^{-1}x$，量级 $O(d_{\text{eff}}/n)$。
- **Noise（噪声）**：给定 $x$ 时 $y$ 的条件方差，是任何以 $x$ 为输入的预测器都无法消除的下界。严格说"不可约"是相对于当前特征集而言的：若能观测到更多与 $y$ 相关的协变量，条件方差会变小。

两点边界必须说清楚：(1) 该恒等式对**平方损失**严格成立，0-1 损失也有形式类似的分解，但 bias/variance 的定义不再唯一且需要额外处理最优贝叶斯误差项（Domingos, 2000）；(2) 推导用到"$\varepsilon$ 与 $D$ 独立"，即测试点与训练集同分布，**分布漂移**时等式失效，误差里会多出协变量偏移带来的偏差——这正是"离线指标好、线上差"的常见原因。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「期望泛化误差的分解推导」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
