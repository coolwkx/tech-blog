# 01 NLP 概述与文本预处理

> **一句话总结**：把人类语言变成模型能吃的「数字 + 定长张量」，这条流水线的每一步都直接决定模型上限。
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。

> 1. 说清 NLP 在 AI 体系中的位置、发展脉络与典型应用，并解释「规则派 / 统计派 / 深度学习派」的差别。
> 2. 独立完成一套中文文本预处理流水线：分词 → 词性标注 / 实体识别 → 去停用词 → n-gram → 定长填充。
> 3. 用标签分布、句子长度分布、词频词云三张图诊断语料问题，并据此确定 `max_len`、是否做数据增强。

## 1. 核心概念

### 1.1 NLP 是什么

人工智能（Artificial Intelligence, AI）的目标是让机器模仿甚至超越人的某项机能。按处理的信息模态，最常被拿来对比的三个方向是：

| 缩写 | 全称 | 处理对象 | 典型任务 |
|------|------|----------|----------|
| NLP | Natural Language Processing | 人类语言（文本 / 语音转写后的文本） | 分类、翻译、问答、摘要 |
| CV | Computer Vision | 图像、视频 | 检测、分割、识别 |
| ASR | Automatic Speech Recognition | 语音波形 | 语音转文字 |

NLP 的定义可以收紧成一句话：**让机器理解并生成人类语言**。注意「理解」和「生成」是两个方向——BERT 类模型偏理解（判别式），GPT 类模型偏生成（自回归），这也解释了后面第 09 篇为什么要分 Encoder-only / Decoder-only / Encoder-Decoder 三条技术路线。

### 1.2 发展简史：每一次跃迁都是「表示能力」的跃迁

| 时间 | 阶段 | 核心思路 | 代表 |
|------|------|----------|------|
| 1950 | 思想起点 | 图灵提出「机器能思考吗」 | Turing Test |
| 1956 | AI 元年 | 达特茅斯会议正式提出 Artificial Intelligence | — |
| 1957–1970 | 两大阵营 | 规则派 vs 统计派并行 | 语法规则解析、统计机器翻译 |
| 1994–1999 | 统计主导 | 大规模语料 + 概率模型 | n-gram 语言模型、HMM |
| 2000–2012 | 机器学习盛行 | 人工特征 + 判别式分类器 | SVM、CRF、TF-IDF |
| 2012–2022 | 深度学习主导 | 分布式表示 + 端到端训练 | word2vec、RNN/LSTM、Transformer |
| 2023– | 大模型时代 | 预训练 + 提示 / 微调 | GPT、LLaMA 等 |

两条主线要能各举一例：

- **基于规则**：人工设计语言学规则来解析句子结构，例如「一个句子由主谓宾构成」。优点是无需数据、可解释；缺点是规则爆炸、跨领域失效。
- **基于统计**：收集大规模平行语料，统计短语对齐概率，计算「给定源语言句子，目标语言句子出现的可能性」。优点是自动、可扩展；缺点是需要大量标注/平行数据，且早期特征仍靠人工设计。

### 1.3 文本预处理的五个环节

预处理处在「原始数据 → 模型输入」之间。它的作用有两个：**数据清洗**和**指导超参数选择**。

| # | 环节 | 目的 | 主要手段 |
|---|------|------|----------|
| 1 | 文本处理基本方法 | 把连续字序列切成有语义的单元 | 分词、词性标注（POS）、命名实体识别（NER） |
| 2 | 文本张量表示 | 把文本变成数字 | one-hot、word2vec、word embedding |
| 3 | 文本数据分析 | 诊断语料问题，定超参数 | 标签数量分布、句子长度分布、词频与词云 |
| 4 | 文本特征处理 | 补充特征、统一形状 | 添加 n-gram 特征、文本长度规范（补齐/截断） |
| 5 | 数据增强 | 扩充数据、缓解不均衡 | 回译（back translation）、同义词替换 |

一句话记住这五步的顺序逻辑：**先切对（1），再数字化（2），再体检（3），再整形（4），不够就造（5）**。

### 1.4 预处理的三个「为什么」

1. **为什么必须分词？** 模型能接受的最小单位通常是「词」而不是「字序列」；中文没有天然空格，需要显式切分。
2. **为什么必须统一定长？** 一个 batch 要拼成矩阵，矩阵要求每行等长；同时 GPU 的并行计算也依赖固定形状。
3. **为什么必须先做数据分析？** `max_len` 定得太小会截掉长句信息，定得太大则大量位置被 padding 浪费，注意力被无效位置稀释。

## 2. 方法细节

### 2.1 分词：三种模式与各自动机

分词的定义是：把连续的字序列，按照一定规范重新组合成词序列。jieba 提供三种切分模式，它们的**目标函数不同**：

| 模式 | API | 目标 | 粒度 | 典型用途 |
|------|-----|------|------|----------|
| 精确模式 | `jieba.lcut(s)` | 最精确地切开，无冗余 | 中 | 文本分析、分类、向量化 |
| 全模式 | `jieba.lcut(s, cut_all=True)` | 扫描出所有可能成词 | 细（有冗余） | 召回优先的场景 |
| 搜索引擎模式 | `jieba.lcut_for_search(s)` | 精确模式基础上对长词再切 | 中 + 细 | 搜索引擎索引、召回 |

精确模式与全模式的差别用一句话说清：全模式会把「人工智能」切成「人工 / 智能 / 人工智能」三者全留，且标点也会成词；精确模式只留最合理的一种切法。

### 2.2 用户自定义词典

专有名词（品牌名、领域术语）是分词错误的重灾区。jieba 支持加载自定义词典，格式为：

```
词语 词频 词性
```

其中词频和词性都可省略。加载后，jieba 会优先考虑词典里的词。工程上有两种用法：

```python
jieba.load_userdict("userdict.txt") # 全局生效
jieba.add_word("自然语言处理") # 动态加一个词
```

### 2.3 词性标注与命名实体识别

- **词性标注（POS, Part-Of-Speech tagging）**：给每个词标上词性（名词 n、动词 v、形容词 a、代词 r 等）。`jieba.posseg` 返回的对象同时带 `word` 和 `flag` 两个属性，天然适合做「筛形容词」这类操作。
- **命名实体识别（NER, Named Entity Recognition）**：从文本中识别专有名词。常见 7 类实体：人名、地名、机构名、时间、日期、货币、百分比。

NER 的标准两阶段拆解（面试高频）：

1. **边界识别**——判断每个 token 属于哪个实体的哪个位置，是 **token 级分类**（序列标注任务，见第 06 篇）。
2. **span 分类**——把识别出的实体片段归到具体类型（人物 / 地点 / 机构），可以看成 **句子级分类**。

### 2.4 one-hot：最朴素的张量表示

对词表大小为 $n$ 的语料，每个词表示为一个长度 $n$ 的 0/1 向量：

$$
\text{onehot}(w_i) = (\underbrace{0,\dots,0}_{i-1},1,0,\dots,0)
$$

| 优点 | 缺点 |
|------|------|
| 简单、易理解、无需训练 | 任意两个词的余弦相似度恒为 0，无法表达语义相近 |
| 无 OOV 之外的参数 | 向量的维度 = 词表大小，大语料下极度稀疏、占内存 |

这两个缺点正是第 04 篇 word2vec 要解决的问题：用低维稠密向量取代高维稀疏向量，并让相似词的向量靠得近。

### 2.5 文本特征处理

**n-gram 特征**：把连续的 n 个相邻 token 组合成一个新特征。

| n | 名称 | 对「我 / 爱 / 」的产出 |
|---|------|---------------------------|
| 1 | unigram | 我、爱、 |
| 2 | bi-gram | 我爱、爱 |
| 3 | tri-gram | 我爱 |

n-gram 的价值：让词袋模型也能部分感知词序，缓解「我爱你」和「你爱我」被当成同一句话的问题。

**文本长度规范**：模型需要固定尺寸输入，因此对短句补齐（padding）、对长句截断（truncating）。两个决策点——补在左边还是右边、截掉头部还是尾部——都会影响效果：

| 策略 | 含义 | 适用 |
|------|------|------|
| `padding="pre"` | 前面补 0 | RNN 类模型（让真实信息紧邻最后一个时间步） |
| `padding="post"` | 后面补 0 | 大多数 Transformer 分类任务 |
| `truncating="pre"` | 截掉前面 | 关键信息常在结尾（如评论结论） |
| `truncating="post"` | 截掉后面 | 关键信息常在开头（如新闻导语） |

### 2.6 数据增强

| 方法 | 做法 | 代价 |
|------|------|------|
| 回译（back translation） | 中文 → 韩文 → 英文 → 中文，得到语义相同、表述不同的新样本 | 需要翻译接口/模型，可能引入语义漂移 |
| 同义词替换 | 用同义词表替换非关键词 | 需要领域词表，可能改变情感极性 |

回译的直觉：中间语言充当一个「语义瓶颈」，强迫模型表达同一含义的不同说法，从而提升泛化。注意回译会改变文本长度，用完还要重新做长度规范。

### 2.7 三种数据分析方法及其结论

| 分析方法 | 看什么 | 得出的决策 |
|----------|--------|------------|
| 标签数量分布 | 各类别样本数是否接近 1:1 | 若严重不均衡 → 数据增强 / 删减 / 换评估指标 |
| 句子长度分布 | 长度的均值、方差与分位数 | 取 `mean + 2*std` 或 95 分位数作为 `max_len` |
| 词频统计与词云 | 高频词里有没有脏数据 | 人工审核清洗，或补充停用词 |

## 3. 可运行示例

### 3.1 jieba 分词、词性标注、自定义词典

```python
# 依赖: pip install jieba
import jieba
import jieba.posseg as pseg

# 造一个自定义词典，格式: 词语 [词频] [词性]
with open("user_dict.txt", "w", encoding="utf-8") as f:
 f.write("教育 100 n\n")
 f.write(" 100 n\n")

jieba.load_userdict("user_dict.txt")

content = "教育是一家上市公司，旗下有品牌。我是在这里学习人工智能"

print("精确模式 :", jieba.lcut(content))
print("全模式 :", jieba.lcut(content, cut_all=True))
print("搜索模式 :", jieba.lcut_for_search(content))

# 词性标注: 每个元素同时带 word 和 flag
print("词性标注 :", [(g.word, g.flag) for g in pseg.lcut(content)])

# 只取形容词（词性 a）——做词云前的常见筛选
only_adj = [g.word for g in pseg.lcut(content) if g.flag == "a"]
print("形容词 :", only_adj)
```

预期输出要点：精确模式会把「教育」「」各切成一个词（自定义词典生效）；全模式额外产出「传」「智」「教育」「上市」「公司」「程序」等冗余结果，标点也会单独成词；搜索模式在精确结果上额外补出「上市」「公司」「程序」「人工」「智能」这类子词。

### 3.2 n-gram 特征与文本长度规范（纯 numpy，无额外依赖）

```python
import numpy as np

def add_n_gram(a: list, n: int = 2) -> set:
 """把列表 a 切成 n-gram 集合，例如 [1,3,2,1,5,3] -> {(1,3),(3,2),...}"""
 return set(zip(*[a[i:] for i in range(n)]))

print(add_n_gram([1, 3, 2, 1, 5, 3], n=2))
# {(1, 3), (3, 2), (2, 1), (1, 5), (5, 3)}

def my_padding(x: list, max_len: int = 5) -> list:
 """先截断再补齐: 取前 max_len 个，不足则尾部补 0"""
 x = x[:max_len]
 x = x + [0] * (max_len - len(x))
 return x

print(my_padding([1, 2, 3, 45, 5, 6, 7, 8], max_len=5)) # [1, 2, 3, 45, 5]
print(my_padding([1, 2], max_len=5)) # [1, 2, 0, 0, 0]
```

如果要按 batch 统一长度，`keras` 的 API 更省事（注意顺序：先截断后补齐）：

```python
# 依赖: pip install tensorflow (或用 numpy 手写上面的 my_padding 代替)
from tensorflow.keras.preprocessing import sequence

x_train = [[1, 23, 5, 32, 55, 63, 2, 21, 78, 32, 23, 1],
[2, 32, 1, 23, 1]]
print(sequence.pad_sequences(x_train, maxlen=10, padding="post", truncating="pre"))
```

### 3.3 完整预处理流水线 + 语料体检

```python
# 依赖: pip install jieba pandas
import re
from collections import Counter
import jieba
import pandas as pd

STOPWORDS = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "都", "也", "很"}

def clean(text: str) -> str:
 """只保留中文，其余替换为空格（注意: 会丢掉 CT、MRI 这类英文缩写）"""
 text = re.sub(r"[^\u4e00-\u9fa5]", "", str(text))
 return re.sub(r"\s+", "", text).strip

def preprocess(text: str, max_len: int = 30) -> str:
 words = [w for w in jieba.lcut(clean(text)) if w.strip and w not in STOPWORDS]
 return "".join(words[:max_len]) # 先按词截断，再交给向量化器

# 用一份内联小样本代替外部数据文件，保证示例自包含
docs = [
 ("这个酒店位置很好，房间干净整洁，服务员态度不错", 1),
 ("早餐不好，服务不到位，房间条件差，隔音非常差", 0),
 ("交通很方便，性价比高，推荐一下", 1),
 ("酒店设备一般，套房里卧室不能上网", 0),
]
df = pd.DataFrame(docs, columns=["sentence", "label"])

# --- 语料体检 1: 标签分布，判断是否需要数据增强 ---
print("标签分布:", Counter(df["label"]))

# --- 语料体检 2: 句子长度分布，据此决定 max_len ---
df["char_len"] = df["sentence"].apply(len)
print("字符长度: mean=%.1f std=%.1f 95分位=%.0f"
 % (df["char_len"].mean, df["char_len"].std, df["char_len"].quantile(0.95)))

# --- 预处理 ---
df["words"] = df["sentence"].apply(preprocess)
print(df[["sentence", "words", "label"]].to_string(index=False))

# --- 语料体检 3: 词频统计，看高频词里有没有脏数据 ---
vocab = set(w for s in df["words"] for w in s.split)
print("词表大小:", len(vocab))
```

### 3.4 词向量层：one-hot 的「可训练」替代品

```python
# 依赖: pip install torch
import torch
import torch.nn as nn

vocab = ["<pad>", "酒店", "位置", "很好", "服务", "差"]
word2id = {w: i for i, w in enumerate(vocab)}

sentence = ["酒店", "位置", "很好"]
ids = torch.tensor([word2id[w] for w in sentence])

# num_embeddings=词表大小, embedding_dim=每个词的向量维度
embedding = nn.Embedding(num_embeddings=len(vocab), embedding_dim=4)
vecs = embedding(ids)
print(vecs.shape) # torch.Size([3, 4]) —— 3 个词，每个 4 维
```

对比一下 one-hot 与 embedding 的参数规模：one-hot 的「参数」是词表大小的稀疏向量，而 embedding 是一个 `词表大小 × 维度` 的可训练矩阵——后者维度可控，且训练后语义相近的词会自动靠近。这正是第 04 篇展开的内容。

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 分词把专有名词切碎（「」→「 / 程序员」） | 未加载领域词典，jieba 默认词典不含该词 | `jieba.load_userdict` 加载自定义词典，格式 `词 词频 词性` |
| 全模式结果里出现空字符串和标点 | 全模式穷举所有成词组合，标点也被切出来 | 全模式只用于召回类场景；常规任务用精确模式，并显式过滤标点 |
| 用 `jieba.lcut` 却发现返回生成器 | `jieba.cut` 返回生成器，`jieba.lcut` 才返回 list | 需要列表就统一用 `lcut`；需要流式处理才用 `cut` |
| 只用 `re.sub(r"[^\u4e00-\u9fa5]", "", text)` 清洗，结果 CT / MRI 全没了 | 正则排除了所有非汉字字符 | 改为保留字母数字：`re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", text)`，或对医学文本单独建缩写白名单 |
| 训练时报「expected sequence of length N」 | 同一个 batch 内样本长度不一致 | 在 Dataset/collate 阶段统一 `max_len`，补齐与截断策略保持一致 |
| 模型对长评论效果差 | `max_len` 定得太小，长句关键信息在截断中丢失 | 先画长度分布，取 `mean + 2*std` 或 95 分位数 |
| 正负样本 9:1，准确率虚高但 F1 很低 | 类别不均衡，模型倾向预测多数类 | 数据增强 / 重采样，或改用 macro-F1、AUC 等指标 |
| 回译后样本长度暴涨或语义漂移 | 中间语言翻译引入了额外修饰 | 回译后重新过滤长度、人工抽检，控制增强比例（一般不超过原数据 20%） |
| 词云中文显示成方框 | matplotlib 默认字体不含中文 | 指定中文字体路径：`WordCloud(font_path="SimHei.ttf")`，并设置 `plt.rcParams["font.sans-serif"]` |
| 随机种子不固定，两次实验指标对不上 | 数据划分、初始化、shuffle 都有随机性 | 固定 `random_state` / `torch.manual_seed` / `np.random.seed` |

## 5. 面试问答

**Q1. 中文分词为什么比英文分词难？jieba 的三种模式应该怎么选？**

<details><summary>参考答案</summary>

英文有天然空格作为词边界，中文是连续的字序列，词的边界本身没有显式标记，因此分词本质是一个**歧义消解 + 未登录词识别**的问题。主要难点有三类：

1. **切分歧义**：「乒乓球拍卖完了」可以切成「乒乓球 / 拍卖 / 完 / 了」或「乒乓球拍 / 卖 / 完 / 了」，需要靠上下文概率决定。
2. **未登录词（OOV）**：新词、人名、品牌名、领域术语不在词典里，只能靠统计模型或子词方法兜底。
3. **规范不统一**：「自然语言处理」算一个词还是三个词，取决于任务定义。

jieba 三种模式的选择：

- **精确模式**（默认）适合绝大多数任务，尤其是分类、向量化，因为它没有冗余、歧义最少。
- **全模式**把成词可能全部扫出来，速度快但不能消歧，只适合「宁可多召回、后面再用规则筛」的场景。
- **搜索引擎模式**在精确模式基础上对长词再切出子词（如「人工智能」→「人工 / 智能 / 人工智能」），专门为搜索索引设计，能提高长词的部分匹配召回。

实际工程中还有一步不能省：**加载自定义词典**。领域专名不处理，后面的 TF-IDF 和词向量都会在错误的粒度上学习。

</details>

**Q2. 为什么预处理阶段一定要先做文本数据分析？不做会怎样？**

<details><summary>参考答案</summary>

文本数据分析的作用是「理解语料 + 发现问题 + 指导超参数」，对应三张图三个决策：

| 分析 | 发现的问题 | 对应决策 |
|------|-----------|----------|
| 标签数量分布 | 正负样本不均衡（例如 9:1） | 做数据增强 / 重采样；评估指标从 accuracy 换成 macro-F1 或 AUC |
| 句子长度分布 | 长度长尾严重，mean 和 95 分位差很远 | `max_len` 取 `mean + 2*std` 或 95 分位；过长文本改用分块或 head+tail 截断 |
| 词频统计与词云 | 高频词里混入了 HTML 标签、乱码、广告 | 定位并清洗脏数据，补充停用词表 |

不做分析的典型后果：`max_len` 拍脑袋定成 128，而语料 95 分位是 40——大量位置是 padding，注意力被无效位置稀释，训练变慢且效果下降；或者正负样本严重不均衡却只看 accuracy，得到一个「全预测多数类」也有 90% 准确率的假象模型。

</details>

**Q3. one-hot 的两个致命缺点是什么？它们分别被什么方法解决？**

<details><summary>参考答案</summary>

one-hot 的两个缺点是：

1. **语义鸿沟**：任意两个不同词的向量正交，余弦相似度恒为 0，所以「酒店」和「宾馆」在模型眼里毫无关系。这直接导致模型无法泛化到同义表达。
2. **维度灾难 + 稀疏**：向量长度等于词表大小（中文动辄几万到几十万），且每个向量只有一个 1，存储和计算都极其浪费；词表每增大一次，所有向量都要变长。

解决路径是**分布式表示（distributed representation）**：

- **word2vec / GloVe**：用低维（通常 100–300 维）稠密向量表示词，通过「上下文相似的词向量也应相似」这一假设训练，使相似词在向量空间中靠近。这一步同时解决了两个缺点。
- **word embedding（`nn.Embedding`）**：把词向量矩阵作为模型的一层参数，随任务一起端到端训练。相比用预训练静态词向量，它能让「酒店」在这个具体任务里的向量更贴合任务分布。
- 再往后，**ELMo / BERT** 进一步解决「同一个词在不同上下文里应该有不同的向量」的问题（一词多义），这是静态词向量无法处理的。

</details>

## 6. 自测题

**1. 判断并说明原因：中文分词属于「token 级分类任务」，命名实体识别属于「句子级分类任务」。**

<details><summary>参考答案</summary>

前半句对，后半句不完整。

- 中文分词：需要给字序列中的每个位置判断「是否是一个词的边界」，输出与输入等长，属于典型的**序列标注 / token 级分类**（常用 B/M/E/S 标签体系）。
- 命名实体识别：标准做法拆成**两阶段**——第一阶段边界识别，对每个 token 打标签（如 B-PER、I-PER、O），这一段同样是 **token 级分类**；第二阶段 span 分类，把识别出的实体片段整体归到具体类型，这一段可以看作**句子级（片段级）分类**。

所以更准确的说法是：NER = token 级边界识别 + 片段级类型分类。

</details>

**2. 语料共 10000 条，句长 mean = 25、std = 10。请给出一个合理的 `max_len`，并说明理由。**

<details><summary>参考答案</summary>

取 `max_len = mean + 2*std = 45`（工程上常直接取 48 或 50 的对齐值），或直接看 95 分位数。

理由：正态分布下 `mean ± 2*std` 覆盖约 95% 的样本，意味着只有约 5% 的长句会被截断，而 `max_len` 又没有按最大值设定（最大值可能是 200+，会造成大量 padding 浪费）。这是一个「信息损失」与「计算开销」之间的平衡点。

如果业务上不能接受任何截断（例如法律文书、医疗记录里末尾常有关键结论），则应改用分块（chunking）或 head+tail 截断，而不是单纯增大 `max_len`。

</details>

**3. 「我 / 爱 / 」在 bi-gram 下会新增哪些特征？为什么词袋模型加了 n-gram 就变强了？**

<details><summary>参考答案</summary>

新增 bi-gram 特征：「我爱」「爱」。tri-gram 下还会新增「我爱」。

词袋模型（Bag-of-Words）把文本看成无序的词集合，因此「我爱你」和「你爱我」的词袋表示完全相同，丢失了词序。加入 n-gram 后，相邻词的组合被当成独立特征，等于**局部地把词序编码进了特征**，因此能区分语序不同的句子。

代价是特征维度会快速膨胀（词表为 $V$ 时 bi-gram 理论上界是 $V^2$），实际必须配合 `min_count` 阈值剪掉低频 n-gram，否则稀疏度和内存都会失控。

</details>

**4. 回译数据增强为什么能提升模型效果？使用时要注意什么？**

<details><summary>参考答案</summary>

原理：让文本经过「中文 → 韩文 → 英文 → 中文」的往返翻译，中间语言的表达能力构成了一个「语义瓶颈」。原始表述中的具体措辞被剥掉，只有核心语义能穿过这个瓶颈，翻译回来就得到了**语义相同、表述不同**的新样本。这相当于给模型注入了「同义表达多样性」，缓解过拟合，提升泛化。

注意事项：

1. **语义漂移**：多跳翻译可能改变原意，尤其在专业领域（医疗、法律）术语容易被译错，必须人工抽检。
2. **情感极性翻转**：情感分析任务里，回译偶尔会把否定词丢掉导致极性反转，建议同时保留原样本。
3. **长度变化**：增强后文本长度分布会改变，需要重新做长度规范统计。
4. **增强比例**：一般控制在新样本不超过原数据的 20% 左右，过多会引入噪声主导训练。
5. **标签继承**：回译不保证标签一定正确，对高价值标签建议用模型复核。

</details>

**5. 为什么 `padding="pre"` 和 `padding="post"` 会对 RNN 的效果造成不同影响？**

<details><summary>参考答案</summary>

因为 RNN 是**按时间步顺序递归**的，最后一个时间步的隐状态通常被当作整句表示送往分类层。

- `padding="post"`（尾部补 0）：真实 token 在前，padding 在后。若模型直接把最后一个时间步的 hidden state 当句子表示，读到的是 padding 对应的隐状态，信息被稀释；必须配合 `pack_padded_sequence` 或取最后一个**有效**时间步才能正确工作。
- `padding="pre"`（头部补 0）：padding 在前，真实 token 在后，最后一个时间步恰好落在真实内容上，因此不打包序列也能拿到较合理的表示。但代价是前面几个时间步都在处理无意义的 0，仍会污染早期隐状态。

对 Transformer 类模型来说这个问题不存在——因为 `attention_mask` 会显式屏蔽 padding 位置，注意力和 LayerNorm 都不会被无效位置干扰。所以在大模型时代，padding 方向的重要性已经大幅下降，反而是「mask 有没有正确传进去」更关键。

</details>

## 7. 延伸阅读

- jieba 官方仓库（分词模式、自定义词典、词性标注全部 API）：https://github.com/fxsjy/jieba
- jieba 词性标注对照表（`n` / `v` / `a` / `nr` / `ns` 等全量说明）：https://github.com/fxsjy/jieba/blob/master/jieba/posseg/char_state_tab.py
- 《Speech and Language Processing》(Jurafsky & Martin) 第 2 章 Regular Expressions, Text Normalization, Edit Distance：https://web.stanford.edu/~jurafsky/slp3/
- Hugging Face NLP Course 第 2 章「Using 🤗 Transformers」中的 tokenization 与 padding/truncation：https://huggingface.co/learn/nlp-course/chapter2/4
- PyTorch `nn.Embedding` 官方文档：https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html
- 中文酒店评论情感语料 ChnSentiCorp（本第 4 节数据分析使用的语料来源）：https://github.com/chatopera/ChnSentiCorp

---

[⬅️ 返回 NLP 目录](README.md)
