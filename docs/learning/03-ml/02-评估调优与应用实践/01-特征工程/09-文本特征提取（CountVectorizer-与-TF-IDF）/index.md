---
article_id: kp-cded184a0f057c68
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-0d24db15ec32
learning_sourceId: 0d24db15ec32
learning_order: 8
learning_objective: 理解并验证：文本特征提取（CountVectorizer 与 TF-IDF）
---

# 文本特征提取（CountVectorizer 与 TF-IDF）

> **学习目标**：能够解释「文本特征提取（CountVectorizer 与 TF-IDF）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 的 `groupby`/`get_dummies`/缺失值处理、numpy 的数组拼接（`hstack`）、距离与量纲的影响（见 [02-KNN算法](../../../../../03-ml/02-经典算法/02-KNN算法.md)）。
>
> **所属主题**：特征工程 · 算法细节

## 本次只学这一点

**流程**：分词 → 去停用词 → 构建词频矩阵。

```python
import jieba
from sklearn.feature_extraction.text import CountVectorizer

stop_words = [line.strip() for line in open('stopwords.txt', encoding='utf8')]
comment_list = [','.join(jieba.lcut(line)) for line in data['内容']]

transform = CountVectorizer(stop_words=stop_words)
x = transform.fit_transform(comment_list) # 稀疏矩阵
names = transform.get_feature_names_out # 词表
x = x.toarray # 需要稠密时再转
```

**TF-IDF**（扩展）——衡量一个词对某篇文档的重要性：

$$\text{TF}(t,d) = \frac{n_{t,d}}{N_d},\qquad
\text{IDF}(t) = \log\frac{|D|}{|\{d: t\in d\}|},\qquad
\text{TF-IDF} = \text{TF}\times\text{IDF}$$

| 符号 | 含义 |
| --- | --- |
| $n_{t,d}$ | 词 $t$ 在文档 $d$ 中出现的次数 |
| $N_d$ | 文档 $d$ 中所有词汇的总数 |
| $\lvert D\rvert$ | 语料库中的总文档数 |
| $\lvert\{d:t\in d\}\rvert$ | 包含词 $t$ 的文档数量 |

**直觉**：一个词在当前文档出现越多（TF 高）、在别的文档出现越少（IDF 高），它就越有代表性。这样能自动压低"的、是、了"这类高频停用词的影响（实践中还会直接用停用词表过滤）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「文本特征提取（CountVectorizer 与 TF-IDF）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)
