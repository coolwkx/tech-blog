---
article_id: kp-6bb68f23b38342d5
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-266564777403
learning_sourceId: '266564777403'
learning_order: 1
learning_objective: 理解并验证：监督学习的形式化
---

# 监督学习的形式化

> **学习目标**：能够解释「监督学习的形式化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：条件期望 $E[Y\mid X]$、方差、极大似然估计、矩阵最小二乘（正规方程）、训练/验证集切分与交叉验证。
>
> **所属主题**：机器学习核心概念与偏差方差分解 · 核心思想

## 本次只学这一点

设数据 $(x_i,y_i)\stackrel{\text{iid}}{\sim}P(X,Y)$，$P$ 未知且固定。回归的目标函数是条件均值 $f^\star(x)=E[Y\mid X=x]$（平方损失下的最优预测），分类的目标函数是条件概率 $\eta(x)=P(Y=1\mid X=x)$。我们用**假设空间** $\mathcal H=\{f_\theta:\theta\in\Theta\}$ 参数化候选模型，用**损失** $\ell(y,f(x))$ 度量单点误差，并定义：

$$R(f)=\mathbb E_{(X,Y)\sim P}\big[\ell(y,f(x))\big]\quad\text{(expected risk，期望风险)},\qquad
\hat R_n(f)=\frac{1}{n}\sum_{i=1}^{n}\ell\big(y_i,f(x_i)\big)\quad\text{(empirical risk，经验风险)}$$

**经验风险最小化（ERM）**：$\hat f=\arg\min_{f\in\mathcal H}\hat R_n(f)$；实际几乎总加正则项，$\hat f=\arg\min_{f\in\mathcal H}\big[\hat R_n(f)+\lambda\Omega(f)\big]$。$\hat R_n$ 是 $R$ 的无偏但高方差的估计（$n$ 个样本的均值），所以"训练误差小"与"期望风险小"是两件事。写严格就是泛化误差的两个来源：

$$R(\hat f)-R^\star=\underbrace{\big(R(f^\star_{\mathcal H})-R^\star\big)}_{\text{近似误差 approximation error}}+\underbrace{\big(R(\hat f)-R(f^\star_{\mathcal H})\big)}_{\text{估计误差 estimation error}}$$

其中 $R^\star=\inf_f R(f)$，$f^\star_{\mathcal H}=\arg\min_{f\in\mathcal H}R(f)$。近似误差只由假设空间决定（$\mathcal H$ 越大越小），估计误差由"用有限样本从 $\mathcal H$ 里挑一个"决定（$\mathcal H$ 越大、$n$ 越小则越大）。这与第 4 节的 bias-variance 是同一件事的两种说法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「监督学习的形式化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/01-机器学习核心概念与偏差方差分解.md)
