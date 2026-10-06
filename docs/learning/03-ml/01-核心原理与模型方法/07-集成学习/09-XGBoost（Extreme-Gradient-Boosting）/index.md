---
article_id: kp-cff46a7a9f22ec56
learning_kind: article
learning_category: 03-ml
learning_direction: foundations
learning_topic: topic-95982a1c122f
learning_sourceId: 95982a1c122f
learning_order: 8
learning_objective: 理解并验证：XGBoost（Extreme Gradient Boosting）
---

# XGBoost（Extreme Gradient Boosting）

> **学习目标**：能够解释「XGBoost（Extreme Gradient Boosting）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：决策树的构建与剪枝（见 [05-决策树](../../../../../03-ml/02-经典算法/05-决策树.md)）、偏差-方差分解、梯度下降与泰勒展开的一阶/二阶形式（见 [03-线性回归](../../../../../03-ml/02-经典算法/03-线性回归.md)）。
>
> **所属主题**：集成学习 · 算法细节

## 本次只学这一点

**定位**：GBDT 的改进版，"集成学习方法的王牌"，在数据挖掘比赛中大部分获胜者都用了 XGBoost。核心改进有两点：
1. **在损失函数中加入正则化项**，降低模型复杂度、提高泛化性能；
2. 用**二阶泰勒展开**近似目标函数，从而得到解析的最优叶子权重与分裂增益。

**模型形式**（加法模型）：

$$\hat y_i = \sum_{k=1}^{K}f_k(x_i),\qquad f_k\in\mathcal{F}\ (\text{回归树空间})$$

**目标函数**：

$$\boxed{\ \text{Obj} = \sum_{i=1}^{n}L\big(y_i,\hat y_i\big) + \sum_{k=1}^{K}\Omega(f_k)\ }$$

其中第一项是**训练损失**，第二项是**所有弱学习器的复杂度之和**。单棵树的复杂度定义为

$$\Omega(f) = \gamma T + \frac12\lambda\|w\|^2$$

| 符号 | 含义 |
| --- | --- |
| $T$ | 该树的**叶子节点数量** |
| $w$ | 叶子节点**输出值组成的向量** |
| $\gamma$ | 对叶子节点数量的调节系数（相当于"分裂一次要付的成本"） |
| $\lambda$ | 对叶子权重的 L2 调节系数 |

**举例**：某棵树有 3 个叶子，输出 $\{2, 0.1, -1\}$，则 $\Omega = 3\gamma+\tfrac12\lambda(4+0.01+1)$。

#### 推导 1：二阶泰勒展开

**泰勒展开**：把一个函数在某一点处展开成无限项的多项式表达式。

- 一阶：$f(x+\Delta x)\approx f(x) + f'(x)\Delta x$
- 二阶：$f(x+\Delta x)\approx f(x) + f'(x)\Delta x + \frac12 f''(x)\Delta x^2$

**对第 $t$ 轮的目标函数展开。** 记 $\hat y_i^{(t)} = \hat y_i^{(t-1)} + f_t(x_i)$，则

$$
\begin{aligned}
\text{Obj}^{(t)} &= \sum_{i=1}^{n}L\big(y_i,\ \hat y_i^{(t-1)}+f_t(x_i)\big) + \sum_{k=1}^{t}\Omega(f_k)\\
&\approx \sum_{i=1}^{n}\left[L(y_i,\hat y_i^{(t-1)}) + g_i f_t(x_i) + \frac12 h_i f_t^2(x_i)\right] + \Omega(f_t) + \text{const}
\end{aligned}
$$

其中 $g_i$、$h_i$ 分别是损失函数对预测值的**一阶导**与**二阶导**：

$$g_i = \frac{\partial L(y_i,\hat y)}{\partial \hat y}\Big|_{\hat y=\hat y^{(t-1)}},\qquad
h_i = \frac{\partial^2 L(y_i,\hat y)}{\partial \hat y^2}\Big|_{\hat y=\hat y^{(t-1)}}$$

**去掉常数项**：$L(y_i,\hat y_i^{(t-1)})$ 与 $\sum_{k=1}^{t-1}\Omega(f_k)$ 都是**常数**——因为前 $t-1$ 个学习器都已经训练完了，值可以直接算出来，对"当前这棵树怎么长"没有影响。于是

$$\boxed{\ \text{Obj}^{(t)} \approx \sum_{i=1}^{n}\Big[g_i f_t(x_i) + \frac12 h_i f_t^2(x_i)\Big] + \gamma T + \frac12\lambda\sum_{j=1}^{T}w_j^2\ }$$

这个公式里**只剩 $f_t$**，含义是：**"当前这棵树怎么构建，才能最大程度降低损失。"**

**常见损失的 $g_i,h_i$**：

| 损失 | $L$ | $g_i$ | $h_i$ |
| --- | --- | --- | --- |
| 平方损失 | $\tfrac12(y-\hat y)^2$ | $\hat y - y$ | $1$ |
| 逻辑损失（二分类） | $-[y\ln p+(1-y)\ln(1-p)]$ | $p-y$ | $p(1-p)$ |

#### 推导 2：从样本角度转到叶子角度

上式中 $f_t(x_i)$ 是**样本角度**的表达（每个样本落在哪个叶子就取哪个叶子的 $w$），而 $T$、$\|w\|^2$ 是**叶子角度**的。为便于合并，统一切换到叶子视角：设叶子 $j$ 的样本集合为 $I_j=\{i\mid q(x_i)=j\}$，$w_j$ 是它的输出值。

**10 样本落 4 个叶子的例子**（原例）：D 结点 3 个、E 结点 2 个、F 结点 2 个、G 结点 3 个：

$$
\begin{aligned}
\text{D 节点：}& w_1g_{i1}+w_1g_{i2}+w_1g_{i3} = \Big(\sum_{i\in I_1}g_i\Big)w_1\\
\text{E 节点：}& w_2g_{i4}+w_2g_{i5} = \Big(\sum_{i\in I_2}g_i\Big)w_2\\
\text{F 节点：}& \Big(\sum_{i\in I_3}g_i\Big)w_3,\qquad \text{G 节点：}\Big(\sum_{i\in I_4}g_i\Big)w_4
\end{aligned}
$$

定义

$$G_j = \sum_{i\in I_j}g_i,\qquad H_j=\sum_{i\in I_j}h_i$$

（$G_j$ 是落在叶子 $j$ 上**所有样本一阶导之和**，$H_j$ 是**二阶导之和**。）于是目标函数变为

$$\boxed{\ \text{Obj}^{(t)} = \sum_{j=1}^{T}\left[G_j w_j + \frac12(H_j+\lambda)w_j^2\right] + \gamma T\ }$$

#### 推导 3：最优叶子权重与最优目标值

**对 $w_j$ 求导置零**（各叶子互相独立，可逐项求）：

$$\frac{\partial}{\partial w_j}\left[G_jw_j + \frac12(H_j+\lambda)w_j^2\right] = G_j + (H_j+\lambda)w_j = 0$$

$$\boxed{\ w_j^\star = -\frac{G_j}{H_j+\lambda}\ }$$

把 $w_j^\star$ 代回目标函数，得到**最优目标值（打分函数 scoring function）**：

$$\boxed{\ \text{Obj}^\star = -\frac12\sum_{j=1}^{T}\frac{G_j^2}{H_j+\lambda} + \gamma T\ }$$

**这个公式的用途**：它**从损失函数和树的复杂度两个角度衡量一棵树的优劣**。$\text{Obj}^\star$ 越小，这棵树越好。

#### 推导 4：分裂增益（选择划分点）

对某个叶子尝试分裂成左（$L$）、右（$R$）两部分，**分裂前的分数减去分裂后的分数**即为增益：

$$\boxed{\ \text{Gain} = \underbrace{\frac12\left[\frac{G_L^2}{H_L+\lambda}+\frac{G_R^2}{H_R+\lambda}-\frac{(G_L+G_R)^2}{H_L+H_R+\lambda}\right]}_{\text{分裂带来的损失下降}} - \underbrace{\gamma}_{\text{新增一个叶子的复杂度成本}}\ }$$

**决策规则**：
- $\text{Gain}>0$：分裂之后损失更小（收益大于 $\gamma$ 的成本），**考虑此次分裂**；
- $\text{Gain}<0$：分裂后分数更大（更差），**不建议分裂**。

**停止分裂的条件**：
1. 达到最大深度；
2. 叶子节点样本数低于某个阈值（`min_child_weight`）；
3. 所有结点的分裂都不能降低损失（$\text{Gain}\le0$）；
4. 增益小于 `gamma`；
5. 等等。

**XGBoost 相对 GBDT 的改进总结**：

| 改进点 | 说明 |
| --- | --- |
| 正则化项 | 目标函数显式包含 $\gamma T+\tfrac12\lambda\|w\|^2$，控制复杂度 |
| 二阶信息 | 用 $g_i,h_i$ 两个导数，收敛更快、更准 |
| 支持自定义损失 | 只要给出 $g,h$ 就能优化 |
| 分裂增益阈值 | `gamma` 直接控制"分裂是否划算" |
| 列采样 / 行采样 | `colsample_bytree`、`subsample`，进一步防过拟合 |
| 工程优化 | 预排序 + 近似分位点、稀疏感知、并行化、缓存优化 |

**sklearn 风格 API**：

```python
xgb.XGBClassifier(
n_estimators=100, # 树的数量
max_depth=6, # 树的最大深度
learning_rate=0.1, # 学习率（别名 eta）
objective='multi:softmax', # 多分类输出类别
eval_metric='merror', # 多分类错误率
gamma=0, # 分裂所需的最小损失下降
reg_lambda=1, # L2 正则系数（λ）
reg_alpha=0, # L1 正则系数
subsample=1, # 行采样比例
colsample_bytree=1, # 列采样比例
random_state=22,
)
```

| 方法/属性 | 含义 |
| --- | --- |
| `fit(X, y, sample_weight=...)` | 训练，可传样本权重处理不平衡 |
| `predict(X)` / `predict_proba(X)` | 预测类别 / 概率 |
| `feature_importances_` | 特征重要性 |
| `best_estimator_`（配合 GridSearchCV） | 最优模型 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/04-集成与无监督/06-集成学习.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「XGBoost（Extreme Gradient Boosting）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/04-集成与无监督/06-集成学习.md)
