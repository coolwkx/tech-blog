# KMeans 聚类

> **一句话总结**：KMeans 是**无监督学习**中最常用的划分式聚类算法——先随机选 $K$ 个质心，然后"**把每个样本分给最近的质心 → 把每个质心移到本簇样本的均值处**"反复交替，直到质心不再移动；$K$ 值靠**肘部法（SSE 拐点）**、**轮廓系数 SC** 或 **CH 指数**确定。
> **前置知识**：欧氏距离与标准化（见 [02-KNN算法](../02-经典算法/02-KNN算法.md)）、`make_blobs` 造数据、pandas 与 matplotlib 基础。
> **学完能做到**：
> 1. 手算一轮 KMeans 的"分配 + 更新质心"，并解释为什么算法一定会收敛；
> 2. 用 SSE、轮廓系数、CH 指数三种指标为一份数据选出合理的 $K$，说清三者各自的关注点；
> 3. 独立完成顾客数据聚类分析，并指出 KMeans 的局限（需预设 $K$、对初值与异常值敏感、只适合凸形簇）。

---

## 1. 核心思想

### 1.1 聚类是什么

**聚类（Clustering）** 是一种典型的**无监督学习算法**，主要用于**将相似的样本自动归到一个类别中**。

| 对比项 | 聚类（Clustering） | 分类（Classification） |
| --- | --- | --- |
| 学习类型 | 无监督 | 有监督 |
| 是否需要标签 | **不需要** | 需要 |
| 目标 | 发现数据内部的**结构与模式** | 预测已知的类别 |
| 结果评估 | 无标准答案，需内部指标或业务验证 | 有客观的对错，可用准确率/F1 |
| 相似性 | 欧式距离等，**不同准则产生不同结果** | 由标签定义 |

> **原话**：聚类算法的目的是**在没有先验知识的情况下，自动发现数据集中的内在结构和模式**；"使用不同的聚类准则，产生的聚类结果不同"。

### 1.2 生活化引入：动物怎么分类

同一批动物，按**繁衍方式**（胎生 / 卵生）分是一种结果；按**呼吸方式**（肺 / 腮）分是另一种；按**生活环境**（陆地 / 两栖 / 水中）分又是第三种。**划分依据（聚类准则）不同，聚类结果就不同。**

### 1.3 应用场景

| 领域 | 具体应用 |
| --- | --- |
| 用户运营 | 用户画像、广告推荐、Data Segmentation（客户分群） |
| 搜索引擎 | 流量推荐、新闻聚类与筛选排序、恶意流量识别 |
| 位置服务 | 基于位置信息的商业推送 |
| 图像与识别 | 图像分割、降维、识别 |
| 风控 | 离群点检测、信用卡异常消费 |
| 生物信息 | 发掘相同功能的基因片段 |

### 1.4 聚类算法的分类

**（1）按聚类颗粒度**：粗聚类（簇数少、每簇跨度大）、细聚类（簇数多、每簇更紧凑）。

**（2）按实现方法**

| 算法 | 依据 | 特点 |
| --- | --- | --- |
| **K-means** | 按**质心**划分 | 通用、普遍，需预设 $K$ |
| 层次聚类 | 对数据逐层划分，直到达到指定类别数 | 不需要预设 $K$，可得到树状图 |
| DBSCAN | 基于**密度** | 能发现任意形状的簇、能识别噪声，不需预设 $K$ |
| 谱聚类 | 基于**图论** | 适合非凸簇，计算量较大 |

### 1.5 三种评估指标总览

| 指标 | 关注点 | 方向 | 是否需要标签 | 关键性质 |
| --- | --- | --- | --- | --- |
| **SSE**（误差平方和，`inertia_`） | 只关注**簇内聚程度** | **越小越好** | 否 | 随 $K$ 增大单调下降，不能单独用于选 $K$ |
| **SC**（轮廓系数） | 簇内聚 + 簇间分离 | **越大越好**，$[-1,1]$ | 否 | 每个样本都能得到一个轮廓值，可做可视化 |
| **CH**（Calinski-Harabasz 指数） | 簇内聚 + 簇间分离 + **质心个数** | **越大越好** | 否 | 追求"用尽量少的类别聚类尽量多的样本" |
| **肘部法** | SSE 曲线的拐点 | 拐点处取 $K$ | 否 | 不是独立指标，而是用 SSE 选 $K$ 的方法 |

---

## 2. 算法细节

### 2.1 KMeans 的优化目标

给定样本集 $\{x_1,\dots,x_n\}$ 与簇数 $K$，KMeans 要最小化**簇内平方误差和（SSE / inertia）**：

$$\boxed{\ J = \sum_{k=1}^{K}\sum_{x\in C_k}\|x - \mu_k\|_2^2\ },\qquad \mu_k = \frac{1}{|C_k|}\sum_{x\in C_k}x$$

这是一个**NP-hard** 的组合优化问题（要枚举所有划分），所以 KMeans 用**交替迭代**求局部最优。

### 2.2 算法流程（4 步 + 收敛判据）

| 步骤 | 操作 |
| --- | --- |
| 1 | 事先确定常数 $K$（最终聚类类别数） |
| 2 | **随机选择 $K$ 个样本点**作为初始聚类中心 |
| 3 | 计算每个样本到 $K$ 个中心的距离，**选择最近的聚类中心**作为标记类别（Assign） |
| 4 | 根据每个类别中的样本点，**重新计算新的聚类中心（平均值）**（Update）；如果新中心与原中心一样则停止，否则回到第 3 步 |

**为什么"取均值"是最优的质心？** 固定簇内样本集合 $C_k$，最小化 $\sum_{x\in C_k}\|x-\mu\|^2$ 对 $\mu$ 求导置零：

$$\frac{\partial}{\partial\mu}\sum_{x\in C_k}(x-\mu)^2 = -2\sum_{x\in C_k}(x-\mu) = 0
\ \Longrightarrow\ \mu_k = \frac{1}{|C_k|}\sum_{x\in C_k}x = \bar x_k$$

**为什么算法一定会停？** KMeans 的两个步骤都是"**不增加 $J$**"的操作：
- **Assign 步**：把每个点分给它最近的质心，$J$ 不增（每点独立的最小化）；
- **Update 步**：把质心移到簇均值，$J$ 不增（上面已证）。

$J$ 单调不增且有下界 0，而簇划分的取值只有**有限种**，因此**不可能无限循环**，算法必然在有限步内收敛。**注意：收敛到的是局部最优，不是全局最优**——这就是 KMeans 对初始质心敏感的原因。

### 2.3 手算例（$K=2$，10 个二维点）

| 编号 | A | B | C | D | E | F | G | H | I | J |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $x_1$ | 1 | 3 | 2 | 8 | 9 | 10 | 8 | 6 | 2 | 9 |
| $x_2$ | 1 | 3 | 3 | 7 | 8 | 8 | 7 | 6 | 2 | 1 |

**第 1 步：随机选 $K=2$ 个初始中心**，示例取 $P_1=A(1,1)$、$P_2=B(3,3)$。

**第 2 步：分配（Assign）。**

| 点 | 到 $P_1(1,1)$ | 到 $P_2(3,3)$ | 归属 |
| --- | --- | --- | --- |
| A(1,1) | 0 | 2.83 | 簇1 |
| B(3,3) | 2.83 | 0 | 簇2 |
| C(2,3) | 2.24 | **1.41** | 簇2 |
| D(8,7) | 9.22 | **6.40** | 簇2 |
| E(9,8) | 10.63 | **7.81** | 簇2 |
| F(10,8) | 11.40 | **8.60** | 簇2 |
| G(8,7) | 9.22 | **6.40** | 簇2 |
| H(6,6) | 7.07 | **4.24** | 簇2 |
| I(2,2) | 1.41 | 1.41 | 平局（课例归簇1） |
| J(9,1) | 8.00 | **6.32** | 簇2 |

→ 簇1 $=\{A, I\}$，簇2 $=\{B,C,D,E,F,G,H,J\}$。

**第 3 步：更新质心（Update）。**

$$P_1' = \Big(\frac{1+2}{2},\ \frac{1+2}{2}\Big) = (1.5,\ 1.5)$$

$$P_2' = \Big(\frac{55}{8},\ \frac{43}{8}\Big) = (6.875,\ 5.375)$$

> 学习笔记提到的 "$P_2'=(2.3,3.3)$" 属于**分步演示中的中间结果**（在只归入少数点、尚未完整分类时算出的质心），完整一轮后的正确结果是 $(6.875, 5.375)$。关键是掌握"**新质心 = 本簇样本坐标的算术平均**"。

**第 4 步：判断收敛。** $P_1'\ne P_1$、$P_2'\ne P_2$，因此回到第 2 步重新分配。反复迭代，直到某一次迭代中**所有样本的归属不再变化**，算法结束。结论：**"当每次迭代结果不变时，认为算法收敛，聚类完成。K-Means 一定会停下，不可能陷入一直选质心的过程。"**

**标准流程排序（选择题）**：**D → B → A → E → C**

1. **D**：随机初始化 $K$ 个中心点；
2. **B**：计算未知样本点分别到这 $K$ 个中心点的距离 $D$；
3. **A**：将该样本点归类为与 $D$ 值最小时的中心点相同的类别；
4. **E**：计算这 $K$ 个分类簇的均值分别作为 $K$ 个簇新的中心点；
5. **C**：重复上述过程，直至新的中心点与旧的中心点一致，则迭代停止。

### 2.4 SSE 与肘部法

**SSE（The Sum of Squares due to Error，误差平方和）**：

$$\text{SSE} = \sum_{i=1}^{K}\sum_{p\in C_i}\|p - m_i\|^2$$

| 符号 | 含义 |
| --- | --- |
| $C_i$ | 第 $i$ 个簇 |
| $K$ | 聚类中心（质心）的个数 |
| $p$ | 某个簇内的样本 |
| $m_i$ | 该簇的**质心** |

**SSE 越小，表示数据点越接近它们的中心，聚类效果越好。** sklearn 中通过 `KMeans.inertia_` 获取。

**肘部法（Elbow Method）确定 $K$**：
1. 对 $n$ 个点的数据集，迭代计算 $k=1,2,\dots,n$，每次聚类完成后计算 SSE；
2. SSE 会**逐渐变小**（极限情况是 $k=n$ 时每个点自成一簇，SSE $=0$）；
3. SSE 下降过程中会出现一个**拐点**，**下降率突然变缓时即认为是最佳的 `n_clusters` 值**；
4. 直觉：增加簇数带来的"回报"明显减少时，就该停止增加类别。

**实验（1000 个样本、4 个真实簇）**：把 $k$ 从 1 遍历到 99 画 SSE 曲线，可以观察到 **$k=4$ 时 SSE 开始下降趋缓**，因此最佳值为 4。

### 2.5 轮廓系数 SC（Silhouette Coefficient）

**结合簇内的内聚程度（Cohesion）与簇间的分离程度（Separation）**。

**单样本 $i$ 的计算过程**：
1. $a_i$：样本 $i$ 到**同簇内其他样本**的平均距离。$a_i$ 越小，簇内相似度越大；
2. $b_i$：样本 $i$ 到**最近的那个其他簇 $j$** 内所有样本的平均距离。$b_i$ 越大，说明样本越不属于其他簇；
3. 该样本的轮廓系数：

$$s_i = \frac{b_i - a_i}{\max(a_i,\ b_i)}$$

4. 全体样本的轮廓系数取平均：$\text{SC} = \dfrac1n\sum_i s_i$。

| $s_i$ 取值 | 含义 |
| --- | --- |
| 接近 **1** | 簇内很紧、离其他簇很远，**聚类效果很好** |
| 接近 **0** | 处在两个簇的边界上 |
| 接近 **−1** | 可能被分错了簇 |

**范围 $[-1, 1]$，值越大聚类效果越好。** 注意 **SC 要求簇数 ≥ 2**（只有 1 个簇时无法计算簇间距离）。

**实验**：把 $k$ 从 2 遍历到 99 计算 SC，观察到 **$k=4$ 时取到最大值**，与肘部法结论一致。

### 2.6 CH 指数（Calinski-Harabasz Index）

$$\text{CH}(k) = \frac{\text{SSB}/(k-1)}{\text{SSW}/(n-k)}$$

| 符号 | 含义 | 方向 |
| --- | --- | --- |
| **SSW** | 簇内距离平方和（相当于 SSE），即每个样本点到其质心的距离的累加 | **越小越好** |
| **SSB** | 簇间距离平方和：各质心与"全体质心中心点"之间距离的加权和（权重为该簇样本数 $n_j$） | **越大越好** |
| $n$ | 样本数量 | —— |
| $k$ | 质心（类别）个数 | —— |

**CH 要达到的目的**：**用尽量少的类别聚类尽量多的样本，同时获得较好的聚类效果。** $k$ 增大时，分子 $\text{SSB}/(k-1)$ 会因为 $k$ 太大而下降，从而**自动惩罚过多的类别数**。

**方向：分数越高聚类效果越好。** 实验同样在 $k=4$ 时取到最大值。

### 2.7 三个指标的对比与选用

| 维度 | SSE | SC | CH |
| --- | --- | --- | --- |
| 关注 | 簇内聚 | 簇内聚 + 簇间离 | 簇内聚 + 簇间离 + 质心个数 |
| 方向 | 越小越好 | 越大越好（$[-1,1]$） | 越大越好 |
| 能否直接选 $K$ | **不能**（$K$ 越大 SSE 越小，需配肘部法） | **能** | **能** |
| 计算成本 | 最低 | 高（需两两距离） | 中 |

**工程实践建议**：
1. 先用 **肘部法 + SC + CH 三条曲线**交叉验证，若三者都指向同一个 $K$，可信度高；
2. 再用**业务可解释性**做最后裁决；
3. 聚类前**必须标准化**，否则大量纲特征会独占欧氏距离。

### 2.8 API 与参数

```python
sklearn.cluster.KMeans(
 n_clusters=8, # 簇数 K（默认 8）
 init='k-means++', # 初始化方式：'k-means++' 比 'random' 更稳
 n_init=10, # 用不同初始中心跑几次，取 SSE 最小的那次
 max_iter=300, # 单次运行的最大迭代次数
 tol=1e-4, # 收敛阈值
 random_state=None,
)
```

| 成员 | 含义 |
| --- | --- |
| `fit(X)` / `predict(X)` | 计算聚类中心 / 预测每个样本属于哪个簇 |
| `fit_predict(X)` | 先 `fit` 再 `predict`，一步到位 |
| `inertia_` | **SSE 值** |
| `cluster_centers_` | 各质心的坐标，形状 `(n_clusters, n_features)` |
| `labels_` | 每个样本的簇标签 |

| 评估 API | 方向 |
| --- | --- |
| `silhouette_score(X, labels)` | 越大越好 |
| `calinski_harabasz_score(X, labels)` | 越大越好 |
| `KMeans(...).inertia_` | 越小越好（需配合肘部法） |

> **历史坑**：早期 API 名是 `calinski_harabaz_score`（少了一个 `s`），已被废弃；现在必须用 `calinski_harabasz_score`。同理 `sklearn.datasets.samples_generator` 已废弃，应改为 `sklearn.datasets`。

---

## 3. 可运行示例

### 3.1 手算一轮 KMeans（验证 2.3 的计算）

```python
# -*- coding: utf-8 -*-
"""手算一轮 KMeans：分配 -> 更新质心 -> 判断是否收敛"""
import numpy as np

X = np.array([[1, 1], [3, 3], [2, 3], [8, 7], [9, 8],
[10, 8], [8, 7], [6, 6], [2, 2], [9, 1]], dtype=float)
names = list("ABCDEFGHIJ")

centers = np.array([[1, 1], [3, 3]], dtype=float) # P1=A, P2=B


def assign(X, centers):
    """返回每个点到各中心的距离矩阵与归属标签"""
    d = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
    return d, d.argmin(axis=1)


for it in range(1, 8):
    d, labels = assign(X, centers)
    print(f"\n===== 第 {it} 轮 =====")
    for nm, xi, di, lb in zip(names, X, d, labels):
        print(f" {nm}{tuple(xi)}: 到P1={di[0]:6.2f} 到P2={di[1]:6.2f} -> 簇{lb + 1}")

        new_centers = np.array([X[labels == k].mean(axis=0) for k in range(2)])
        sse = sum(((X[labels == k] - new_centers[k]) ** 2).sum() for k in range(2))
        print(" 新质心:", new_centers.round(4).tolist(), " SSE =", round(sse, 4))

        if np.allclose(new_centers, centers):
            print(" >>> 质心不再移动，算法收敛！")
            break
        centers = new_centers

        # 期望第 1 轮：簇1={A,I}，新质心 (1.5,1.5)；
        # 簇2={B,C,D,E,F,G,H,J}，新质心 (6.875,5.375)
```

### 3.2 SSE + 肘部法 + SC + CH 三指标选 $K$

```python
# -*- coding: utf-8 -*-
"""用三种指标共同确定最佳 K"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import calinski_harabasz_score, silhouette_score

# 1. 造数据：1000 样本、2 特征、4 个真实簇
x, y = make_blobs(n_samples=1000, n_features=2,
 centers=[[-1, -1], [0, 0], [1, 1], [2, 2]],
 cluster_std=[0.4, 0.2, 0.2, 0.2], random_state=22)

plt.figure(figsize=(6, 5))
plt.scatter(x[:, 0], x[:, 1], marker="o", s=10)
plt.title("原始数据（无标签）")
plt.show()

ks = list(range(2, 11))
sse_list, sc_list, ch_list = [], [], []

for k in ks:
 km = KMeans(n_clusters=k, n_init=10, max_iter=100, random_state=0)
 labels = km.fit_predict(x)
 sse_list.append(km.inertia_)
 sc_list.append(silhouette_score(x, labels))
 ch_list.append(calinski_harabasz_score(x, labels))

# ---- SSE 肘部法（k 从 1 开始更能看出拐点）----
sse_all = []
for k in range(1, 11):
 sse_all.append(KMeans(n_clusters=k, n_init=10, random_state=0).fit(x).inertia_)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
axes[0].plot(range(1, 11), sse_all, "or-")
axes[0].set_title("肘部法：SSE vs K")
axes[0].set_xlabel("K")
axes[0].set_ylabel("SSE")
axes[0].grid(True)

axes[1].plot(ks, sc_list, "ob-")
axes[1].set_title("轮廓系数 SC vs K（越大越好）")
axes[1].set_xlabel("K")
axes[1].set_ylabel("SC")
axes[1].grid(True)

axes[2].plot(ks, ch_list, "og-")
axes[2].set_title("CH 指数 vs K（越大越好）")
axes[2].set_xlabel("K")
axes[2].set_ylabel("CH")
axes[2].grid(True)
plt.tight_layout()
plt.show()

print("最佳 K（SC 最大）:", ks[int(np.argmax(sc_list))])
print("最佳 K（CH 最大）:", ks[int(np.argmax(ch_list))])
# 三个指标通常一致指向 K=4，与造数据时的 4 个真实中心吻合
```

### 3.3 顾客数据聚类分析（案例）

```python
# -*- coding: utf-8 -*-
"""顾客数据聚类：找到"收入高 + 消费高"的大宗商品客户群"""
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

CSV = "customers.csv"


def main():
    dataset = pd.read_csv(CSV)
    dataset.columns = ["CustomerID", "Gender", "Age", "Annual Income", "Spending Score"]
    print(dataset.info())

    # 只取"年收入"与"消费指数"两个特征做二维可视化聚类
    X = dataset.iloc[:, [3, 4]]
    print(X.head())

    # ---- 第一步：用肘部法 + 轮廓系数确定 K ----
    mysse, mysscore = [], []
    for i in range(2, 11):
        mykmeans = KMeans(n_clusters=i, n_init=10, random_state=0)
        mykmeans.fit(X)
        mysse.append(mykmeans.inertia_)
        mysscore.append(silhouette_score(X, mykmeans.predict(X)))

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].plot(range(2, 11), mysse)
        axes[0].set_title("the elbow method")
        axes[0].set_xlabel("number of clusters")
        axes[0].set_ylabel("SSE")
        axes[0].grid(True)

        axes[1].plot(range(2, 11), mysscore)
        axes[1].set_title("silhouette score")
        axes[1].grid(True)
        plt.show()
        # 结论：肘部法与轮廓系数都显示"聚成 5 类效果最好"

        # ---- 第二步：用 K=5 聚类并可视化 ----
        mykmeans = KMeans(n_clusters=5, n_init=10, random_state=0)
        y_kmeans = mykmeans.fit_predict(X)

        plt.figure(figsize=(10, 7))
        colors = ["red", "blue", "green", "cyan", "magenta"]
        labels = ["Standard", "Traditional", "Normal", "Youth", "TA"]
        for c in range(5):
            plt.scatter(X.values()[y_kmeans == c, 0], X.values()[y_kmeans == c, 1],
            s=100, c=colors[c], label=labels[c])
            plt.scatter(mykmeans.cluster_centers_[:, 0], mykmeans.cluster_centers_[:, 1],
            s=300, c="black", label="Centroids", marker="X")
            plt.title("Clusters of customers")
            plt.xlabel("Annual Income (k$)")
            plt.ylabel("Spending Score (1-100)")
            plt.legend()
            plt.show()

            # ---- 第三步：业务解读 ----
            result = X.copy()
            result["cluster"] = y_kmeans
            print(result.groupby("cluster").mean())
            # 右上角那一簇 = 收入高 + 消费高 => 大宗商品客户群；左下角 = 低收入低消费


            if __name__ == "__main__":
                main()
```

### 3.4 演示"不标准化会造成什么后果"

```python
# -*- coding: utf-8 -*-
"""KMeans 之前不标准化：聚类被大量纲特征单独支配"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
A = np.concatenate([rng.normal(0, 1, 100), rng.normal(1000, 1, 100)])
B = np.concatenate([rng.normal(0, 1, 100), rng.normal(0, 1, 100)])
X = np.c_[A, B]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
lab_raw = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
axes[0].scatter(A, B, c=lab_raw, s=20)
axes[0].set_title("不标准化：聚类只被大量纲特征 A 支配")

Xs = StandardScaler().fit_transform(X)
lab_std = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(Xs)
axes[1].scatter(A, B, c=lab_std, s=20)
axes[1].set_title("标准化后：两个特征共同影响聚类")
plt.show()
```

---

## 4. 常见坑

| # | 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- | --- |
| 1 | 不做标准化直接聚类 | 结果只反映量纲最大的特征 | 欧氏距离被大量纲特征支配 | 先 `StandardScaler` |
| 2 | 用 SSE 单独选 $K$ | 永远选到最大的 $K$ | SSE 随 $K$ 单调下降，$K=n$ 时为 0 | 用**肘部法看拐点**，或改用 SC/CH |
| 3 | `n_clusters` 取 1 却算 SC | `ValueError` | 轮廓系数需要簇间距离，至少 2 个簇 | 循环从 `range(2, ...)` 开始 |
| 4 | 不设 `random_state`/`n_init` | 每次结果不同、结果偏差 | KMeans 对初始质心敏感，易陷局部最优 | 固定 `random_state`，用 `init='k-means++'` + `n_init=10` |
| 5 | 把簇标签当成"真实类别" | 报告结论错误 | 无监督聚类的标签是**任意编号** | 必须结合质心坐标/业务含义解读 |
| 6 | 用聚类标签去和真实标签直接比 | 准确率很低 | 簇编号与真实类别编号没有对应关系 | 需要先做标签匹配再比 |
| 7 | 期望 KMeans 发现任意形状的簇 | 环形/月牙数据分不开 | KMeans 假设簇是**凸形、各向同性、大小相近** | 用 DBSCAN 或谱聚类 |
| 8 | 对异常值不做处理 | 质心被异常点拽偏 | 均值对异常值极其敏感 | 先做异常检测与剔除 |
| 9 | 重复 `fit`+`predict` 而不用 `fit_predict` | 代码慢、结果不一致 | 重复拟合会重新初始化 | 用 `labels = km.fit_predict(X)` |
| 10 | 用了废弃 API | `ImportError` / `FutureWarning` | `calinski_harabaz_score`、`samples_generator` 已废弃 | 用 `calinski_harabasz_score`、`sklearn.datasets` |
| 11 | 只聚类不做业务解读 | 报告没有价值 | 聚类本身不产生结论 | 打印各簇特征均值，给出人群画像命名 |
| 12 | 特征中包含 ID 列 | 聚类被 ID 主导 | ID 数值跨度大且无意义 | 聚类前剔除 ID 列 |

---

## 5. 面试问答

<details markdown="1"><summary markdown="1">Q1：KMeans 的算法流程是什么？为什么它一定会收敛？收敛到的是全局最优吗？</summary>

**参考答案**

**流程（4 步）**：
1. 事先确定常数 $K$；
2. 随机选择 $K$ 个样本点作为**初始聚类中心**；
3. **分配（Assign）**：计算每个样本到 $K$ 个中心的距离，把样本归到最近的中心；
4. **更新（Update）**：对每个簇重新计算均值作为新质心；如果新旧中心一致则停止，否则回到第 3 步。

**一定会收敛的原因**：目标 $J=\sum_k\sum_{x\in C_k}\|x-\mu_k\|^2$ 在两步操作下都**单调不增**：
- Assign 步：每个点独立选最近质心，是"固定质心、优化归属"的精确最优；
- Update 步：质心取簇均值是"固定归属、优化质心"的精确最优（对 $\mu$ 求导置零得 $\mu=\bar x$）。

$J\ge0$ 有下界，且把 $n$ 个样本分到 $K$ 个簇的划分方案数是**有限**的，所以不可能无限循环。

**但是局部最优**：$J$ 是**非凸**的，不同的初始质心会收敛到不同的局部极小。工程上用两种手段缓解：
1. `init='k-means++'`——按距离平方的加权概率依次挑选彼此远离的初始中心；
2. `n_init=10`——用 10 组不同初始中心各跑一遍，取 SSE 最小的结果。
</details>

<details markdown="1"><summary markdown="1">Q2：如何确定 KMeans 的 K 值？SSE、轮廓系数、CH 指数各有什么侧重？</summary>

**参考答案**

| 手段 | 定义 | 方向 | 侧重 |
| --- | --- | --- | --- |
| **肘部法** | 画 $K$ 与 SSE 的曲线，找**下降率突然变缓的拐点** | 拐点处取 $K$ | 只反映**簇内聚程度** |
| **轮廓系数 SC** | $s_i=\dfrac{b_i-a_i}{\max(a_i,b_i)}$ | 越大越好，$[-1,1]$ | 簇内聚 + **簇间分离** |
| **CH 指数** | $\dfrac{\text{SSB}/(k-1)}{\text{SSW}/(n-k)}$ | 越大越好 | 簇内聚 + 簇间离 + **质心个数** |

**注意 SSE 不能单独用来选 $K$**：SSE 随 $K$ 单调下降（$K=n$ 时为 0），只看 SSE 会永远选最大的 $K$，所以必须用**肘部法看拐点**。

**实践流程**：
1. 同时画三条曲线，若三者一致指向同一个 $K$，可信度很高；
2. 实验中 1000 个样本、4 个真实簇的数据，三条曲线都指向 $K=4$；
3. 顾客数据案例中，肘部法与 SC 都显示 $K=5$ 最好；
4. 最后用**业务可解释性**定夺——簇必须有可命名的业务含义。
</details>

<details markdown="1"><summary markdown="1">Q3：KMeans 有哪些局限？什么时候不该用它？</summary>

**参考答案**

| 局限 | 说明 | 替代方案 |
| --- | --- | --- |
| **必须预设 $K$** | $K$ 未知时要试探计算 | 用肘部法/SC/CH 估计；或层次聚类、DBSCAN |
| **对初始质心敏感** | 不同初值可能得到不同局部最优 | `k-means++` + `n_init=10` |
| **假设簇是凸形、各向同性、大小相近** | 环形、月牙形、密度差异大的簇分不开 | **DBSCAN**、**谱聚类** |
| **对异常值敏感** | 均值被离群点拽偏 | 先做异常检测；或用 K-medoids |
| **对量纲敏感** | 未标准化时结果被大量纲特征支配 | 先标准化 |
| **只适用于数值型特征** | 不能直接处理类别型 | 先 one-hot，或改用 K-prototypes |
| **需要遍历全量数据算距离** | 大数据集慢 | MiniBatchKMeans |
| **结果不稳定** | 数据增删一点，簇划分可能大变 | 固定随机种子并做稳定性检验 |

**不该用 KMeans 的典型场景**：
1. 簇是**非凸形状**（如同心圆、双月牙）——应选 DBSCAN；
2. 需要**自动识别噪声点**——应选 DBSCAN；
3. $K$ **完全未知且不想试探**——可用层次聚类看树状图；
4. 数据是**纯类别型**且类别无序——KMeans 的"均值"没有意义；
5. 数据维度极高——欧氏距离失效，应先降维或用余弦相似度。
</details>

---

## 6. 自测题

<details markdown="1"><summary markdown="1">1. 请对 KMeans 的实现流程排序：(A) 归类到最近的中心；(B) 计算到 K 个中心的距离 D；(C) 重复直到新旧中心一致；(D) 随机初始化 K 个中心；(E) 计算各簇均值作为新中心。</summary>

**D → B → A → E → C**

1. **D**：随机初始化 $K$ 个中心点；
2. **B**：计算样本点到这 $K$ 个中心点的距离 $D$；
3. **A**：把样本归类到 $D$ 值最小的那个中心所属的类别；
4. **E**：计算这 $K$ 个分类簇的均值，作为新的中心点；
5. **C**：重复上述过程，直至新的中心点与旧的中心点一致，迭代停止。
</details>

<details markdown="1"><summary markdown="1">2. 已知两个簇：$C_1=\{(1,1),(2,2)\}$，$C_2=\{(8,7),(9,8),(10,8)\}$，求各自的质心与 SSE。</summary>

**质心**：

$$\mu_1 = \Big(\frac{1+2}{2},\frac{1+2}{2}\Big)=(1.5,1.5),\qquad
\mu_2 = \Big(\frac{8+9+10}{3},\frac{7+8+8}{3}\Big)=(9,\ 7.667)$$

**SSE**：

$$C_1:\ (1-1.5)^2+(1-1.5)^2+(2-1.5)^2+(2-1.5)^2 = 1.0$$

$$C_2:\ 1+0.444+0+0.111+1+0.111 = 2.667$$

$$\text{SSE} = 1.0+2.667 = 3.667$$
</details>

<details markdown="1"><summary markdown="1">3. 某样本到同簇其他样本的平均距离 $a=2$，到最近其他簇的平均距离 $b=6$，求它的轮廓系数，并判断聚类质量。</summary>

$$s = \frac{b-a}{\max(a,b)} = \frac{6-2}{6} \approx 0.667$$

$s$ 接近 1，说明该样本**簇内很紧、离其他簇很远**，聚类归属很合理。若 $s$ 接近 0 说明在边界上，接近 $-1$ 则说明可能分错了簇。全体样本的 $s$ 取平均即为 SC。
</details>

<details markdown="1"><summary markdown="1">4. 为什么 KMeans 之前必须做标准化？如果特征里有 ID 列会怎样？</summary>

**必须标准化**：KMeans 用**欧氏距离**衡量相似性，距离对量纲高度敏感。若一个特征取值 0~1000、另一个只有 0~1，则

$$d^2 = (x_1-y_1)^2 + (x_2-y_2)^2$$

第一项会达到 $10^6$ 量级，第二项最多 1，**第二个特征等于完全没参与**。

**有 ID 列会怎样**：ID 通常取值跨度极大且**单调递增、与业务无关**。它会造成两个问题：
1. 在距离中独占主导地位，聚类退化按 ID 大小分组；
2. 即使标准化，ID 的连续性也会引入虚假的"相似性"结构。

所以聚类前应剔除 ID 列，只保留真正有业务含义的特征。
</details>

<details markdown="1"><summary markdown="1">5. SSE 随 K 增大而减小，为什么不能直接用 SSE 最小来选择 K？</summary>

因为 **SSE 有平凡的极小点**：当 $K = n$（每个样本自成一簇）时，每个点就是它所在簇的中心，距离为 0，**SSE = 0**。按"SSE 最小"选择就永远选最大的 $K$。

所以 SSE 只用于**肘部法**：观察 SSE 随 $K$ 下降的**斜率变化**，在"下降率突然变缓"的拐点处取 $K$。更严格的替代方案是使用**对 $K$ 有惩罚**的指标：
- **轮廓系数**：$a$ 随 $K$ 增大必然下降，但 $b$ 也会下降，二者的比值在正确的 $K$ 处取最大；
- **CH 指数**：分子 $\text{SSB}/(k-1)$ 会因 $k$ 过大而下降，自动惩罚过多类别。
</details>

---

## 7. 延伸阅读

- [scikit-learn 官方文档：K-means clustering](https://scikit-learn.org/stable/modules/clustering.html#k-means) —— `n_init`、`init='k-means++'`、`MiniBatchKMeans` 与收敛性质。
- [scikit-learn 官方文档：Clustering performance evaluation](https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation) —— 轮廓系数、CH、Davies-Bouldin 等指标的公式与适用条件。
- [scikit-learn 示例：Selecting the number of clusters with silhouette analysis](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html) —— 轮廓图选 $K$ 的官方可视化示例。
- [scikit-learn 示例：Empirical evaluation of the impact of k-means initialization](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_stability_low_dim_dense.html) —— 展示初始值对 KMeans 结果的影响。
- [Arthur & Vassilvitskii, *k-means++: The Advantages of Careful Seeding* (2007)](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf) —— k-means++ 初始化算法原始论文。
- [Wikipedia: Determine the number of clusters in a data set](https://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set) —— 肘部法、轮廓系数、CH 等方法综述。

---

[⬅️ 返回本目录索引](README.md)
