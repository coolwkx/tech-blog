---
article_id: kp-993eb3a251f3ea8d
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 7
learning_objective: 理解并验证：类别型特征处理
---

# 类别型特征处理

> **学习目标**：能够解释「类别型特征处理」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 算法细节

## 本次只学这一点

**（1）one-hot 编码（独热编码）**

把有 $k$ 个取值的类别特征变成 $k$ 个 0/1 列。

```python
pd.get_dummies(data) # pandas 方式：category -> 0/1 多列
pd.get_dummies(data, columns=['Gender'])
```

| 优点 | 缺点 |
| --- | --- |
| 不引入虚假的大小关系 | 类别多时特征维度爆炸、矩阵稀疏 |
| 对线性模型/距离模型必要 | 高基数类别需要特殊处理（目标编码、哈希） |
| 与树模型兼容 | 存在**哑变量陷阱**（完全共线） |

> **哑变量陷阱（dummy variable trap）**：$k$ 个 0/1 列的和恒为 1，与截距列完全共线，使 $\boldsymbol{X}^\top\boldsymbol{X}$ 奇异。所以在代码里会删掉一列（`data.drop(['gender_Male', 'Churn_No'], axis=1)`）——每个类别组**删掉一个基准列**。

**（2）`DictVectorizer`（字典特征提取）**

把"字典列表"转成特征矩阵，**自动对字符串值做 one-hot**，最适合从 `DataFrame.to_dict(orient='records')` 抽取类别特征：

```python
from sklearn.feature_extraction import DictVectorizer

vec = DictVectorizer(sparse=False)
X_train = vec.fit_transform(X_train.to_dict(orient='records'))
X_test = vec.transform(X_test.to_dict(orient='records')) # 测试集只 transform！
print(vec.get_feature_names_out) # 如 ['Age', 'Pclass', 'Sex=female', 'Sex=male']
```

| 特点 | 说明 |
| --- | --- |
| 输入 | `list[dict]`，键为特征名 |
| 数值型 | 保持原值 |
| 字符串型 | 转成 `特征名=取值` 的 0/1 列 |
| 关键纪律 | 训练集 `fit_transform`、测试集只能 `transform`，否则特征列对不齐 |

**（3）LabelEncoder（序数编码）**——给类别分配整数编号：

```python
from sklearn.preprocessing import LabelEncoder
y = LabelEncoder.fit_transform(y) # [2,3] -> [0,1]
```

**注意**：只适合**有序类别**或**标签列**。直接对无序类别用整数编码会引入虚假的大小关系（"北京=1 < 上海=2"毫无意义），对线性模型和距离模型有害。红酒案例用它把标签 (2,3) 转成 (0,1)，属于**标签编码**的正确用法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「类别型特征处理」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
