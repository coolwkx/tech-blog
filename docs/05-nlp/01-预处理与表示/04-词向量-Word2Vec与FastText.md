# 04 词向量：Word2Vec 与 FastText

> **一句话总结**：用「上下文相似的词，向量也该相似」这一条自监督信号，把稀疏的 one-hot 换成低维稠密、带语义距离的词向量。
> **前置知识**：第 03 篇的 one-hot 与词袋、softmax 与交叉熵、PyTorch `nn.Embedding` 的基本用法。

> 1. 手推 CBOW 与 Skip-gram 的网络结构、输入输出维度，并说清两者的取舍。
> 2. 解释负采样为什么把 $O(V)$ 的 softmax 降成 $O(k)$ 的二分类，并写出其损失函数。
> 3. 用 gensim / fastText 训练词向量，做相似度与词向量类比的定量评估，并说明 FastText 处理 OOV 的原理。

## 1. 核心概念

### 1.1 从 one-hot 到分布式表示

| 对比项 | one-hot | word2vec / 词向量 |
|--------|---------|-------------------|
| 维度 | 词表大小 $V$（几万～几十万） | 100–300 |
| 稠密性 | 稀疏，只有一个 1 | 稠密，每维都是实数 |
| 相似词 | 余弦相似度恒为 0 | 余弦相似度有意义（酒店 ≈ 宾馆） |
| 可迁移性 | 无 | 可作为下游模型的初始化参数 |
| 训练方式 | 无需训练 | 自监督（无监督）训练 |

word2vec 的本质是一句很精炼的话：**训练一个模型，把模型的参数矩阵当作所有词的词向量表示**。所以它既是「一种训练方法」，产物又是「一张词向量表」。矩阵的第 $i$ 行（或列）就是第 $i$ 个词的向量。

### 1.2 分布假设

一切词向量方法都建立在一个语言学假设上——**分布式假设（distributional hypothesis）**：一个词的含义由它经常出现的上下文决定。因此，只要让「上下文相似的词」在向量空间里靠近，就等价于学到了语义。

这也解释了为什么词向量是**自监督**的：不需要任何人工标注，只要有大段文本，就能用「预测上下文 / 用上下文预测中心词」这一任务构造出监督信号。

### 1.3 CBOW 与 Skip-gram

| 对比项 | CBOW（连续词袋） | Skip-gram（跳字） |
|--------|------------------|-------------------|
| 任务 | 用上下文预测中心词 | 用中心词预测上下文 |
| 输入 | 窗口内 $2c$ 个上下文词 | 1 个中心词 |
| 输出 | 1 个中心词 | 窗口内 $2c$ 个上下文词 |
| 上下文处理 | 对上下文向量取**平均**后送入投影层 | 每个上下文位置单独预测 |
| 训练速度 | 快（一次梯度更新学 $2c$ 个词的信息） | 慢（每个上下文位置都要算一次） |
| 低频词效果 | 较差（平均会稀释低频词信号） | 更好（每个上下文都是独立监督） |
| 常见选择 | 大规模语料、追求速度 | 小语料、关注低频词与语义质量 |

一句话选型：**语料大、要快用 CBOW；语料小、要语义质量（尤其低频词）用 Skip-gram**。fastText 的 `train_unsupervised` 默认就是 Skip-gram。

### 1.4 输出层的两种加速方案

词表 $V$ 有几万时，每次预测都要在 $V$ 维上做 softmax，代价高到不可接受。两种经典加速：

| 方案 | 思路 | 单步复杂度 | 特点 |
|------|------|-----------|------|
| 层次 Softmax（Hierarchical Softmax） | 用 Huffman 树组织词表，把「$V$ 分类」变成「从根走到叶」的一系列二分类 | $O(\log V)$ | 无近似、数学精确；Huffman 树让高频词路径更短 |
| 负采样（Negative Sampling） | 把「$V$ 分类」改成「真样本 vs $k$ 个噪声样本」的二分类 | $O(k)$，$k$ 常取 5–20 | 更简单更快，NEG 是 word2vec 论文的推荐方案 |

### 1.5 FastText 的两个创新

FastText 由 Facebook 提出，是一个「词向量 + 文本分类」的开源工具，与原版 word2vec 相比有两处关键改动：

**创新一：子词（subword）表示。** 每个词不只用一个向量，而是「词向量 + 其所有字符 n-gram 向量」之和。例如 `where`（设 $n=3$）会被拆成 `<wh, whe, her, ere, re>` 加上整词 `<where>`，词向量为：

$$
v_{\text{where}} = \frac{1}{|G|}\sum_{g \in G} z_g
$$

其中 $G$ 是整词与所有 n-gram 的集合。带来的直接好处是**OOV 也能有向量**：训练时见过「肾结石」「胆结石」，遇到未见过的「尿结石」，可以用共享的子词（尿、结、石）拼出一个合理向量。

**创新二：分类头结构极简。** 文本分类时，FastText = 「所有词的向量取平均」+「一层线性分类器」+「softmax」：

$$
\hat{y} = \text{softmax}\big(W \cdot \tfrac{1}{n}\sum_{i=1}^{n} v_{w_i} + b\big)
$$

没有卷积、没有循环、没有注意力，只有一层隐式表示。但正因为简单，它训练极快（几分钟到几十分钟）、推理极快（毫秒级）、模型文件小，在文本分类上常能超过同期的复杂模型，是性价比极高的基线。

### 1.6 静态词向量的局限

| 局限 | 说明 | 例子 |
|------|------|------|
| 一词多义无法区分 | 每个词只有唯一向量 | 「苹果」在「苹果手机」与「吃苹果」中向量相同 |
| 无上下文 | 推理时不看句子，查表即可 | 「银行」在「河岸」和「金融机构」义项下无差别 |
| 无法建模句法/角色 | 只知道词是否常共现 | 「猫追狗」与「狗追猫」词向量集合相同 |

这三点正是 ELMo / BERT 的动机（见第 09 篇）：把「静态向量」换成「上下文相关的动态表示」。

## 2. 方法细节

### 2.1 CBOW 的前向与维度变化

设词表大小 $V$、词向量维度 $N$、窗口半径 $c$：

1. **输入**：$2c$ 个上下文词的 one-hot，$x^{(1)},\dots,x^{(2c)} \in \mathbb{R}^V$。
2. **投影**：共享一个输入矩阵 $W \in \mathbb{R}^{V \times N}$，得到 $v_i = W^\top x^{(i)}$（即查表得到该词的 $N$ 维向量）。
3. **平均**：$h = \frac{1}{2c}\sum_i v_i \in \mathbb{R}^N$。这一步是 CBOW 名字的由来——把上下文当成一个无序的「词袋」。
4. **输出**：$u = W'^\top h \in \mathbb{R}^V$，其中 $W' \in \mathbb{R}^{N \times V}$ 是输出矩阵。
5. **softmax**：$\hat y_j = \dfrac{\exp(u_j)}{\sum_{j'=1}^{V}\exp(u_{j'})}$。
6. **损失**：与真实中心词的 one-hot 做交叉熵。

**Skip-gram** 只是把 2–6 步反过来：输入 1 个中心词的 one-hot，对其 $2c$ 个上下文位置各做一次上述预测，总损失是各位置交叉熵之和。

训练完成后，通常用 $W$（输入矩阵）的转置作为词向量表；也有实现把 $W$ 与 $W'$ 相加或拼接。

### 2.2 负采样的动机与损失

对每个训练样本，原 softmax 需要对全部 $V$ 个词求指数并归一化，梯度计算量是 $O(V \cdot N)$。负采样把它替换成**二分类**：

- **正样本**：真实出现的 (中心词, 上下文词) 对，标签 1。
- **负样本**：从噪声分布 $P_n(w)$ 中随机抽 $k$ 个词与中心词配对，标签 0。

单个 (中心词 $w$, 上下文 $c$) 对的损失为

$$
\ell = -\log\sigma(u_o^\top v_c) - \sum_{i=1}^{k} \mathbb{E}_{w_i \sim P_n(w)}\Big[\log\sigma(-u_{w_i}^\top v_c)\Big]
$$

其中 $\sigma$ 是 sigmoid。复杂度从 $O(V)$ 降到 $O(k)$，$k$ 通常取 5–20。

噪声分布不用均匀分布，而用**词频的 3/4 次幂**：

$$
P_n(w) = \frac{\text{count}(w)^{3/4}}{\sum_{w'}\text{count}(w')^{3/4}}
$$

原因是均匀采样会让低频词被抽得太频繁（噪声太大），纯按词频又会让 the/of 这类高频词占满负样本（区分度太低）。3/4 次幂是一个经验上的折中：**抬高低频词的采样概率，同时压低高频词**。

### 2.3 训练技巧与超参数

| 技巧/参数 | 做法 | 原因 |
|-----------|------|------|
| 高频词下采样（subsampling） | 以概率 $P(w_i)=1-\sqrt{t/f(w_i)}$ 丢弃词（$t\approx10^{-5}$） | the / 的 这类词提供的信息极少，却贡献大量样本；丢弃后训练更快、低频词表示更好 |
| 窗口大小 | 小窗口（2–5）偏句法相似词；大窗口（5–15）偏主题相似词 | 窗口决定「上下文」的定义范围 |
| 动态窗口 | 每步从 $[1, c]$ 中随机取窗口大小 | 让近邻获得更高权重（近的词被采样的概率更高），同时兼顾远距离 |
| 负采样数 $k$ | 小语料 5–20，大语料 2–5 | 语料越大，单次更新已足够，减少 $k$ 提速 |
| 词向量维度 | 100–300 | 太小表达不足，太大易过拟合且下游不好用 |
| 迭代轮数 | 5–15 | 语义任务通常需要多于分类任务 |
| 参数初始化 | 小均匀分布 $U(-0.5/N, 0.5/N)$ | 与 one-hot 输入的量级匹配 |

### 2.4 词向量的评估方法

评估分两类，缺一不可：

| 类型 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| 内在评估（intrinsic） | 相似度任务（WordSim-353、Spearman 相关）；类比任务（king − man + woman = ?） | 快、无需下游任务、直接反映语义质量 | 与下游性能不完全一致 |
| 外在评估（extrinsic） | 把词向量接入具体任务（分类、NER）看指标 | 直接反映实用价值 | 慢，且受下游模型影响 |

词向量类比的标准形式：$v_a - v_b + v_c$ 的最近邻（排除 $a,b,c$ 本身）。

### 2.5 词向量迁移的两种方式

训练好的词向量可以作为下游模型的初始化：

| 方式 | 做法 | 适用 |
|------|------|------|
| 冻结（freeze） | 加载预训练向量到 `nn.Embedding`，`requires_grad=False`，只训练后续层 | 下游数据很少（防止 embedding 被小数据带偏） |
| 微调（fine-tune） | 加载后继续参与训练，可全部或部分解冻 | 下游数据充足、领域与预训练语料有差异 |

工业上的折中做法：**分层学习率**——embedding 层用很小的学习率（如 1e-5），上层用正常学习率。

## 3. 可运行示例

### 3.1 用 gensim 训练并在小语料上评估

```python
# 依赖: pip install gensim
from gensim.models import Word2Vec

# 内联小语料（实际项目里换成分词后的大规模句子列表）
sentences = [
 "我 喜欢 自然语言处理".split,
 "自然语言处理 是 人工智能 的 分支".split,
 "机器学习 和 深度学习 是 人工智能 的 技术".split,
 "深度学习 需要 大量 数据 和 算力".split,
 "词向量 是 自然语言处理 的 基础".split,
 "我喜欢 机器翻译 和 文本分类".split,
] * 20 # 小语料重复几次，保证词频足够

model = Word2Vec(
 sentences,
 vector_size=50, # 词向量维度
 window=3, # 上下文窗口
 min_count=1, # 小语料演示用 1；实际项目一般 5
 sg=1, # 1 = Skip-gram，0 = CBOW
 negative=5, # 负采样个数
 epochs=30,
 seed=42,
)

print("词表大小:", len(model.wv))
print("词向量维度:", model.wv["自然语言处理"].shape)
print("与'深度学习'最相近:", [w for w, _ in model.wv.most_similar("深度学习", topn=3)])

# 类比实验：a - b + c，看最近邻
try:
 res = model.wv.most_similar(positive=["人工智能", "数据"], negative=["深度学习"], topn=3)
 print("类比结果:", res)
except KeyError as e:
 print("词表中缺少词:", e)
```

注意 `min_count=1` 只适用于这种演示；真实语料若用 1，会保留大量只出现一次的词，既拖慢训练又几乎学不到有意义的向量。

### 3.2 纯 numpy 实现负采样损失与梯度（看清数学）

```python
# 依赖: pip install numpy
import numpy as np

np.random.seed(0)

V, N, k = 8, 4, 3 # 词表大小、向量维度、负样本数
W_in = np.random.randn(V, N) * 0.1 # 输入矩阵（词向量表）
W_out = np.random.randn(N, V) * 0.1 # 输出矩阵

center, context = 0, 1
negatives = [3, 5, 6] # 简化：直接给定负样本

def sigmoid(x):
 return 1.0 / (1.0 + np.exp(-x))

v_c = W_in[center] # 中心词向量
loss, grads = 0.0, {}

def step(target, label):
 """对单个 (中心词, 目标词) 对做一次二分类的前向与梯度"""
 global loss
 u = W_out[:, target]
 score = float(v_c @ u)
 p = sigmoid(score)
 # 交叉熵: label=1 -> -log(p); label=0 -> -log(1-p)
 loss += -(np.log(p) if label == 1 else np.log(1 - p))
 grads[target] = ((p - label) * u, (p - label) * v_c) # (dv_c 的贡献, dW_out[:, target])

step(context, 1) # 正样本
for n in negatives:
 step(n, 0) # k 个负样本

# 汇总梯度并做一次梯度下降
dv_c = sum(g[0] for g in grads.values)
lr = 0.1
W_in[center] -= lr * dv_c
for target, (_, dwo) in grads.items:
 W_out[:, target] -= lr * dwo

print(f"负采样总损失: {loss:.4f}")
print(f"中心词向量更新量范数: {np.linalg.norm(lr * dv_c):.4f}")
print(f"复现检查: 复杂度 = O(k+1) = {k + 1} 次点积，而非 O(V) = {V}")
```

这个例子把「$V$ 分类 → $k+1$ 个二分类」的等价性摊开：正样本把中心词向量往上下文词方向拉，负样本把它推离噪声词。

### 3.3 FastText：分类 + 词向量 + OOV

```python
# 依赖: pip install fasttext （若不成功可尝试 pip install fasttext-wheel）
import os
import tempfile
import fasttext

workdir = tempfile.mkdtemp

# FastText 分类要求每行「__label__类别 文本」
train_path = os.path.join(workdir, "train.txt")
with open(train_path, "w", encoding="utf-8") as f:
    for text, label in [
    ("肾结石 一般 用 什么 药", "治疗"),
    ("胆结石 怎么 治疗 效果好", "治疗"),
    ("心肌梗死 症状 是 什么", "症状"),
    ("脑梗死 表现 有哪些", "症状"),
    ("如何 预防 糖尿病", "预防"),
    ("怎么 预防 高血压", "预防"),
    ] * 20:
        f.write(f"__label__{label} {text}\n")

        model = fasttext.train_supervised(
        input=train_path,
        lr=0.5,
        epoch=25,
        dim=100,
        wordNgrams=2, # 加 bi-gram，部分恢复词序
        loss="softmax", # 多分类用 softmax；类别极多时可用 'ova' 或 'hs'
        verbose=0,
        )
        model.save_model(os.path.join(workdir, "cls.bin"))

        # 测试集：故意用训练集里没出现过的词「尿结石」
        test_path = os.path.join(workdir, "test.txt")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("__label__治疗 尿结石 用 什么 药\n")
            f.write("__label__症状 心梗 的 表现\n")

            n, precision, recall = model.test(test_path)
            print(f"样本数={n} 准确率={precision:.4f} 召回率={recall:.4f}")

            labels, probs = model.predict("尿 结石 用 什么 药", k=2)
            print("预测标签:", labels, "概率:", probs)
            print("OOV 演示 —— '尿结石' 的向量（子词拼出来）:", model.get_word_vector("尿结石").shape)

            # 还可以用 FastText 无监督训练词向量（相当于原版 word2vec）
            unsup_path = os.path.join(workdir, "unsup.txt")
            with open(unsup_path, "w", encoding="utf-8") as f:
                for s in ["猫 喜欢 鱼", "狗 喜欢 骨头", "猫 和 狗 都 是 宠物"] * 50:
                    f.write(s + "\n")
                    vec_model = fasttext.train_unsupervised(unsup_path, model="skipgram", dim=50, epoch=20, verbose=0)
                    print("'猫' 的最近邻:", vec_model.get_nearest_neighbors("猫"))
```

`get_word_vector("尿结石")` 能正常返回向量，正是因为 FastText 用子词合成，而不是查一张固定的词表。

### 3.4 把预训练词向量迁移进 PyTorch 模型

```python
# 依赖: pip install torch gensim
import torch
import torch.nn as nn

vocab = ["<pad>", "<unk>", "肾结石", "治疗", "方法"]
word2id = {w: i for i, w in enumerate(vocab)}

# 假设从 gensim/keyedvectors 取到的向量（这里用随机值占位）
import numpy as np
pretrained = np.random.randn(len(vocab), 6).astype("float32")

# 关键：padding_idx 必须与 <pad> 一致，否则 PAD 也会被学成有语义的向量
embedding = nn.Embedding.from_pretrained(
torch.tensor(pretrained), freeze=False, padding_idx=word2id["<pad>"]
)

ids = torch.tensor([word2id[w] for w in ["肾结石", "治疗"]])
print(embedding(ids).shape) # [2, 6]

# 分层学习率：embedding 用 1e-5，分类头用 1e-3
optimizer = torch.optim.Adam([
{"params": embedding.parameters, "lr": 1e-5},
], lr=1e-3)
print("OK")
```

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 训练出的词向量「语义很差」，近邻都是高频虚词 | 语料太小或 `min_count=1` 导致大量噪声词 | 增大语料；`min_count=5` 起；去掉停用词或对高频词下采样 |
| 相似度查询报 `KeyError` | 该词未进词表（被 `min_count` 过滤或不在语料中） | 先用 `w in model.wv` 判断；用 FastText 子词方案天然规避 |
| CBOW 效果明显不如 Skip-gram | CBOW 对上下文取平均，稀释了低频词信号 | 小语料改用 Skip-gram（`sg=1`），或加大负采样数 |
| 训练极慢 | 词表大 + 用了层次 softmax + 未下采样高频词 | 用负采样（`negative=5`）、开启下采样（`sample=1e-5`） |
| 词向量维度设成 1000 后下游变差 | 维度大 → 参数量大，小语料上严重过拟合 | 100–300 通常足够；用下游任务验证 |
| 加载预训练向量后 PAD 也有语义 | 未设置 `padding_idx`，或该行初值非 0 | `nn.Embedding.from_pretrained(..., padding_idx=pad_id)`，并保证 pad 行为全 0 |
| 微调后效果反而下降 | 下游数据太少，embedding 被小数据带偏 | 冻结 embedding（`freeze=True`），或分层学习率（embedding 用 1e-5） |
| FastText 分类中文效果差 | 输入未分词，整句变成一个「词」 | 先用 jieba 分词并以空格连接；或开启 `wordNgrams=2` |
| `fasttext.train_supervised` 报标签格式错误 | 标签前缀必须是 `__label__`，且标签与文本用空格分隔 | 严格写 `__label__治疗 肾结石 用 什么 药` |
| 类比实验（king-man+woman）结果荒谬 | 小语料学不出线性结构；或 `most_similar` 未排除输入词 | 类比需要大数据集（>1 亿词）；用 `restrict_vocab` 与排除项 |

## 5. 面试问答

**Q1. CBOW 和 Skip-gram 有什么区别？实际项目怎么选？**

<details><summary>参考答案</summary>

| 维度 | CBOW | Skip-gram |
|------|------|-----------|
| 任务方向 | 上下文 → 中心词 | 中心词 → 上下文 |
| 输入/输出 | $2c$ 个词 → 1 个词 | 1 个词 → $2c$ 个词 |
| 上下文聚合 | 取平均后送入投影层 | 每个上下文位置独立预测 |
| 计算量 | 小（一次更新利用 $2c$ 个词） | 大（每个上下文位置都要算） |
| 低频词表现 | 差（平均会稀释信号） | 好（每个上下文都是独立监督） |
| 适合 | 大语料、追求训练速度 | 小语料、追求语义质量 |

选择建议：语料规模在亿级、训练时间受限时用 CBOW；语料在千万级以下、关心低频词与语义质量时用 Skip-gram（fastText 的默认选择）。也可以两者都训一遍，用**内在评估**（相似度/类比）加**下游任务**指标来定，不要凭直觉。

</details>

**Q2. 为什么需要负采样？噪声分布为什么要用词频的 3/4 次幂？**

<details><summary>参考答案</summary>

**为什么需要**：原始 word2vec 的输出层是 $V$ 分类 softmax，每一步都要对全部 $V$ 个词求指数与归一化，单步计算量 $O(V\cdot N)$。$V$ 是几万到几十万时，训练不可接受。

负采样把问题转化为**二分类**：对每个真实出现的 (中心词, 上下文) 正样本，配 $k$ 个随机噪声词作为负样本，用 sigmoid + 二值交叉熵训练：

$$\ell=-\log\sigma(u_o^\top v_c)-\sum_{i=1}^{k}\log\sigma(-u_{w_i}^\top v_c)$$

复杂度变为 $O(k)$（$k$ 常取 5–20），且模型只需学会「区分真实上下文与噪声」，这已足以让共现词的向量靠近。

**为什么用 $P_n(w)\propto \text{count}(w)^{3/4}$**：这是一个折中。

- 用**均匀分布**：低频词被采样得过于频繁，噪声太大，模型学不到有意义的区分，且高频词几乎不参与负样本。
- 用**原始词频**：负样本几乎被 the / of / 的 这类词垄断，模型只学会区分这些词，对其他词无区分度。
- 用 **3/4 次幂**：抬高低频词的概率、压低高频词的概率，使得采样分布更接近「有信息量」的词。这是论文中的经验取值，效果最好。

</details>

**Q3. FastText 怎么解决 OOV？它和 word2vec、BERT 的表示有什么本质区别？**

<details><summary>参考答案</summary>

**FastText 解决 OOV 的机制**是**子词（subword）合成**：每个词的向量不是查表得到，而是由「整词 + 所有字符 n-gram」的向量求和（或平均）得到：

$$v_w=\frac{1}{|G|}\sum_{g\in G}z_g,\quad G=\{\text{词本身}\}\cup\{\text{所有长度 3--6 的字符 n-gram}\}$$

遇到训练时未见过的词，它的字符 n-gram 大概率都见过，因此仍能合成一个合理向量。极端情况下退化为字符级，永远不会出现「没有向量」。

**三者表示的本质区别**：

| 方法 | 表示 | 上下文相关 | OOV 处理 | 词序 |
|------|------|-----------|----------|------|
| word2vec | 静态查表，一词一向量 | 否 | 无法处理 | 不建模 |
| FastText | 静态、由子词合成 | 否 | 子词合成 | 分类时用 wordNgrams 部分建模 |
| BERT | 动态，由整个上下文计算 | 是 | 子词（WordPiece）+ 上下文 | self-attention 全局建模 |

关键差别在「静态 vs 动态」：word2vec 和 FastText 都是**静态词向量**，训练完就把向量表固定了，「苹果」永远只有一个向量；BERT 的每个 token 表示由整句上下文算出，因此能区分一词多义。这也是为什么后续章节要进入预训练模型。

</details>

## 6. 自测题

**1. 设词表 $V=10000$、词向量维度 $N=100$、窗口半径 $c=2$。分别写出 CBOW 与 Skip-gram 一次训练样本的输入输出形状。**

<details><summary>参考答案</summary>

**CBOW**（用 4 个上下文词预测 1 个中心词）：

- 输入：$x^{(1)},\dots,x^{(4)}$，每个是 $V=10000$ 维 one-hot；查表后得到 $4$ 个 $100$ 维向量
- 投影层（平均）：$h\in\mathbb{R}^{100}$
- 输出：$u\in\mathbb{R}^{10000}$，经 softmax 得 10000 维概率分布
- 标签：中心词的 one-hot（$10000$ 维）

**Skip-gram**（用 1 个中心词预测 4 个上下文词）：

- 输入：1 个 $10000$ 维 one-hot（或直接查表得 $100$ 维向量）
- 输出：4 组 $10000$ 维概率分布（每个上下文位置一组）
- 标签：4 个上下文词各自的 one-hot

注意两者参数量完全相同：输入矩阵 $W\in\mathbb{R}^{10000\times100}$、输出矩阵 $W'\in\mathbb{R}^{100\times10000}$。差别只在「一次前向产生几组预测」以及上下文是否被平均。

</details>

**2. 负采样把 $O(V)$ 降到 $O(k)$。若 $V=50000$、$k=5$，一轮训练（1 个正样本 + 5 个负样本）的计算量大约降到原来的几分之几？**

<details><summary>参考答案</summary>

原 softmax 需要 1 次完整的 $V$ 维 softmax（含 $V$ 次指数运算）+ 1 次 $N\times V$ 的梯度计算，量级按 $V=50000$ 计。

负采样只需 $k+1=6$ 次「点积 + sigmoid」以及对应的梯度，量级按 6 计。

$$\frac{k+1}{V}=\frac{6}{50000}=\frac{1}{8333}$$

即计算量降到约 **1/8000**（严格说是 $O(k)/O(V)$ 的比值，实际实现里还有常数项差异，但量级上就是这个结论）。

要注意的代价：这不是精确的 softmax，而是一种**近似目标**，因此学到的向量与真实 softmax 目标下的向量并不完全一致——但实践中下游效果相当甚至更好，因为噪声样本起到了正则化作用。

</details>

**3. 为什么说 word2vec 是「自监督」而不是「无监督」？**

<details><summary>参考答案</summary>

两者都强调「不需要人工标注」，但「自监督」更精确地描述了它的机制：**监督信号是从数据本身自动构造出来的**。

word2vec 的做法是：从原始文本中滑窗，把「上下文词 → 中心词」（CBOW）或「中心词 → 上下文词」（Skip-gram）当作预测任务，标签就是文本中真实出现的词本身。也就是说，它把无标签文本**转化**成了有监督的 (输入, 标签) 对，然后用标准分类目标训练。

这个区分在实践中很重要：它意味着自监督任务的**设计**（预测什么、怎么构造正负样本）直接决定了学到表示的质量。后来自监督学习在 NLP 中的演进（BERT 的 MLM、GPT 的下一词预测）都是在这个框架下换更好的「代理任务」。

</details>

**4. 词向量迁移到下游任务时，什么情况下该冻结 embedding、什么情况下该微调？**

<details><summary>参考答案</summary>

| 情况 | 选择 | 理由 |
|------|------|------|
| 下游数据很少（几百到几千条） | **冻结** | embedding 参数量大（$V\times N$），小数据上继续训练会严重过拟合，甚至破坏预训练学到的语义 |
| 下游数据充足（十万条以上） | **微调** | 让表示适配任务分布，通常能带来额外收益 |
| 下游领域与预训练语料差异大（医疗、法律、金融） | **微调**，且优先在领域语料上做继续预训练 | 通用语料学不到「心肌梗死」「不可抗力」这类领域语义 |
| 上游语料与下游同领域 | 冻结或微调差别不大 | 表示已经足够贴合，冻结更省算力 |

最实用的折中是**分层学习率**：embedding 层用很小的学习率（如 1e-5），上层用正常学习率（如 1e-3）。这样既能缓慢适配，又不会一步把预训练表示冲垮。

另一个细节：无论冻结与否，PAD 行都必须固定为全零向量（`padding_idx`），否则 padding 会参与注意力/池化，污染句子表示。

</details>

**5. 请设计一个评估方案，判断「我用 gensim 训出来的词向量是否比 fastText 训出来的更好」。**

<details><summary>参考答案</summary>

不能只凭感觉看几个近邻词，要分两层评估：

**第一层：内在评估（intrinsic，快，可反复迭代）**

1. **词相似度**：在人工标注的相似度数据集（WordSim-353、SimLex-999、中文可用 Wordsim-240）上计算模型相似度与人工评分的 **Spearman 相关系数**。
2. **词类比**：$a-b+c$ 的 top-1 命中率，用 Google 类比集或中文类比集；注意这需要足够大的语料，小语料上结果噪声很大。
3. **覆盖率**：两个模型的词表覆盖率、OOV 率对比。FastText 在这项上必然占优（子词合成），gensim 的 OOV 会直接失败——这也是必须记录的一项。

**第二层：外在评估（extrinsic，决定性）**

把两个词向量分别作为 embedding 初始化，接入**同一个下游模型**（如 BiLSTM 或 TextCNN 分类器），在**同一份**训练/验证/测试划分上训练、调同样的超参，比较验证集指标（macro-F1）。至少跑 3 个随机种子取均值 ± 标准差，否则差异可能在噪声范围内。

**结论呈现**：列出「维度 / 词表大小 / OOV 率 / 相似度 Spearman / 类比命中率 / 下游 macro-F1 / 训练耗时 / 模型体积」的对比表，并明确指出在哪个场景下该选哪个。通常的结论形态是：FastText 在 OOV 与低频词上占优，gensim Skip-gram 在同领域高频词上语义更细，最终取决于下游是否有大量未登录词。

</details>

## 7. 延伸阅读

- 原始论文《Efficient Estimation of Word Representations in Vector Space》(Mikolov et al., 2013)：https://arxiv.org/abs/1301.3781
- 负采样与下采样《Distributed Representations of Words and Phrases and their Compositionality》：https://arxiv.org/abs/1310.4546
- FastText 论文《Enriching Word Vectors with Subword Information》(Bojanowski et al., 2017)：https://arxiv.org/abs/1607.04606
- FastText 官方文档（`train_supervised` / `train_unsupervised` 全部参数与 autotune）：https://fasttext.cc/docs/en/options.html
- gensim Word2Vec 与 API：https://radimrehurek.com/gensim/models/word2vec.html
- GloVe 论文（另一种基于全局共现矩阵的词向量方法）：https://nlp.stanford.edu/pubs/glove.pdf

---

[⬅️ 返回 NLP 目录](README.md)
