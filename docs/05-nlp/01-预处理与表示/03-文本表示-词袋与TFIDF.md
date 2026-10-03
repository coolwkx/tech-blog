# 03 文本表示：词袋与 TF-IDF

> **一句话总结**：把变长文本压成定长稀疏向量——词袋负责「有哪些词」，TF-IDF 负责「哪些词更重要」。
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。

> 1. 手写词袋与 TF-IDF 的计算过程，并解释 `TF × IDF` 里每一项的作用。
> 2. 说清 sklearn `TfidfVectorizer` 的 `smooth_idf`、`sublinear_tf`、L2 归一化到底做了什么。
> 3. 用 `/max_features`、`min_df`、`max_df`、停用词把特征维度压到可训练规模，并给出选型理由。

## 1. 核心概念

### 1.1 文本表示要解决什么问题

模型只能吃数字。把文本变成数字的过程叫**文本张量表示**，主流路线有三代：

| 代际 | 表示 | 维度 | 是否稠密 | 是否含语义 | 代表 |
|------|------|------|----------|-----------|------|
| 第一代 | one-hot | 词表大小 $V$ | 稀疏（只有一个 1） | 无（任意两词正交） | 独热编码 |
| 第二代 | 词袋 / n-gram 计数 | $V$ 或 $V^n$ 裁剪后 | 稀疏 | 只有词形，无同义 | BoW、TF、TF-IDF |
| 第三代 | 分布式词向量 | 100–768 | 稠密 | 有（相似词靠近） | word2vec、BERT |

本篇聚焦第二代：**它至今仍是强基线**。在中小规模、类别区分度靠关键词的任务上（新闻分类、垃圾邮件、医疗问题分类），TF-IDF + 线性模型的表现往往接近甚至超过小模型深度网络，而且训练只要几秒、可解释性强。所以先打好这一代的地基，再理解为什么需要第三代。

### 1.2 one-hot 的两个致命缺点（复习）

| 优点 | 缺点 |
|------|------|
| 简单、易理解、无需训练 | 任意两个不同词的余弦相似度恒为 0，无法表达「酒店≈宾馆」 |
| 无额外参数 | 维度 = 词表大小，一个向量只有一个 1，极度稀疏 |

文本级 one-hot 的另一个问题：一条句子有多个词，如果直接把各词 one-hot 相加，就得到了**词袋**；这也是词袋与 one-hot 的天然联系。

### 1.3 词袋模型（Bag-of-Words）

词袋把文本表示成一个「词频向量」，忽略词序：

$$
\text{BoW}(d) = \big(\text{count}(w_1, d),\ \text{count}(w_2, d),\ \dots,\ \text{count}(w_V, d)\big)
$$

| 文档 | 词袋（词表 = [我, 爱, 你, 他]） |
|------|-------------------------------|
| 我爱你 | (1, 1, 1, 0) |
| 你爱我 | (1, 1, 1, 0) ← 与上一行完全相同 |
| 他爱你 | (0, 1, 1, 1) |

第二、三行暴露了词袋的两大缺陷：

1. **丢失词序**：「我爱你」和「你爱我」表示完全相同。
2. **丢失重要性**：「的」「是」出现得多，权重反而比「退款」这类关键判别词更高。

n-gram 特征解决第一个问题（把相邻词组合成新特征），TF-IDF 解决第二个问题。

### 1.4 n-gram 特征

把连续的 $n$ 个 token 组合成一个新特征：

| n | 名称 | 「我 / 爱 / 」的产出 |
|---|------|--------------------------|
| 1 | unigram | 我、爱、 |
| 2 | bi-gram | 我爱、爱 |
| 3 | tri-gram | 我爱 |

实现上一行代码即可：

```python
def add_n_gram(a, n=2):
 return set(zip(*[a[i:] for i in range(n)]))
```

原理：`[a[i:] for i in range(n)]` 得到 `n` 条错位对齐的列表，`zip` 把它们按位置捆成元组。词表为 $V$ 时 bi-gram 理论上界是 $V^2$，因此实际必须用 `min_count`/`min_df` 剪掉低频 n-gram。

### 1.5 TF-IDF：核心思想

TF-IDF 用两个因子相乘来衡量一个词对一篇文档的重要性：

| 因子 | 含义 | 直觉 |
|------|------|------|
| TF（Term Frequency） | 词在**本篇**文档中出现的频率 | 出现越多，越可能反映本篇主题 |
| IDF（Inverse Document Frequency） | 词在**整个语料**中有多稀有 | 越稀有越有区分度，越常见越没用 |

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \text{IDF}(t)
$$

一句话记忆：**TF 看「这篇里有多少」，IDF 看「全语料里有多稀」**。"的」TF 很高但 IDF 极低（几乎每篇都有），乘积很小；「量子计算」TF 可能只有 1，但 IDF 很高，乘积反而大。

## 2. 方法细节

### 2.1 TF 的三种变体

$$
\text{TF}(t,d) =
\begin{cases}
f_{t,d} & \text{原始计数} \\
\dfrac{f_{t,d}}{\sum_{t' \in d} f_{t',d}} & \text{归一化频率（防长文档占优）} \\
1 + \log f_{t,d} & \text{对数 TF（抑制高频）}
\end{cases}
$$

注意：原始计数会让长文档的所有词得分都更高，因此**归一化或对数化几乎是必须的**。sklearn 里对应 `sublinear_tf=True` 时使用 $1+\log f$。

### 2.2 IDF 与平滑

$$
\text{IDF}(t) = \log\frac{N}{\text{DF}(t)}
$$

其中 $N$ 是文档总数，$\text{DF}(t)$ 是包含词 $t$ 的文档数。两个问题需要平滑处理：

1. 若某词出现在所有文档中（$\text{DF} = N$），则 $\text{IDF} = \log 1 = 0$，该词被完全抹掉。这本身符合预期，但若某词在**整个语料**都没出现（推理时的新词），会除零。
2. 为避免除零并使权重平滑，常用变体：

$$
\text{IDF}(t) = \log\frac{1 + N}{1 + \text{DF}(t)} + 1
$$

这正是 sklearn `TfidfVectorizer` 的**默认行为**（`smooth_idf=True`）：加 1 平滑，并且最后整体加 1，使得「出现在所有文档中的词」IDF 取 1 而不是 0（保证它仍有一点权重、不会完全消失）。

### 2.3 向量归一化

计算完 TF-IDF 后，sklearn 默认对每个文档向量做 **L2 归一化**：

$$
\tilde{v} = \frac{v}{\lVert v \rVert_2}
$$

原因：归一化后，任意两个文档的**点积就等于余弦相似度**，与文档长度无关。这直接让后续的线性模型 / KNN / 检索打分变得稳健。这也是为什么检索系统里 TF-IDF 与余弦相似度总是成对出现。

### 2.4 TF-IDF 的完整计算示例

语料（3 篇文档，$N=3$）：

```
d1: 猫 喜欢 鱼
d2: 狗 喜欢 骨头
d3: 猫 狗 喜欢 打架
```

含词文档数：`喜欢`=3、`猫`=2、`狗`=2、`鱼`=1、`骨头`=1、`打架`=1。

用 sklearn 默认的平滑 IDF $\log\frac{1+N}{1+DF}+1$：

| 词 | DF | IDF |
|----|-----|-----|
| 喜欢 | 3 | $\log\frac{4}{4}+1 = 1.0$ |
| 猫 | 2 | $\log\frac{4}{3}+1 = 1.2877$ |
| 狗 | 2 | $\log\frac{4}{3}+1 = 1.2877$ |
| 鱼 | 1 | $\log\frac{4}{2}+1 = 1.6931$ |
| 骨头 | 1 | 1.6931 |
| 打架 | 1 | 1.6931 |

对 d1「猫 喜欢 鱼」，若 TF 用原始计数（均为 1），归一化前的向量为 `(猫:1.2877, 喜欢:1.0, 鱼:1.6931)`，L2 范数为 $\sqrt{1.2877^2+1^2+1.6931^2}=2.3856$，归一化后为 `(0.5398, 0.4192, 0.7097)`。

可以看到：**「喜欢」虽然出现在每篇文档里，仍保留了 1.0 的 IDF**（因为加了平滑与 +1），而不是被抹成 0——这是 sklearn 与教科书朴素 IDF 的差异，读源码时容易踩。

### 2.5 稀疏矩阵为什么省内存

词表 $V$ 可能有 5 万，但一篇文档平均只有 30 个词，所以词袋矩阵 99.9% 是 0。用稠密 `numpy.ndarray` 存 $(180000, 50000)$ 的 float64 需要

$$
180000 \times 50000 \times 8\ \text{字节} \approx 72\ \text{GB}
$$

而 CSR（Compressed Sparse Row）只存非零值、列索引和行指针：

| 数组 | 长度 | 含义 |
|------|------|------|
| `data` | nnz | 所有非零值，按行优先排列 |
| `indices` | nnz | 每个非零值对应的列号 |
| `indptr` | n_rows + 1 | 第 i 行的非零值在 `data` 中的起止位置 |

同样 18 万行 × 平均 30 个非零值，只需约 $180000 \times 30 \times 12$ 字节 ≈ 65 MB，**缩小了三个数量级**。代价是不支持直接随机访问单个元素、切片不灵活。

### 2.6 sklearn `TfidfVectorizer` 参数速查

| 参数 | 默认 | 作用 | 建议 |
|------|------|------|------|
| `max_features` | None | 只保留词频最高的前 N 个词 | 中文任务常取 5000–50000；先看特征维度再定 |
| `min_df` | 1 | 忽略文档频率低于该值的词 | 取 2–5，可有效剪掉拼写错误与噪声 |
| `max_df` | 1.0 | 忽略文档频率高于该值（比例）的词，相当于自动停用词 | 取 0.8–0.95 |
| `stop_words` | None | 停用词表（list 或 `'english'`） | 中文必须自己传 list |
| `ngram_range` | (1,1) | n-gram 范围 | 短文本用 (1,2)，长文本 (1,1) 即可 |
| `sublinear_tf` | False | 用 $1+\log f$ 替代原始计数 | 词频差异大时开启 |
| `smooth_idf` | True | 加 1 平滑并整体 +1 | 通常保持开启 |
| `norm` | 'l2' | 归一化方式（`l1`/`l2`/None） | 保持 `'l2'` |
| `token_pattern` | `r"(?u)\b\w\w+\b"` | 分词正则 | **中文必须改**，否则单字被丢弃 |
| `lowercase` | True | 是否转小写 | 中文可设 False |

两个中文场景的经典坑：

- `token_pattern` 默认要求 token 至少 2 个 `\w`，中文单字会被直接丢掉。若已用 jieba 分好词并用空格连接，需设为 `r"(?u)\b\w+\b"`。
- `analyzer='char'` 可以做**字符级** TF-IDF，对中文短文本有时比词级更稳（无分词错误），可以作为对照实验。

## 3. 可运行示例

### 3.1 手写 TF-IDF（含平滑与 L2 归一化）

```python
# 依赖: pip install numpy
import math
from collections import Counter
import numpy as np

docs = ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 狗 喜欢 打架"]
docs_tokens = [d.split for d in docs]

# 1) 建立词表
vocab = sorted({w for doc in docs_tokens for w in doc})
word2id = {w: i for i, w in enumerate(vocab)}
N, V = len(docs_tokens), len(vocab)

# 2) 文档频率 DF
df = Counter
for doc in docs_tokens:
    df.update(set(doc))

    # 3) 平滑 IDF: log((1+N)/(1+df)) + 1
    idf = {w: math.log((1 + N) / (1 + df[w])) + 1 for w in vocab}

    # 4) TF-IDF（TF 用对数变体 1+log f）+ L2 归一化
    matrix = np.zeros((N, V))
    for i, doc in enumerate(docs_tokens):
        tf = Counter(doc)
        for w, f in tf.items:
            matrix[i, word2id[w]] = (1 + math.log(f)) * idf[w]
            norm = np.linalg.norm(matrix[i])
            if norm > 0:
                matrix[i] /= norm

                print("词表:", vocab)
                for w in vocab:
                    print(f" IDF({w}) = {idf[w]:.4f}")
                    print("\nTF-IDF 矩阵:\n", np.round(matrix, 4))

                    # 5) 用余弦相似度做检索（归一化后点积即余弦）
                    query = "猫 鱼".split
                    q = np.zeros(V)
                    for w in query:
                        if w in word2id:
                            q[word2id[w]] = 1.0 * idf[w]
                            q /= np.linalg.norm(q)
                            print("\n与查询的相似度:", np.round(matrix @ q, 4))
```

### 3.2 与 sklearn 对照（验证两者的差异）

```python
# 依赖: pip install scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer

docs = ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 狗 喜欢 打架"]

vec = TfidfVectorizer(
token_pattern=r"(?u)\b\w+\b", # 中文分词后必须放宽，否则单字被丢弃
smooth_idf=True, # log((1+N)/(1+df)) + 1
sublinear_tf=False, # TF 用原始计数，与上一节手写版不同
norm="l2",
)
X = vec.fit_transform(docs)

print("词表:", vec.get_feature_names_out)
print("IDF :", dict(zip(vec.get_feature_names_out, vec.idf_.round(4))))
print("矩阵:\n", X.toarray.round(4))
print("稀疏结构: data=%d, indices=%d, indptr=%s"
% (X.data.size, X.indices.size, X.indptr))
```

注意手写版与 sklearn 的结果**不可能完全一致**，因为：手写版用了 `1 + log f` 的对数 TF 而 sklearn 默认用原始计数；两者对 IDF 的实现细节也略有出入。要严格对齐，把手写版的 TF 改回原始计数即可。

### 3.3 `fit_transform` 与 `transform` 的区别（最经典的坑）

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

train = ["这个酒店位置很好 干净", "服务很好 推荐", "早餐不好 房间差", "服务不到位 隔音差"]
y = [1, 1, 0, 0]
test = ["位置很好 服务不错", "房间差 服务不到位"]

vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")

# 训练集: fit + transform 一步完成，会学习词表与 IDF
X_train = vec.fit_transform(train)

# 测试集: 只能 transform，复用训练时学到的词表与 IDF
X_test = vec.transform(test)

clf = LogisticRegression(max_iter=1000).fit(X_train, y)
print("预测:", clf.predict(X_test))

# 查看对分类贡献最大的词，便于做错误分析
import numpy as np
names = np.array(vec.get_feature_names_out)
for cls, coef in zip(clf.classes_, clf.coef_):
 top = names[np.argsort(coef)[-5:]][::-1]
 print(f"类别 {cls} 的正向关键词: {list(top)}")
```

如果对测试集也调用 `fit_transform`，会**重新学习一套词表和 IDF**，导致：
训练/测试特征空间维度可能不同（直接报维度不匹配），或维度碰巧相同但列的含义错位，模型给出的预测是垃圾。这是一个不会报错、只会静默变差的最危险错误。

### 3.4 稀疏矩阵与特征裁剪的工程实践

```python
# 依赖: pip install scikit-learn scipy
from sklearn.feature_extraction.text import TfidfVectorizer

# 用内联小语料模拟 180000 条新闻的场景
docs = ["湖人 队 赢得 总冠军", "美联储 宣布 加息", "高考 改革 方案 公布",
"湖人 战胜 凯尔特人", "央行 调整 利率", "教育部 发布 通知"] * 300

vec = TfidfVectorizer(
max_features=50000, # 只保留最高频的 5 万个词
min_df=2, # 出现在少于 2 篇文档中的词直接丢弃
max_df=0.9, # 出现在超过 90% 文档中的词视为停用词
ngram_range=(1, 2), # 加入 bi-gram，部分恢复词序
sublinear_tf=True, # 词频差异大，用 1+log(f)
token_pattern=r"(?u)\b\w+\b",
)
X = vec.fit_transform(docs)
print("矩阵形状:", X.shape)
print("稠密存储需要: %.2f GB" % (X.shape[0] * X.shape[1] * 8 / 1024 ** 3))
print("稀疏实际占用: %.2f MB" % ((X.data.nbytes + X.indices.nbytes + X.indptr.nbytes) / 1024 ** 2))
```

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 中文特征里全是单字或干脆为空 | `token_pattern` 默认要求 ≥2 个 `\w`，中文单字被过滤 | 设为 `r"(?u)\b\w+\b"`；已用 jieba 分词并空格连接时尤其重要 |
| 测试集准确率异常低但训练集很高 | 对测试集调用了 `fit_transform`，重学了词表 | 测试/推理一律用 `transform`，`fit` 只在训练集上做 |
| 报错 "X has n features, expecting m" | 训练与推理用了两个不同的 vectorizer 实例 | 把 vectorizer 与模型一起持久化（`joblib.dump`），推理时同时加载 |
| 内存爆掉 | 用了稠密数组存词袋矩阵 | 保持 CSR 稀疏格式，或上 `HashingVectorizer` |
| 关键词权重不高、「的/是」权重反而高 | 没加停用词、也没设 `max_df` | 传 `stop_words` 列表（中文需自备），并设 `max_df=0.8~0.95` |
| 长文档的分类得分普遍偏高 | TF 用了原始计数，未归一化 | `norm='l2'`，或 TF 用频率 / `sublinear_tf=True` |
| 「我爱你」与「你爱我」无法区分 | 词袋丢失词序 | 加 `ngram_range=(1,2)`，或改用第 04/09 篇的序列模型 |
| `max_features` 设得太小，效果骤降 | 稀有但关键的判别词被截掉（如「退款」「投诉」） | 先不加限制看总维度，再逐步收紧；结合 `feature_importances_` 检查 |
| 推理时出现训练集没有的新词，直接消失 | 词袋无法处理 OOV（无对应列） | 接受丢弃，或改用 `HashingVectorizer` / 子词（第 02 篇）、词向量（第 04 篇） |
| 两次运行结果不可复现 | 词表顺序、`max_features` 并列时的选择不确定 | 固定 `random_state`，并把 vectorizer 持久化复用 |

## 5. 面试问答

**Q1. 请解释 TF-IDF 的公式，以及为什么它能衡量词的重要性？**

<details><summary>参考答案</summary>

$$\text{TF-IDF}(t,d)=\text{TF}(t,d)\times\text{IDF}(t),\qquad \text{IDF}(t)=\log\frac{N}{\text{DF}(t)}$$

- **TF** 表示词 $t$ 在文档 $d$ 中出现的次数（或其归一化/对数形式）。出现越多，越可能与这篇文档的主题相关。
- **IDF** 表示词 $t$ 的稀有程度：$\text{DF}(t)$ 是包含该词的文档数，$N$ 是总文档数。词越普遍（DF 越大），IDF 越小。

两部分相乘的含义是**「局部频繁」且「全局稀有」的词最有判别力**。"的」局部频繁但全局也频繁，IDF 接近 0，乘积很小；「量子计算」局部可能只出现 1 次，但全局稀有，IDF 很大，乘积就大。

工程上要注意两件事：① TF 必须归一化或取对数，否则长文档所有词得分都会被抬高；② sklearn 默认实现是带平滑的 $\log\frac{1+N}{1+DF}+1$，因此即使某词出现在所有文档中，IDF 也是 1 而不是 0，这与教科书朴素形式不同。

</details>

**Q2. 词袋模型的两大缺陷是什么？各自怎么缓解？**

<details><summary>参考答案</summary>

**缺陷一：丢失词序**。"我爱你」与「你爱我」的词频向量完全相同，模型无法区分否定、主宾颠倒等语序敏感现象。

缓解手段：
- 加入 **n-gram 特征**（`ngram_range=(1,2)`），把相邻词的组合作为新特征，等于局部地把词序编码进特征。代价是维度按 $V^n$ 膨胀，必须配合 `min_df` 剪枝。
- 使用**序列模型**（RNN / CNN / Transformer），从根本上建模顺序信息。

**缺陷二：丢失词的重要性**。高频虚词（的、是、了）会主导向量，真正的判别词被淹没。

缓解手段：
- **TF-IDF 加权**，用 IDF 压低普遍词的权重。
- **停用词过滤**与 **`max_df`**：直接把出现在绝大多数文档中的词删掉。
- **`sublinear_tf`**：用 $1+\log f$ 抑制高频词的数值优势。

这两条也解释了为什么在现代深度模型里，词袋 + n-gram + TF-IDF 仍是文本分类的强基线：它用极低的成本换来大部分「词形层面」的判别信息，而语义层面的缺口才需要词向量和预训练模型来补。

</details>

**Q3. 为什么 sklearn 的 `TfidfVectorizer` 默认要加 `smooth_idf` 和 L2 归一化？**

<details><summary>参考答案</summary>

**`smooth_idf=True`** 把 IDF 从 $\log\frac{N}{\text{DF}}$ 改成

$$\log\frac{1+N}{1+\text{DF}}+1$$

两个作用：① 避免 `DF=0`（推理阶段的新词）导致除零或 $\log 0$；② 最后整体 +1，使得出现在所有文档中的词 IDF 取 1 而不是 0，保留一点权重、不至于完全消失。工程上这更稳健：语料规模变化时权重不会剧烈跳动。

**L2 归一化**把每个文档向量除以其 L2 范数：

$$\tilde v=\frac{v}{\lVert v\rVert_2}$$

作用是消除**文档长度**的影响。不做归一化时，长文档的非零项更多、范数更大，与任何查询的点积都偏大，检索时会「长文档通吃」。归一化后两个向量的点积就等于余弦相似度，只与方向（即词的相对分布）有关，与长度无关。

附带好处：L2 归一化让特征数值范围稳定在 $[0,1]$，便于线性模型收敛，也让稀疏矩阵的数值更均匀。

</details>

**Q4. 特征维度太高（比如 50 万）怎么办？请给出至少三种手段并说明取舍。**

<details><summary>参考答案</summary>

| 手段 | 做法 | 取舍 |
|------|------|------|
| 词表裁剪 | `max_features=50000`、`min_df=2~5`、`max_df=0.8~0.95` | 最常用、最有效；风险是截掉稀有但关键的判别词，需要看特征重要性验证 |
| 停用词过滤 | 传中文停用词表；或用 `max_df` 自动近似 | 简单，但通用停用词表可能删掉任务关键词（如情感分析里的「不」） |
| 降维 | TruncatedSVD / LSA 把 5 万维压到 200–500 维 | 能显著缩小模型、提升泛化；但**语义可解释性丢失**，且 SVD 本身是额外计算 |
| 特征选择 | 用卡方（`chi2`）、互信息选 top-k | 与标签相关的筛选更有针对性，属于有监督方法；需要交叉验证避免过拟合 |
| 哈希技巧 | `HashingVectorizer` 固定维度、无需词表 | 内存恒定、支持在线学习；但哈希冲突不可逆，无法回看特征名 |
| 换表示 | 改用词向量 / 预训练模型 | 语义更强、维度更低（通常 768 反而小于 5 万），但需要 GPU 与更多数据 |

实践顺序建议：先 `min_df=2` + `max_df=0.9` 做无监督裁剪，再看维度是否可接受；仍过大时加 `max_features`；如果模型训练慢或过拟合明显，再考虑 TruncatedSVD 或换稠密表示。

</details>

## 6. 自测题

**1. 语料有 4 篇文档，`N=4`。词「苹果」出现在 2 篇文档中。请分别用朴素 IDF 与 sklearn 平滑 IDF 计算它的 IDF 值。**

<details><summary>参考答案</summary>

朴素形式：

$$\text{IDF} = \log\frac{N}{\text{DF}} = \log\frac{4}{2} = \log 2 \approx 0.6931$$

sklearn 默认（`smooth_idf=True`）：

$$\text{IDF} = \log\frac{1+N}{1+\text{DF}} + 1 = \log\frac{5}{3} + 1 \approx 0.5108 + 1 = 1.5108$$

可见 sklearn 的值明显更大——因为有 +1 的平移。这提醒我们：**不同库的 IDF 定义不可直接比较**，跨库迁移模型时必须连 vectorizer 一起迁移，或者自己统一实现。

顺便：若「苹果」出现在全部 4 篇中，朴素 IDF = $\log 1 = 0$（权重归零），而 sklearn 为 $\log\frac{5}{5}+1 = 1$（仍保留一点权重）。

</details>

**2. 判断：「词袋模型的向量长度等于文档的词数。」**

<details><summary>参考答案</summary>

错。词袋向量的长度等于**词表大小 $V$**（语料去重后的词数），而不是某篇文档的词数。文档的词数只决定了向量中非零元素的个数。

例如词表是 `[猫, 狗, 喜欢, 鱼, 骨头, 打架]`（$V=6$），文档「猫 喜欢 鱼」的词袋向量是 `(1,0,1,0,1,0)` —— 长度 6，非零项 3 个。

这也解释了为什么词袋矩阵是高度稀疏的：$V$ 通常几万，而一篇文档只有几十个词，稀疏度常在 99.9% 以上。

</details>

**3. 把 `ngram_range` 从 `(1,1)` 改成 `(1,2)`，特征维度大约会变成多少？会带来什么问题？**

<details><summary>参考答案</summary>

维度从 $V$ 变为 $V + V_{\text{bigram}}$，其中 $V_{\text{bigram}}$ 是实际出现过的 bi-gram 种类数，理论上界是 $V^2$，实际取决于语料规模，通常会让总维度增长 3–10 倍。

带来的问题：

1. **稀疏度上升、内存与训练时间增加**。
2. **过拟合风险**：bi-gram 中大量组合只出现 1–2 次，几乎是噪声，模型容易记住它们。必须配合 `min_df=2` 以上裁剪。
3. **OOV 更严重**：推理时的新词组合完全无法匹配。
4. **长文档收益递减**：文档越长，任意 bi-gram 的判别力越弱。

实践做法：短文本（评论、标题、query）用 `(1,2)` 通常有收益；长文档（新闻正文、报告）用 `(1,1)` 更划算。改完一定要用交叉验证确认收益，而不是凭感觉开。

</details>

**4. 为什么推理阶段必须用 `transform` 而不是 `fit_transform`？**

<details><summary>参考答案</summary>

`fit` 会从传入数据中**学习**词表（`vocabulary_`）和 IDF 权重；`transform` 只是**套用**已学到的映射做编码。训练集用 `fit_transform` 正确，推理阶段再用 `fit_transform` 会重新学一套映射，两个后果：

1. **特征空间错位或维度不匹配**：新词表长度可能不同，直接报 "X has n features, but ... expecting m"；若恰好长度相同，列的含义也已不同（训练时第 3 列是「很好」，推理时可能变成「很差」），输出完全不可信且**不会报错**——这是最危险的情况。
2. **IDF 漂移**：IDF 从推理数据的文档频率重新统计，而单条或少量样本的 DF 统计毫无意义（DF 非 0 即 1），权重严重失真。

正确做法：把 vectorizer 与模型一起持久化（`joblib.dump({"vec": vec, "clf": clf}, path)`），推理时一起加载。

</details>

**5. 在新闻分类任务里，TF-IDF + 线性模型已经能到 0.85 准确率，为什么还需要 BERT？请说出 TF-IDF 表示法的三个根本局限。**

<details><summary>参考答案</summary>

三个根本局限：

1. **无同义/语义泛化能力**：「宾馆」和「酒店」、「心肌梗死」和「心梗」在 TF-IDF 空间里完全正交，模型必须见过每一个具体词形才能学到对应关系。而 BERT 通过预训练把语义相近的表示拉近，可以零样本泛化到训练时未见过的同义表达。
2. **无上下文消歧**：「苹果」在「苹果手机」和「吃苹果」中是同一个特征列，模型无法区分词义；BERT 的表示是上下文相关的，同一个词在不同语境下向量不同。
3. **无词序建模（除非显式加 n-gram）**：「不推荐这家酒店」与「推荐这家酒店」在有停用词过滤后可能几乎同形，极易判错；n-gram 只能局部缓解，且带来维度爆炸和稀疏问题。

此外还有工程层面的差异：TF-IDF 需要人工设计特征裁剪与停用词，跨领域迁移时要重新调参；而预训练模型通过微调可以直接适配新领域，只是代价是算力（需要 GPU）和推理延迟。

补充：实践中并不总是「BERT 替代 TF-IDF」。在低延迟、无 GPU、标注量小的场景，TF-IDF + 线性模型仍是首选；常见方案是用 BERT 蒸馏一个小模型（见第 12 篇），或把 TF-IDF 特征与词向量特征拼接使用。

</details>

## 7. 延伸阅读

- sklearn `TfidfVectorizer` 官方文档（含 `smooth_idf`、`sublinear_tf`、`norm` 的精确定义）：https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- sklearn 文本特征提取用户指南（含 `HashingVectorizer` 与大规模场景建议）：https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- scipy 稀疏矩阵（CSR/CSC）官方说明：https://docs.scipy.org/doc/scipy/reference/sparse.html
- 《Introduction to Information Retrieval》第 6 章 Scoring, Term Weighting, and the Vector Space Model（TF-IDF 的经典推导）：https://nlp.stanford.edu/IR-book/html/htmledition/scoring-term-weighting-and-the-vector-space-model-1.html
- 《Speech and Language Processing》第 2 章（n-gram 与文本规范化）：https://web.stanford.edu/~jurafsky/slp3/
- 中文停用词表（百度 / 哈工大 / 四川大学等多份可选）：https://github.com/goto456/stopwords

---

[⬅️ 返回 NLP 目录](README.md)
