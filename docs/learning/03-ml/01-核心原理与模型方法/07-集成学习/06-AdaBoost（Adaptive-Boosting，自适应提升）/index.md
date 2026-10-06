---
article_id: kp-4158f71fa3c608f5
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 5
learning_objective: 理解并验证：AdaBoost（Adaptive Boosting，自适应提升）
---

# AdaBoost（Adaptive Boosting，自适应提升）

> **学习目标**：能够解释「AdaBoost（Adaptive Boosting，自适应提升）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 算法细节

## 本次只学这一点

**核心思想**：**通过逐步提高那些被前一步分类错误的样本的权重来训练一个强分类器。**

**算法流程（推导）**：
1. **初始化**：$n$ 个样本权重相等，$D_1(i)=1/n$（如 100 个样本则每个为 $1/100$）；
2. **训练第 $t$ 个弱学习器**：在当前样本权重分布 $D_t$ 下，找一个**加权错误率最小**的分裂点，得到 $h_t$；
3. **计算该学习器的加权错误率**：

$$\varepsilon_t = \sum_{i=1}^{n}D_t(i)\,\mathbb{1}\big[h_t(x_i)\ne y_i\big]$$

4. **计算该学习器的模型权重**：

$$\boxed{\alpha_t = \frac12\ln\frac{1-\varepsilon_t}{\varepsilon_t}}$$

5. **更新样本权重**（分对的样本权重降低，分错的样本权重升高）：

$$D_{t+1}(i) = \frac{D_t(i)}{Z_t}\times
\begin{cases}
e^{-\alpha_t}, & h_t(x_i)=y_i \quad(\text{分类正确})\\[4pt]
e^{+\alpha_t}, & h_t(x_i)\ne y_i \quad(\text{分类错误})
\end{cases}$$

 其中 $Z_t=\sum_i D_{t+1}^{\text{未归一}}(i)$ 是**归一化因子**（保证权重和为 1）。等价写法：

$$D_{t+1}(i) = \frac{D_t(i)\exp(-\alpha_t y_i h_t(x_i))}{Z_t}$$

6. **重复**直到训练出 $m$ 个弱学习器；
7. **最终强分类器（加权投票）**：

$$\boxed{H(x) = \operatorname{sign}\left(\sum_{t=1}^{m}\alpha_t h_t(x)\right)}$$

**注意**：$H(x)>0$ 归为正类，$<0$ 归为负类。

**$\alpha_t$ 的直觉**：
- $\varepsilon_t \to 0$（学习器很准）→ $\dfrac{1-\varepsilon}{\varepsilon}\to\infty$ → $\alpha_t$ 很大 → **话语权大**；
- $\varepsilon_t \to 0.5$（等于瞎猜）→ $\alpha_t \to 0$ → **话语权几乎为 0**；
- $\varepsilon_t > 0.5$（比瞎猜还差）→ $\alpha_t<0$ → 理论上投票时"反着听"。

**AdaBoost 的注意点**：
- 一般用于**二分类**（多分类需扩展），在视觉领域应用较多；
- 弱学习器**深度不宜过深**（通常只用决策树桩 `max_depth=1`），否则容易过拟合；
- `learning_rate` 作用于每棵树的**数据权重更新幅度**（相当于对 $\alpha_t$ 做收缩）。

#### 手算例（例，10 个样本）

**第 1 轮**：
- 初始化权重：每个样本 0.1
- 枚举分裂点 0.5~8.5，其中以 **2.5** 分裂时的**加权错误率最低**：错 3 个样本
- 错误率 $\varepsilon_1 = 3/10 = 0.3$
- 模型权重 $\alpha_1 = \tfrac12\ln\dfrac{1-0.3}{0.3} = \tfrac12\ln\dfrac{7}{3} = 0.4236$
- 权重变化系数：分对 $e^{-\alpha_1}=e^{-0.4236}=0.6547$；分错 $e^{+\alpha_1}=e^{0.4236}=1.5275$
- 未归一化权重：分对的 7 个样本 → $0.1\times0.6547=0.06547$；分错的 3 个样本 → $0.1\times1.5275=0.15275$
- 归一化因子 $Z_1 = 0.06547\times7+0.15275\times3 = 0.9165$
- 归一化后：分对样本 $0.06547/0.9165=0.07143$；分错样本 $0.15275/0.9165=0.1667$

**第 2 轮**（在第一轮权重下重算加权错误率）：
- 以 **8.5** 分裂时错误率最低：$\varepsilon_2 = 0.07143\times3 = 0.21429$
- 模型权重 $\alpha_2 = \tfrac12\ln\dfrac{1-0.21429}{0.21429} = 0.64963$
- 权重调整系数：分对 $0.5222$、分错 $1.9148$
- 归一化后：部分样本 0.0455、部分 0.1060、分错样本 0.1667

**第 3 轮**：错误率 0.1820，模型权重 $\alpha_3 = 0.7514$。

**最终强学习器**：$H(x)=\operatorname{sign}(0.4236h_1+0.64963h_2+0.7514h_3)$

> **观察**：随着轮次推进，$\alpha_t$ 越来越大（0.4236 → 0.6496 → 0.7514），说明后续学习器**越来越准**，AdaBoost 确实在"自适应"地变强。

#### AdaBoost 实证（葡萄酒数据）

```python
mytree = DecisionTreeClassifier(criterion='entropy', max_depth=1, random_state=0)
myada = AdaBoostClassifier(base_estimator=mytree, n_estimators=500,
learning_rate=0.1, random_state=0)
```

| 模型 | 训练集准确率 | 测试集准确率 |
| --- | --- | --- |
| 单棵决策树桩 | 0.845 | 0.854 |
| AdaBoost（500 棵树桩） | **1.0** | **0.875** |

**结论**：AdaBoost 显著提升了性能，但训练集准确率已经到 1.0 —— **开始有轻微过拟合迹象**，这也是 Boosting 类算法的通病。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「AdaBoost（Adaptive Boosting，自适应提升）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
