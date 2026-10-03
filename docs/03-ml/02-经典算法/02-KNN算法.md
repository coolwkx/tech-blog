# KNN 算法

> **一句话总结**：KNN（K-Nearest Neighbor）是"懒惰学习"的代表——训练阶段什么都不做，只把数据存下来；预测时现场计算待预测样本与所有训练样本的距离，取最近的 $K$ 个邻居，分类靠**多数表决**、回归靠**取平均**。
> **前置知识**：向量与距离概念、numpy 数组索引与广播、pandas 基础、`train_test_split` 的使用（见 [01-机器学习概述与流程](../01-基础与特征工程/01-机器学习概述与流程.md)）。
> **学完能做到**：
> 1. 手算欧氏距离、曼哈顿距离、切比雪夫距离与闵氏距离，并说明它们的关系；
> 2. 说清 $K$ 值大小的利弊，并使用 `GridSearchCV` 为 KNN 选出较优的 `n_neighbors`；
> 3. 独立完成"鸢尾花分类"与"手写数字识别"两个案例，并解释为什么 KNN 前必须做标准化。

---

## 1. 核心思想

### 1.1 一句话直觉

> **一个样本在特征空间中的 $K$ 个最相似的样本中，大多数属于某一个类别，则该样本也属于这个类别。**

"相似"用**距离**度量，距离越近越相似。KNN 的哲学是：**物以类聚，近朱者赤**——不做任何显式的函数拟合，完全靠邻居投票。

用电影类型预测的经典例子理解：已知若干电影的两个特征（"打斗镜头数"、"接吻镜头数"）和类型（动作片/爱情片），新来一部电影，看它在平面上离哪些点最近即可判断类型。

### 1.2 KNN 的关键属性

| 属性 | 说明 |
| --- | --- |
| 学习类型 | **监督学习**（分类 + 回归都能做） |
| 训练开销 | 几乎为零（懒惰学习 lazy learning），只存储训练集 |
| 预测开销 | $O(N \cdot d)$，$N$ 为训练样本数、$d$ 为特征维度；大数据集上很慢 |
| 是否需要标准化 | **必须**，因为距离对量纲敏感 |
| 是否受异常值影响 | 较大（尤其 $K$ 很小时） |
| 是否可解释 | 可解释性弱，只能说"因为邻居是这些" |
| 能否处理非线性边界 | 能，决策边界可以非常不规则 |

### 1.3 分类流程 vs 回归流程

| 步骤 | 分类（KNeighborsClassifier） | 回归（KNeighborsRegressor） |
| --- | --- | --- |
| 1 | 计算未知样本到**每一个**训练样本的距离 | 同左 |
| 2 | 按距离**升序**排序 | 同左 |
| 3 | 取出距离最近的 $K$ 个训练样本 | 同左 |
| 4 | **多数表决**：统计 $K$ 个邻居中哪个类别最多 | **取均值**：把这 $K$ 个样本的目标值求平均 |
| 5 | 把未知样本归到票数最多的类别 | 该平均值即为预测值 |

> 分类的"概率输出"就是各类别的投票占比：`predict_proba` 返回的是 $K$ 个邻居中各类别所占比例。

### 1.4 $K$ 值的选择：整门课最关键的一个超参数

| $K$ 取值 | 决策边界 | 偏差 | 方差 | 对噪声 | 极端情况 |
| --- | --- | --- | --- | --- | --- |
| $K$ 很小（如 1） | 非常曲折、贴着每个点 | 低 | 高 | **极敏感** | $K=1$：训练误差恒为 0，几乎必然过拟合 |
| $K$ 适中（如 5~10） | 平滑但仍能弯曲 | 中 | 中 | 较稳健 | 常用默认值 `n_neighbors=5` |
| $K$ 很大（如 $K=N$） | 几乎退化成一个平面 | 高 | 低 | 不敏感 | $K=N$：分类永远预测样本数最多的类（欠拟合） |

**工程上的规律**：
1. 一般取**奇数**，避免二分类时出现票数相同的平局；
2. $K$ 通常不超过 $\sqrt{N}$；
3. 用**交叉验证 + 网格搜索**确定，不要凭感觉。

### 1.5 KNN 的优缺点

| 优点 | 缺点 |
| --- | --- |
| 思想极简，无需训练，无参数假设（非参数模型） | 预测慢，需要保存全部训练数据，空间开销大 |
| 天然支持多分类 | 对量纲、异常值敏感，必须标准化 |
| 决策边界可以任意复杂 | 高维下距离失效（**维度灾难**） |
| 新数据可随时加入（增量友好） | 可解释性差，无法给出特征重要性 |

---

## 2. 算法细节

### 2.1 距离度量（四种距离的统一视角）

设两个 $d$ 维样本 $\boldsymbol{x}=(x_1,\dots,x_d)$、$\boldsymbol{y}=(y_1,\dots,y_d)$。

**（1）欧氏距离（Euclidean Distance）**——最常用，$L_2$ 范数：

$$d(\boldsymbol{x},\boldsymbol{y}) = \sqrt{\sum_{i=1}^{d}(x_i - y_i)^2} = \|\boldsymbol{x}-\boldsymbol{y}\|_2$$

**（2）曼哈顿距离（Manhattan / City Block Distance）**——$L_1$ 范数，只能横平竖直走：

$$d(\boldsymbol{x},\boldsymbol{y}) = \sum_{i=1}^{d}|x_i - y_i| = \|\boldsymbol{x}-\boldsymbol{y}\|_1$$

**（3）切比雪夫距离（Chebyshev Distance）**——$L_\infty$ 范数，取最大的那一维差值：

$$d(\boldsymbol{x},\boldsymbol{y}) = \max_{i} |x_i - y_i| = \|\boldsymbol{x}-\boldsymbol{y}\|_\infty$$

**（4）闵可夫斯基距离（Minkowski Distance）**——以上三者的统一形式：

$$d(\boldsymbol{x},\boldsymbol{y}) = \left(\sum_{i=1}^{d}|x_i - y_i|^{p}\right)^{1/p}$$

| $p$ 的取值 | 得到的距离 |
| --- | --- |
| $p = 1$ | 曼哈顿距离 |
| $p = 2$ | 欧氏距离 |
| $p \to \infty$ | 切比雪夫距离 |

> **注意**：闵氏距离不是一种新距离，而是**一类距离的概括表达式**，$p$ 就是它的"旋钮"。

### 2.2 手算示例：三种距离的差异

取 $\boldsymbol{x}=(0,0)$、$\boldsymbol{y}=(3,4)$：

| 距离 | 计算过程 | 结果 |
| --- | --- | --- |
| 欧氏 | $\sqrt{3^2+4^2}=\sqrt{25}$ | $5$ |
| 曼哈顿 | $|0-3|+|0-4| = 3+4$ | $7$ |
| 切比雪夫 | $\max(3,4)$ | $4$ |
| 闵氏 $p=3$ | $(3^3+4^3)^{1/3}=(27+64)^{1/3}$ | $\approx 4.50$ |

再看一个体现"形状差异"的例子：$\boldsymbol{a}=(1,1)$、$\boldsymbol{b}=(2,2)$ 与 $\boldsymbol{u}=(0,5)$

- 以曼哈顿距离看，$d(\boldsymbol{a},\boldsymbol{u})=5$、$d(\boldsymbol{b},\boldsymbol{u})=5$——**同距**；
- 以欧氏距离看，$d(\boldsymbol{a},\boldsymbol{u})=\sqrt{17}\approx 4.12$、$d(\boldsymbol{b},\boldsymbol{u})=\sqrt{13}\approx 3.61$——**不同距**。

**结论**：不同的相似度度量会得到**不同的分类/聚类结果**。

### 2.3 标准化：为什么 KNN 一定要做

假设两个特征：`每月工资`（6000~13000）与 `房产面积`（55~90）。计算欧氏距离时：

$$d^2 = (6000-8000)^2 + (55-65)^2 = 4{,}000{,}000 + 100$$

第二项被完全淹没。**距离由量纲大的特征单独支配**，量纲小的特征等于没参与。

**归一化（Min-Max Normalization）**：

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

API：`sklearn.preprocessing.MinMaxScaler(feature_range=(0, 1))`

**标准化（Z-Score Standardization）**：

$$x' = \frac{x - \mu}{\sigma},\qquad \mu = \frac{1}{N}\sum_i x_i,\quad \sigma=\sqrt{\frac{1}{N}\sum_i (x_i-\mu)^2}$$

API：`sklearn.preprocessing.StandardScaler()`，属性 `mean_`、`var_`、`scale_`。

| 对比项 | 归一化 MinMaxScaler | 标准化 StandardScaler |
| --- | --- | --- |
| 输出范围 | $[0,1]$（可指定） | 无固定范围，大致 $[-3,3]$ |
| 是否受异常值影响 | **大** | 小 |
| 适用场景 | 传统精确小数据、图像像素（除 255） | 通用首选；KNN、SVM、逻辑回归、PCA |

> 结论：**"一般倾向使用标准化"**。

### 2.4 KNN 的预测公式化描述

1. 计算距离并取最近邻下标集合：$\mathcal{N}_K(\boldsymbol{q}) = \arg\text{K-smallest}_{i}\ d(\boldsymbol{q},\boldsymbol{x}_i)$
2. **分类（多数表决）**：

$$\hat{y} = \arg\max_{c}\ \sum_{i \in \mathcal{N}_K(\boldsymbol{q})} \mathbb{1}[y_i = c]$$

 等价于预测概率 $\hat{p}(c\mid\boldsymbol{q}) = \frac{1}{K}\sum_{i\in\mathcal{N}_K}\mathbb{1}[y_i=c]$，再取最大者。

3. **回归（均值）**：

$$\hat{y} = \frac{1}{K}\sum_{i \in \mathcal{N}_K(\boldsymbol{q})} y_i$$

4. **距离加权版本**（`weights='distance'`）：

$$\hat{y} = \frac{\sum_{i\in\mathcal{N}_K} w_i\, y_i}{\sum_{i\in\mathcal{N}_K} w_i},\qquad w_i = \frac{1}{d(\boldsymbol{q},\boldsymbol{x}_i)}$$

### 2.5 交叉验证与网格搜索

**交叉验证**：把训练集切成 $n$ 份，每次拿 1 份当验证集、其余 $n-1$ 份当训练集。

以 $n=5$ 为例：

| 轮次 | 训练用 | 验证用 |
| --- | --- | --- |
| 第 1 轮 | 第 2,3,4,5 份 | 第 1 份 |
| 第 2 轮 | 第 1,3,4,5 份 | 第 2 份 |
| 第 3 轮 | 第 1,2,4,5 份 | 第 3 份 |
| 第 4 轮 | 第 1,2,3,5 份 | 第 4 份 |
| 第 5 轮 | 第 1,2,3,4 份 | 第 5 份 |

取 5 次验证得分的**平均值**作为该超参数组合的得分。

**网格搜索**：把候选超参数做笛卡尔积，逐一用交叉验证评分，取最高分组合。以 $K \in \{1,\dots,9\}$、$cv=5$ 为例，一共要训练 $9 \times 5 = 45$ 次。

| API 属性 | 含义 |
| --- | --- |
| `best_score_` | 交叉验证中所有参数组合的最高平均验证得分 |
| `best_params_` | 最优超参数字典 |
| `best_estimator_` | 用最优参数在**全部训练集**上重新拟合好的估计器 |
| `cv_results_` | 每一组参数的详细结果 |

> `GridSearchCV` 只使用训练集，**不碰测试集**；选完参数后再用测试集评估一次。

---

## 3. 可运行示例

### 3.1 距离公式的 numpy 实现

```python
# -*- coding: utf-8 -*-
"""四种距离的 numpy 实现与对比"""
import numpy as np


def euclidean(a, b):
    return np.sqrt(np.sum((a - b) ** 2))


def manhattan(a, b):
    return np.sum(np.abs(a - b))


def chebyshev(a, b):
    return np.max(np.abs(a - b))


def minkowski(a, b, p):
    """p=1 -> 曼哈顿, p=2 -> 欧氏, p->inf -> 切比雪夫"""
    return np.power(np.sum(np.abs(a - b) ** p), 1.0 / p)


if __name__ == "__main__":
    a = np.array([0.0, 0.0])
    b = np.array([3.0, 4.0])
    print("欧氏距离 :", euclidean(a, b)) # 5.0
    print("曼哈顿距离 :", manhattan(a, b)) # 7.0
    print("切比雪夫距离:", chebyshev(a, b)) # 4.0
    for p in (1, 2, 3, 10):
        print(f"闵氏距离 p={p:2d}: {minkowski(a, b, p):.4f}")
```

### 3.2 鸢尾花分类：完整流程 + 交叉验证网格搜索

```python
# -*- coding: utf-8 -*-
"""KNN 鸢尾花分类：标准化 + 网格搜索选 K"""
import numpy as np
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


def main():
    # 1. 获取数据
    iris = load_iris()
    X, y = iris.data, iris.target

    # 2. 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=22, stratify=y
    )

    # 3. 特征工程：标准化（训练集 fit_transform，测试集 transform）
    transfer = StandardScaler()
    X_train = transfer.fit_transform(X_train)
    X_test = transfer.transform(X_test)

    # 4. 网格搜索 + 交叉验证选 K
    estimator = KNeighborsClassifier()
    param_grid = {"n_neighbors": range(1, 15)}
    grid = GridSearchCV(estimator=estimator, param_grid=param_grid, cv=5)
    grid.fit(X_train, y_train)

    print("最优 K :", grid.best_params_)
    print("CV 最高平均分 :", round(grid.best_score_, 4))
    print("最优估计器 :", grid.best_estimator_)

    # 5. 用最优模型评估测试集
    best = grid.best_estimator_
    y_pred = best.predict(X_test)
    print("测试集准确率 :", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # 6. 对新样本预测（别忘了用同一个 scaler 变换）
    my_data = transfer.transform([[5.1, 3.5, 1.4, 0.2]])
    print("新样本类别 :", best.predict(my_data),
    "->", iris.target_names[best.predict(my_data)[0]])
    print("新样本类别概率 :", np.round(best.predict_proba(my_data), 4))


    if __name__ == "__main__":
        main()
```

### 3.3 KNN 回归：验证"取邻居均值"这一条

```python
# -*- coding: utf-8 -*-
"""KNN 回归：预测值 = 最近 K 个邻居目标值的平均"""
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

X = [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]]
y = [0.1, 0.2, 0.3, 0.4]

model = KNeighborsRegressor(n_neighbors=3)
model.fit(X, y)

q = [[4, 4, 5]]
print("预测值:", model.predict(q)) # 0.3（0.2/0.3/0.4 的均值）

# 手工验证：q 到 4 个训练点的距离（欧氏）
q_arr = np.array(q[0])
for xi, yi in zip(X, y):
 print(f"点 {xi} 距离 {np.linalg.norm(np.array(xi) - q_arr):.4f} 目标值 {yi}")
 # 最近的 3 个距离为 1.7321/1.7321/3.4641 -> 目标值 0.2, 0.3, 0.4 -> 平均 0.3
```

### 3.4 手写数字识别的关键片段

数据：`手写数字识别.csv`，每行 785 列 = 1 列标签 + 784 个像素（28×28，取值 0~255）。

```python
# -*- coding: utf-8 -*-
"""KNN 手写数字识别：读取 -> 归一化 -> 训练 -> 保存 -> 推理"""
import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

CSV = "手写数字识别.csv"


def show_digit(idx, data):
    """把第 idx 行还原成 28x28 的灰度图"""
    x = data.iloc[:, 1:]
    digit = x.iloc[idx].values.reshape(28, 28)
    plt.axis("off")
    plt.imshow(digit, cmap="gray")
    plt.show()


    def train_model(data):
        x = data.iloc[:, 1:]
        y = data.iloc[:, 0]

        # 归一化：像素值 0~255 -> 0~1（对 KNN 这类基于距离的模型很重要）
        x = x / 255

        # stratify=y：按类别比例分层抽样
        x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=21
        )

        estimator = KNeighborsClassifier(n_neighbors=3)
        estimator.fit(x_train, y_train)
        print("测试集准确率: %.4f" % estimator.score(x_test, y_test))

        joblib.dump(estimator, "knn_digit.pkl")


        def use_model(img_path):
            img = plt.imread(img_path) # 28x28 灰度图
            estimator = joblib.load("knn_digit.pkl")
            img = img / 255.0 # 关键：推理时也要做与训练一致的归一化
            img = img.reshape(1, -1) # (28,28) -> (1,784)
            print("识别结果:", estimator.predict(img))


            if __name__ == "__main__":
                data = pd.read_csv(CSV)
                train_model(data)
```

> **注意**：原代码的 `use_model` 里**没有除以 255**，而训练时做了归一化，导致训练/推理量纲不一致。这里已补上 `img = img / 255.0`。

---

## 4. 常见坑

| # | 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- | --- |
| 1 | 不做标准化直接上 KNN | 准确率很低且难以提升 | 大量纲特征支配距离 | 先 `StandardScaler`/`MinMaxScaler` |
| 2 | 对全量数据 `fit_transform` 后再划分 | 离线指标虚高，线上掉分 | 测试集统计量泄漏 | 先划分；训练集 `fit_transform`、测试集 `transform` |
| 3 | 新样本预测时忘了做同样的变换 | 预测结果荒谬 | 训练/推理量纲不一致 | 把 `transfer` 一起保存，或用 `Pipeline` |
| 4 | $K$ 取偶数做二分类 | 出现平票，结果不稳定 | 投票数相同 | 取奇数，或用 `weights='distance'` |
| 5 | $K$ 取 1 就宣布"准确率 100%" | 训练集准确率必然 100% | $K=1$ 时每个点都是自己的最近邻 | 只看**测试集/CV**得分 |
| 6 | $K$ 取得过大 | 所有样本预测成同一类 | 邻居太多，退化为"多数类" | 用网格搜索在合理区间（如 1~20）选 |
| 7 | 直接对原始像素做距离且不归一化 | 数字识别效果差 | 像素值差异被放大 | 除以 255 或用标准化 |
| 8 | 高维特征直接上 KNN | 效果比随机猜还差 | **维度灾难**：高维空间中距离趋于相等 | 先做特征选择/PCA 降维，或改用树模型 |
| 9 | 用 KNN 处理超大训练集 | 预测接口超时 | 每次预测都要扫描全量样本 | 用 KD-Tree/Ball-Tree（`algorithm='kd_tree'`）或换模型 |
| 10 | 类别极不平衡时看 KNN 的准确率 | 准确率虚高 | 多数类邻居占满 K 个位置 | 看 F1/AUC，或对样本加权 |

---

## 5. 面试问答

<details><summary>Q1：KNN 的 K 值大小如何影响模型？如何选择最优 K？</summary>

**参考答案**

**影响**：
- $K$ 太小（如 1）：模型复杂度高、方差大、对噪声和异常值极敏感，决策边界贴着每个训练点，训练误差≈0 但泛化差（过拟合）；
- $K$ 太大：模型过于简单、偏差大，邻居过多导致"多数类"吞掉所有预测，出现欠拟合；
- $K=N$：分类永远输出训练集中样本最多的类别。

**选择方法**：
1. 用**交叉验证 + 网格搜索**（`GridSearchCV(KNeighborsClassifier(), {"n_neighbors": range(1,21)}, cv=5)`）选 `best_params_`；
2. 经验上取奇数、不超过 $\sqrt{N}$；
3. 若采用距离加权（`weights='distance'`），$K$ 的敏感度会降低。

**补充**：$K$ 的调优必须配合**标准化**，否则距离本身就被量纲污染，调 $K$ 意义不大。
</details>

<details><summary>Q2：KNN 与 KMeans 有什么区别？（名字像，本质完全不同）</summary>

**参考答案**

| 维度 | KNN | KMeans |
| --- | --- | --- |
| 学习类型 | 监督学习（分类/回归） | 无监督学习（聚类） |
| 是否需要标签 | 需要 | 不需要 |
| $K$ 的含义 | **邻居个数** | **簇（聚类中心）个数** |
| 训练过程 | 无（懒惰学习），只存数据 | 有迭代：分配样本 → 更新质心 → 收敛 |
| 预测依据 | 最近 $K$ 个邻居投票/取均值 | 距离最近的**质心**所属簇 |
| 计算复杂度 | 预测 $O(Nd)$ | 每轮 $O(NKd)$，迭代若干轮 |
| 一句话 | "看邻居是谁" | "把样本分成 K 堆，让堆内最紧" |
</details>

<details><summary>Q3：为什么 KNN 对异常值敏感？有哪些改进手段？</summary>

**参考答案**

**原因**：KNN 的预测完全由距离最近的 $K$ 个样本决定，没有全局参数"平滑"，一个异常点只要恰好落进邻居圈，就会直接参与投票或拉高/拉低均值。$K$ 越小越严重。

**改进手段**：
1. **增大 $K$**：更多邻居平均掉异常点的影响；
2. **距离加权 `weights='distance'`**：按 $1/d$ 衰减，降低单点影响；
3. **异常值检测与清洗**：先用 IQR / 3σ / Isolation Forest 剔除离群点；
4. **改用中位数或截尾均值**（自定义实现回归的聚合方式）；
5. **特征标准化**：避免某个异常大的量纲把距离整体拉偏；
6. **改用对噪声更稳健的模型**（随机森林、GBDT）。
</details>

---

## 6. 自测题

<details><summary>1. 计算 $\boldsymbol{a}=(0,0)$ 与 $\boldsymbol{b}=(6,8)$ 的欧氏距离、曼哈顿距离、切比雪夫距离。</summary>

- 欧氏：$\sqrt{6^2+8^2} = 10$
- 曼哈顿：$6 + 8 = 14$
- 切比雪夫：$\max(6,8) = 8$

三者大小关系恒为：切比雪夫 ≤ 欧氏 ≤ 曼哈顿（对同一个点对）。
</details>

<details><summary>2. 闵氏距离中 $p=1,2,\infty$ 分别对应什么距离？为什么说它不是"新距离"？</summary>

$p=1$ 对应曼哈顿距离，$p=2$ 对应欧氏距离，$p\to\infty$ 对应切比雪夫距离。它不是一种新的度量方式，而是**对多个距离公式的概括性表述**——通过改变 $p$ 得到已知距离，所以又称"距离的组合"。
</details>

<details><summary>3. 为什么 KNN 之前必须做标准化，而决策树一般不需要？</summary>

KNN 用**距离**判断相似性，距离对特征量纲高度敏感，量纲大的特征会独占距离的绝大部分，使量纲小的特征失效。而决策树每次只在**单个特征**上找一个切分阈值，分裂不涉及不同特征之间的数值比较，因此对单调变换不敏感，标准化的影响通常可忽略。
</details>

<details><summary>4. 用 $K=1$ 的 KNN 在训练集上评估，准确率是多少？这说明什么？</summary>

**恒为 100%**（在无重复且无冲突标签的前提下）。因为每个训练样本的最近邻居就是它自己，距离为 0。

这说明：**训练集准确率不能用来评价 KNN**，必须使用测试集或交叉验证。$K=1$ 是过拟合的极端案例——它记住了所有训练样本，包括噪声。
</details>

<details><summary>5. 交叉验证与网格搜索分别解决什么问题？为什么 `GridSearchCV` 不能碰测试集？</summary>

- **交叉验证**解决"评估不稳定、数据太少"的问题：通过轮换验证集，让每个样本都参与验证，得到更稳的泛化估计；
- **网格搜索**解决"超参数怎么选"的问题：把候选参数组合逐一用交叉验证评分。

不能碰测试集是因为：一旦用测试集的结果来决定超参数，测试集的信息就通过你的选择过程泄漏进模型，它不再代表"未见过的新数据"，最终评估会乐观偏置。正确做法是 `GridSearchCV` 只在训练集上做，测试集只用于**最终一次**评估。
</details>

---

## 7. 延伸阅读

- [scikit-learn 官方文档：Nearest Neighbors](https://scikit-learn.org/stable/modules/neighbors.html) —— `KNeighborsClassifier/Regressor` 的参数（`weights`、`algorithm`、`metric`）与复杂度说明。
- [scikit-learn 官方文档：Preprocessing — Standardization or Min-Max scaling?](https://scikit-learn.org/stable/modules/preprocessing.html) —— 归一化与标准化的官方选型建议。
- [scikit-learn 官方用户指南：Cross-validation 与 GridSearchCV](https://scikit-learn.org/stable/modules/grid_search.html) —— 网格搜索 API 与 `cv_results_` 字段含义。
- [scikit-learn 官方文档：Pairwise metrics（距离度量）](https://scikit-learn.org/stable/modules/metrics.html) —— `manhattan_distances`、`euclidean_distances` 等实现。
- [MNIST 数据集官方主页（Yann LeCun）](http://yann.lecun.com/exdb/mnist/) —— 手写数字识别的原始数据集与基准结果。

---

[⬅️ 返回本目录索引](README.md)
