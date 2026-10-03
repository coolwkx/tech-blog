# 11 NLP 项目实战：情感分析

> **一句话总结**：情感分析是二分类问题的典型代表，它的难点不在模型选型，而在「否定与转折的语义、类别不均衡、以及把分类流水线做成一件事可复现的工程」。
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。

> 1. 完整走通中文情感分析项目：数据体检 → 预处理 → 三档模型对比 → 评估 → 错误分析 → 上线封装。
> 2. 针对「否定词、程度副词、转折句」设计专项特征或数据增强，并用量化实验验证收益。
> 3. 说清情感分析特有的坑（极性翻转、标注主观性、领域迁移）并给出处理方案。

> **说明**：**没有专门的情感分析项目**，只有一份与之高度等价的中文二分类语料——中文酒店评论语料（`train.tsv` / `dev.tsv`，`sentence \t label`，0 消极 / 1 积极），用于第 01 篇的文本数据分析教学（标签分布、句子长度分布、形容词词云）。本文把它按「情感分析项目」的主线重组，并补充了否定/转折处理、三档模型对比、上线封装等本主题覆盖的工程内容。

## 1. 核心概念

### 1.1 情感分析的任务变体

「情感分析」是一个任务族，先明确边界：

| 变体 | 输出 | 例子 |
|------|------|------|
| 文档级情感分类 | 整段文本一个极性 | 这条酒店评论是正面还是负面 |
| 句子级情感分类 | 每句一个极性 | 评论中哪句是吐槽 |
| 方面级（ABSA） | （方面, 极性）对 | 「房间干净，但服务差」→ 房间+、服务− |
| 情感强度回归 | 1–5 星 | 打几分 |
| 情绪分类 | 多类情绪 | 喜 / 怒 / 哀 / 惧 |

语料对应的场景是**文档级二分类**（0 消极 / 1 积极），等价于「二分类情感极性判定」。这是最常见的入门形态，也是后面医疗多分类（第 12 篇）的直接前身。

### 1.2 中文酒店评论语料

使用的中文酒店评论语料属于**二分类中文情感分析语料**，`train.tsv` 是训练集、`dev.tsv` 是验证集，两者格式相同：

| 列 | 含义 |
|----|------|
| `sentence` | 具有感情色彩的评论文本 |
| `label` | 0 = 消极，1 = 积极 |

真实样本（来自，注意转折、否定与多话题混写的情况）：

| sentence | label |
|----------|-------|
| 早餐不好,服务不到位,晚餐无西餐,早餐晚餐相同,房间条件不好,餐厅不分吸烟区.房间不分有无烟房. | 0 |
| 去的时候 ,酒店大厅和餐厅在装修,感觉大厅有点挤.由于餐厅装修本来该享受的早饭,也没有享受(他们是8点开始每个房间送,但是我时间来不及了)不过前台服务员态度好! | 1 |
| 有很长时间没有在西藏大厦住了，以前去北京在这里住的较多。这次住进来发现换了液晶电视，但网络不是很好，他们自己说是收费的原因造成的。其它还好。 | 1 |
| 非常好的地理位置，住的是豪华海景房，打开窗户就可以看见栈桥和海景。记得很早以前也住过，现在重新装修了。总的来说比较满意，以后还会住 | 1 |
| 交通很方便，房间小了一点，但是干净整洁，很有香港的特色，性价比较高，推荐一下哦 | 1 |
| 酒店的装修比较陈旧，房间的隔音，主要是卫生间的隔音非常差，只能算是一般的 | 0 |
| 酒店有点旧，房间比较小，但酒店的位子不错，就在海边，可以直接去游泳。8楼的海景打开窗户就是海。如果想住在热闹的地带，这里不是一个很好的选择，不过威海城市真的比较小，打车还是相当便宜的。晚上酒店门口出租车比较少。 | 1 |
| 位置很好，走路到文庙、清凉寺5分钟都用不了，周边公交车很多很方便，就是出租车不太爱去（老城区路窄爱堵车），因为是老宾馆所以设施要陈旧些， | 1 |
| 酒店设备一般，套房里卧室的不能上网，要到客厅去。 | 0 |

这九条样本身就揭示了情感分析的核心难点：

1. **转折决定极性**。"装修陈旧、隔音差」整体却是 label=1（因为「位子不错」「海景」）；「房间小了一点，但是干净整洁」也是 1。**最后一个分句、或句子整体正负面的净和**往往决定标签，而不是「是否出现了负面词」。
2. **多话题混写**。一条评论同时评价位置、房间、服务、早餐，需要模型学会「按整体印象」而非「按最强烈的单个词」判断。
3. **否定与程度**。"不是很好」「不太爱去」「比较陈旧」都含否定或弱化修饰，纯词袋几乎无法处理。
4. **标注主观性**。第 3、7、8 条的正面性其实偏弱（都是「有缺点但总体还行」），不同标注者可能给出不同标签——这是情感分析指标天花板受标注质量限制的根本原因。

### 1.3 标签分布的判断准则

给出的准则非常实用：

> 在深度学习模型评估中，一般使用 **ACC** 作为评估指标。若想把 ACC 的基线定义在 **50% 左右**，则正负样本比例需要维持在 **1:1** 左右，否则就要做必要的数据增强或数据删减。

酒店评论语料的训练集与验证集正负样本**都稍有不均衡**，的建议是「可以进行一些数据增强」。工程上的完整判断链条是：

| 观察 | 结论 |
|------|------|
| 正负比在 1:1 ± 10% 内 | 直接用 ACC 与 F1，无需处理 |
| 偏离到 6:4 左右 | 加 `class_weight='balanced'`，同时报告 macro-F1 |
| 偏离到 8:2 以上 | 必须处理：增强少数类 / 重采样 / 换指标（macro-F1、AUC、PR-AUC） |
| 少数类样本 < 500 条 | 优先考虑「换更小的模型 + 强正则」或「用大模型做零样本/少样本」，而不是硬训 |

### 1.4 三档模型在情感分析上的对比

| 档位 | 方法 | 优势 | 局限（情感分析场景） |
|------|------|------|---------------------|
| 1 | TF-IDF + 线性/树模型 | 秒级训练、可解释（能看哪些词推高正面分） | 完全无法处理否定与转折；「不推荐」与「推荐」词袋几乎同形 |
| 2 | 词向量 + FastText / TextCNN | 快、能捕捉局部 n-gram（部分处理否定） | 上下文有限；长距离转折（「…但…」）建模弱 |
| 3 | BERT 微调 | 上下文相关表示，能正确区分「服务好」与「服务不好」 | 需要 GPU、推理慢、模型大 |

对情感分析这类**主观性强、语义细粒度**的任务，第 1 档与第 3 档的差距通常比主题分类更大——因为主题分类靠关键词就能做，而情感极性常常由语气词、否定、转折决定。这也是情感分析特别值得上预训练模型的原因。

## 2. 方法细节

### 2.1 完整项目流水线

```
① 数据体检 ──► ② 预处理 ──► ③ 基线模型 ──► ④ 指标与错误分析 ──► ⑤ 增强/换模型 ──► ⑥ 封装上线
 │ │ │ │ │ │
 标签分布 清洗/分词 TF-IDF+LR macro-F1 否定/转折专项 Flask API
 长度分布 去停用词 FastText 混淆矩阵 数据增强 阈值与置信度
 形容词词云 长度规范 BERT 微调 错例人工归纳 换领域模型 监控与重训
```

### 2.2 数据体检：三个必看的图（对应第 4 节）

| 图 | 代码要点 | 看什么结论 |
|----|----------|-----------|
| 标签数量分布 | `sns.countplot(x="label", data=train_data, hue="label")` | 正负比例，决定是否需要增强 |
| 句子长度分布 | 新增 `sentence_length` 列；`sns.countplot` 柱状图 + `sns.displot(kde=True)` 密度曲线 | 定 `max_len`；长尾明显则考虑分块 |
| 正负样本长度散点 | `sns.stripplot(y="sentence_length", x="label", data=train_data, hue="label")` | **是否存在长度偏差**：如果正面评论系统性更长，模型可能学到「长=正面」的伪特征 |

第三张图是情感分析特有的检查项。很多真实数据集里，负面评论因为要列举问题而更长，或正面评论因为要夸而更长；一旦存在这种相关性，模型会走捷径，换到新数据上就崩。发现后应做长度分桶评估（把样本按长度分段分别算准确率），确认模型不是靠长度。

**词频与高频词云**（原样做法）：

```python
# 统计词表规模
train_vocab = set(chain(*map(lambda x: jieba.lcut(x), train_data["sentence"])))

# 只取形容词（词性 a）按类别画词云，能直接看出极性用词差异
def get_a_list(text):
 return [g.word for g in pseg.lcut(text) if g.flag == "a"]

p_a_words = list(chain(*map(get_a_list, train_data[train_data["label"] == 1]["sentence"])))
# WordCloud(font_path='SimHei.ttf', max_words=100, background_color="white").generate("".join(p_a_words))
```

词云的真正用途不是「好看」，而是**发现脏数据**：如果正面词云里出现「差 / 烂 / 垃圾」，要么是标注错误，要么是停用词/分词有问题，需要人工审核清洗。

### 2.3 情感分析特有的三个语义难点与处理

**（1）否定与双重否定**

「服务好」与「服务不好」在词袋里都包含「服务」和「好」，几乎同形。三种处理方式：

| 方式 | 做法 | 效果 | 代价 |
|------|------|------|------|
| 否定词直接拼接 | 把「不」「没」「无」与后一个词拼成新 token：`不好` → `不_好` | 简单，词袋也能用 | 依赖分词质量；连续否定处理不了 |
| 加否定窗口特征 | 检测否定词后 N 个词（如 3 词内）的极性取反 | 可解释 | 需要规则维护 |
| 交给上下文模型 | BERT/attention 天然建模「不」与「好」的依赖 | 效果最好 | 需要 GPU |

**（2）程度副词**

「很好 / 好 / 一般 / 差」是强度谱。TF-IDF 只关心词形，不加权强度。可以引入情感词典对程度副词打分（如「非常 ×1.5、稍微 ×0.5」），或让模型从数据里学（BERT 能做到）。

**（3）转折结构**

「A 但 B」的极性主要由 B 决定，但词袋会把 A 的权重也算进去。可用 n-gram（`ngram_range=(1,3)`）让「但」与后文形成特征组合，或直接用注意力模型。在词汇层面，可维护一个转折词表（但、但是、不过、然而、可惜、只是），把它们作为**特征**而非停用词——很多新手会把这类词当停用词删掉，反而丢掉关键信息。

### 2.4 数据增强：优先做「极性安全」的增强

情感分析的增强有一个特殊约束：**不能翻转极性**。第 01 篇讲过的两类增强要区别对待：

| 方法 | 对情感分析的安全性 | 说明 |
|------|-------------------|------|
| 回译（中→韩→英→中） | 有风险 | 多跳翻译可能丢掉否定词，把「不好」译成「good」；必须人工抽检 |
| 同义词替换 | 有风险 | 「好」→「差」如果被词典当成同义就灾难性；只替换中性词 |
| 标点/语气词扰动 | 安全 | 加入「！」「…」，或补充「啊/呢/吧」等语气词 |
| 随机删除非关键词 | 较安全 | 删除中性词（「这个」「那个」），不删情感词与否定词 |
| 否定式构造 | 安全且高价值 | 主动构造「不 + 正面词」作为负样本，专门补否定能力 |
| 类别重采样 | 安全 | 直接对少数类过采样 |

**回译必须抽检**，这是实践中的硬教训：情感分析里最容易翻车的就是回译把否定丢掉。

### 2.5 评估与阈值

情感分析常需要输出**概率**而不是硬标签（用于分流、排序、置信度过滤）。这时：

1. 训练照常用 `CrossEntropyLoss` 得到 logits。
2. 推理时用 `softmax(logits)` 得到概率。
3. **不要固定用 0.5 作为阈值**。用验证集画 **PR 曲线**，按业务目标选阈值：
 - 若「漏判负面」（FN）代价高（如舆情预警）→ 降低正面阈值，提高负面召回。
 - 若「误判负面」（FP）代价高（如自动回复）→ 提高负面阈值，保证精确率。
4. 报告指标时同时给出 accuracy、macro-F1、AUC、PR-AUC，以及**在选定阈值下**的 P/R/F1。

### 2.6 领域迁移与标注一致性

情感分析模型在跨领域时掉点非常普遍（酒店评论训练的模型直接用在手机评论上，可能掉 10+ 个点）。原因：

- **领域词极性不同**：「屏幕大」在手机评论里是优点，在手表评论里可能是缺点。
- **表达风格不同**：数码产品的评价更专业、更简短；酒店评论更生活化、更长。

应对手段按成本排序：

| 手段 | 成本 | 效果 |
|------|------|------|
| 在目标领域标注 500–2000 条做微调 | 中 | 通常最有效 |
| 用目标领域语料做继续预训练（continue pretraining）| 高 | 领域差异极大时值得 |
| 用大模型做零样本/少样本标注，再人工审核 | 中低 | 快速冷启动 |
| 直接跨领域使用 | 低 | 只在领域相近时可用，必须做小样本评测确认 |

**标注一致性**是另一个天花板。同一句话不同标注者可能给不同标签。工程上应做：多人交叉标注一小部分（如 5%）、计算 Cohen's Kappa 或 Krippendorff's Alpha；一致性低于 0.7 说明任务定义本身模糊，应先修改标注规范，而不是继续调模型。

## 3. 可运行示例

### 3.1 端到端流水线（自包含，内联样本）

```python
# 依赖: pip install scikit-learn jieba numpy
import jieba
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
confusion_matrix, roc_auc_score)
from sklearn.model_selection import train_test_split

# ---------- ① 内联构造语料（实际项目从 train.tsv/dev.tsv 读取 sentence\tlabel） ----------
raw = [
("非常好的地理位置，打开窗户就可以看见海景，比较满意", 1),
("交通很方便，房间小了一点，但是干净整洁，性价比高", 1),
("前台服务员态度好，早餐也不错，以后还会住", 1),
("位置很好，走路到景点五分钟，周边公交很多很方便", 1),
("房间干净，床很舒服，值得推荐", 1),
("早餐不好，服务不到位，房间条件不好，隔音差", 0),
("酒店装修比较陈旧，卫生间隔音非常差，只能算一般", 0),
("设备一般，房间里不能上网，必须到客厅去", 0),
("服务态度差，房间有异味，绝对不推荐", 0),
("空调坏了没人修，前台还很不耐烦", 0),
] * 6 # 重复以形成 60 条样本

df = pd.DataFrame(raw, columns=["sentence", "label"])

# ---------- ② 数据体检 ----------
print("== 标签分布 ==")
print(df["label"].value_counts.to_dict)
ratio = df["label"].mean
print(f"正面比例: {ratio:.3f} （接近 0.5 说明均衡）")

df["char_len"] = df["sentence"].apply(len)
print("\n== 句子长度分布 ==")
print(df["char_len"].describe[["mean", "std", "50%", "max"]].round(2))
suggests_max_len = int(df["char_len"].mean + 2 * df["char_len"].std)
print(f"建议 max_len = mean + 2*std = {suggests_max_len}")

print("\n== 长度偏差检查（正负样本长度是否系统性不同） ==")
print(df.groupby("label")["char_len"].mean.round(2).to_dict)

# ---------- ③ 预处理 ----------
STOPWORDS = {"的", "了", "在", "是", "我", "有", "和", "就", "都", "也", "很", "只", "要"}
# 注意：转折词与否定词必须保留！它们决定极性
KEEP_WORDS = {"不", "没", "无", "但", "但是", "不过", "然而", "差", "好"}

def preprocess(text: str) -> str:
    words = [w for w in jieba.lcut(text)
    if w.strip() and (w in KEEP_WORDS or w not in STOPWORDS)]
    return "".join(words)

df["words"] = df["sentence"].apply(preprocess)
print("\n== 预处理示例 ==")
print(df[["sentence", "words"]].head(3).to_string(index=False))

# ---------- ④ 划分 + 特征 + 模型 ----------
X_train, X_test, y_train, y_test = train_test_split(
df["words"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
)

vec = TfidfVectorizer(
token_pattern=r"(?u)\b\w+\b",
ngram_range=(1, 2), # 让「不 好」这类组合成为特征
min_df=1,
sublinear_tf=True,
use_idf=True,
norm="l2",
)
Xtr = vec.fit_transform(X_train)
Xte = vec.transform(X_test) # 只用 transform！

clf = LogisticRegression(max_iter=1000, C=4.0, class_weight="balanced")
clf.fit(Xtr, y_train)

# ---------- ⑤ 评估（含概率与阈值分析） ----------
proba = clf.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)

print("\n== 指标 ==")
print("accuracy : %.4f" % accuracy_score(y_test, pred))
print("AUC : %.4f" % roc_auc_score(y_test, proba))
print(classification_report(y_test, pred, target_names=["消极", "正面"], digits=4))

print("== 混淆矩阵（行=真实 0/1，列=预测 0/1） ==")
print(confusion_matrix(y_test, pred))

# 阈值敏感性：不同阈值下的表现
print("\n== 阈值敏感性 ==")
for thr in [0.3, 0.4, 0.5, 0.6, 0.7]:
    p = (proba >= thr).astype(int)
    tp = int(((p == 1) & (y_test == 1)).sum)
    fp = int(((p == 1) & (y_test == 0)).sum)
    fn = int(((p == 0) & (y_test == 1)).sum)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(f"thr={thr:.1f} P={precision:.3f} R={recall:.3f} acc={accuracy_score(y_test, p):.3f}")

    # ---------- ⑥ 错误分析与特征重要性 ----------
    print("\n== 错例（含概率，便于判断是标注问题还是模型问题） ==")
    for text, true, p, pr in zip(X_test, y_test, pred, proba):
        if true != p:
            print(f" 真实={true} 预测={p} P(正面)={pr:.3f} 文本={text}")

            names = np.array(vec.get_feature_names_out)
            coef = clf.coef_[0]
            print("\n推动【正面】的关键词:", list(names[np.argsort(coef)[-8:]][::-1]))
            print("推动【消极】的关键词:", list(names[np.argsort(coef)[:8]]))
```

对照真实项目：把 `raw` 换成 `pd.read_csv("train.tsv", sep="\t")`、把 `df.columns` 对齐为 `sentence/label` 即可，其余逻辑完全一致（注意真实数据的 `train.tsv` 是 `sentence \t label` 两列）。

### 3.2 否定感知的预处理与专项特征

```python
import jieba
import re

NEGATIONS = {"不", "没", "没有", "无", "非", "别", "莫", "未", "不要", "不能"}
DEGREE = {"非常": 1.5, "特别": 1.5, "很": 1.3, "太": 1.3,
"比较": 0.8, "有点": 0.6, "稍微": 0.5, "略": 0.5}
CONTRAST = {"但", "但是", "不过", "然而", "可是", "只是", "可惜"}

def negate_join(text: str, window: int = 2) -> str:
    """把否定词与后 window 个词拼接成新 token，让词袋也能感知否定。
    例: '服务 不 好' -> '服务 不_好'
    """
    words = list(jieba.lcut(text))
    out, i = [], 0
    while i < len(words):
        if words[i] in NEGATIONS:
            j = min(i + window, len(words))
            merged = "_".join(words[i:j])
            out.append(merged)
            i = j
        else:
            out.append(words[i])
            i += 1
            return "".join(out)

        def polarity_features(text: str) -> dict:
            """抽出可用于树模型/线性模型的显式情感特征（规则词典原型）"""
            words = list(jieba.lcut(text))
            POS = {"好", "满意", "推荐", "干净", "方便", "舒服", "不错", "热情"}
            NEG = {"差", "脏", "冷漠", "陈旧", "吵", "异味", "不耐烦"}

            score = 0.0
            for k, w in enumerate(words):
                if w in POS:
                    polarity = 1.0
                    # 若前 2 个词内出现否定词，极性翻转
                    if any(p in NEGATIONS for p in words[max(0, k - 2):k]):
                        polarity = -1.0
                        # 若前一个词是程度副词，按权重缩放
                        degree = DEGREE.get(words[k - 1], 1.0) if k > 0 else 1.0
                        score += polarity * degree
                    elif w in NEG:
                        score -= 1.0

                        return {
                    "n_negation": sum(w in NEGATIONS for w in words),
                    "n_contrast": sum(w in CONTRAST for w in words),
                    "degree_sum": sum(DEGREE.get(w, 0.0) for w in words),
                    "rule_score": round(score, 2),
                    "has_contrast": int(any(w in CONTRAST for w in words)),
                    }

                    samples = ["服务 不 好", "房间 非常 干净 ， 但 服务 太 差", "不 推荐 这家 酒店"]
                    for s in samples:
                        print(f"{s!r}\n 否定拼接 -> {negate_join(s)}\n 特征 -> {polarity_features(s)}\n")
```

`negate_join` 的效果可以用对照实验量化：分别用「原始分词」与「否定拼接后」训练同一个模型，比较验证集 macro-F1，就能确定这个改动是否值得保留——**不要凭感觉加特征**。

### 3.3 BERT 微调（第 3 档，替代方案）

```python
# 依赖: pip install transformers torch datasets
import numpy as np
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
 Trainer, TrainingArguments)

MODEL = "bert-base-chinese"
tokenizer = AutoTokenizer.from_pretrained(MODEL)

raw = [
 ("非常好的地理位置，打开窗户就可以看见海景", 1),
 ("交通方便，房间干净整洁，性价比高", 1),
 ("早餐不好，服务不到位，隔音差", 0),
 ("酒店装修陈旧，卫生间隔音非常差", 0),
] * 8
texts = [t for t, _ in raw]
labels = [y for _, y in raw]

ds = Dataset.from_dict({"text": texts, "label": labels})
ds = ds.map(lambda batch: tokenizer(batch["text"], truncation=True, max_length=64), batched=True)
ds = ds.train_test_split(test_size=0.25, seed=42) # 注意：先划分再看，避免在上面 split 后 map 造成泄漏

model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2)

def compute_metrics(eval_pred):
 logits, y_true = eval_pred
 pred = np.argmax(logits, axis=-1)
 return {"accuracy": accuracy_score(y_true, pred),
 "macro_f1": f1_score(y_true, pred, average="macro")}

args = TrainingArguments(
 output_dir="./sentiment_bert",
 num_train_epochs=3, # BERT 收敛慢，至少 3 轮
 per_device_train_batch_size=8,
 per_device_eval_batch_size=8,
 learning_rate=2e-5, # 必须很小，避免破坏预训练知识
 weight_decay=0.01,
 warmup_ratio=0.1,
 max_grad_norm=1.0,
 evaluation_strategy="epoch",
 save_strategy="epoch",
 load_best_model_at_end=True,
 metric_for_best_model="macro_f1",
 logging_steps=5,
 seed=42,
)

trainer = Trainer(
 model=model, args=args,
 train_dataset=ds["train"], eval_dataset=ds["test"],
 compute_metrics=compute_metrics,
)
# trainer.train # 取消注释即可训练
print("配置就绪。注意：小数据上 BERT 极易过拟合，务必用 eval 曲线早停。")
```

### 3.4 情感分类服务封装（Flask，含阈值与置信度）

```text
# 依赖: pip install flask scikit-learn jieba
# 说明：这是「离线训练 + 在线推理」的标准形态；训练产物与预处理物料必须一起加载
import json
import time

import jieba
import joblib
from flask import Flask, Response, request

# 训练阶段保存（在同一份代码里）：
# joblib.dump({"vec": vec, "clf": clf, "stopwords": STOPWORDS}, "sentiment.pkl")
ARTIFACT = joblib.load("sentiment.pkl") # 包含 vec / clf / stopwords
STOPWORDS = set(ARTIFACT["stopwords"])
KEEP_WORDS = {"不", "没", "无", "但", "但是", "不过", "然而"}

app = Flask(__name__)

def preprocess(text: str) -> str:
 """必须与训练时完全一致：同一个分词器、同一份停用词表"""
 return "".join(w for w in jieba.lcut(text)
 if w.strip() and (w in KEEP_WORDS or w not in STOPWORDS))

@app.route("/v1/sentiment/", methods=["POST"])
def sentiment:
 t1 = time.time
 text = request.form["text"]
 vec, clf = ARTIFACT["vec"], ARTIFACT["clf"]

 proba_pos = float(clf.predict_proba(vec.transform([preprocess(text)]))[0, 1])
 # 阈值可配置：舆情预警场景应调低正面阈值以提高负面召回
 threshold = float(request.form.get("threshold", 0.5))
 label = "positive" if proba_pos >= threshold else "negative"

 return Response(
 status=200,
 response=json.dumps({
 "Status": "success",
 "Text": text,
 "Result": label,
 "ProbPositive": round(proba_pos, 4),
 "Confidence": round(max(proba_pos, 1 - proba_pos), 4),
 "Time": "{:.4f}s".format(time.time - t1),
 }, ensure_ascii=False),
 mimetype="application/json",
 )

if __name__ == "__main__":
 app.run(host="127.0.0.1", port=5000)
```

三个工程要点：① **输出概率而不只是标签**，便于下游按业务阈值分流；② **置信度低的样本应转人工**（例如 `Confidence < 0.6`），而不是硬给一个标签；③ **预处理物料必须与模型一起持久化**，否则会出现「离线好、线上差」的静默错误（见第 03 篇的 `fit_transform` 坑）。

## 4. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| 「服务不好」被判为正面 | 词袋无法建模否定，`服务`+`好` 与 `服务`+`不好` 同形 | 否定词拼接、加 n-gram，或直接用 BERT |
| 「装修陈旧但海景好」被判为负面 | 转折结构未被建模，负面词权重压过正面 | 保留转折词作为特征；加 `ngram_range=(1,3)`；换注意力模型 |
| 把「但 / 不过」当停用词删掉后效果下降 | 转折词是极强的情感信号，不是噪声 | 从停用词表中移出转折词与否定词，加入 `KEEP_WORDS` 白名单 |
| 验证集准确率 0.9，线上 0.6 | 领域迁移；或预处理物料与训练时不一致 | 在目标领域标注少量数据微调；把 vectorizer/停用词与模型一起持久化 |
| 模型学到「长评论=正面」 | 正负样本长度系统性不同，特征泄漏 | 画长度散点图检查；做长度分桶评估；必要时做长度均衡采样 |
| 回译增强后准确率反而下降 | 回译丢掉否定词，极性被翻转 | 抽检增强样本；对否定句禁用回译；控制增强比例 ≤ 20% |
| 各类指标都不错，但业务说不好用 | 只看了 accuracy，没看具体场景的 P/R | 按业务定阈值，报告选定阈值下的 P/R/F1；低置信度转人工 |
| 换个随机种子指标波动 3 个点 | 数据量小 + 未固定种子 | 固定所有种子；跑 3–5 次取均值±标准差；做交叉验证 |
| BERT 微调第 1 轮验证集最高，后面越来越差 | 小数据上过拟合 | 减少 epoch；加权重衰减与 dropout；早停；冻结底层 |
| 训练集样本重复出现在验证集 | 划分前未去重（评论语料常有近似重复） | 划分前按文本去重；或用分组划分避免同一来源泄漏 |
| 形容词词云显示方框 | matplotlib 默认字体不含中文 | `WordCloud(font_path="SimHei.ttf")` 并设置 `plt.rcParams["font.sans-serif"]` |
| 标注者之间分歧大，指标上不去 | 情感标注主观性；任务定义模糊 | 先算 Kappa 一致性；统一标注规范（明确「总体印象」还是「是否含负面点」） |

## 5. 面试问答

**Q1. 情感分析和文本分类是什么关系？为什么情感分析更难？**

<details><summary>参考答案</summary>

**关系**：情感分析是文本分类的一个子类——把「情感极性」当作标签空间。文档级情感分析在建模上就是二分类（或几分类），可以直接复用第 05 篇的全部流水线（预处理 → 特征 → 模型 → 评估）。这也是为什么它可以作为「分类项目」的标准练习：任务简单，但对预处理和评估的要求完整。

**更难的原因**（都是文本分类里被放大的问题）：

1. **极性由细粒度语义决定，而非关键词**。主题分类里「湖人」「美联储」直接指示类别；而情感极性依赖否定（「不是很好」）、程度（「还行」vs「非常好」）、转折（「A 但 B」）。纯词袋模型在这方面几乎无能为力，因此第 1 档与第 3 档的性能差距在情感分析上比主题分类更大。
2. **标注主观性强**。主题是客观的（一篇新闻是不是体育新闻，争议很小），而情感强度是主观的。"房间小但干净」到底正面还是负面，不同标注者可能不一致，导致指标天花板受限。必须先做标注一致性检查。
3. **领域敏感**。同一个词在不同领域极性可能相反（「屏幕大」在手机是优点，在手表是缺点），跨领域迁移掉点严重。主题分类的领域迁移问题要轻得多。
4. **类别不均衡更常见**：真实评论里正面通常远多于负面（或反之），且负面样本往往更短/更极端，导致指标失真。
5. **方面混写**：一条评论同时评价多个方面（位置、房间、服务、价格），标签只有整体一个，模型需要学会「按整体而非按最强烈的单词」判断——这是文档级情感分析的理论局限，需要 ABSA（方面级情感分析）才能精确解决。

</details>

**Q2. 词袋模型完全处理不了「服务不好」，你会怎么改？请给出至少三种方案并说明取舍。**

<details><summary>参考答案</summary>

| 方案 | 做法 | 效果 | 代价 |
|------|------|------|------|
| **否定词拼接** | 检测到否定词后，把它与后 1–2 个词用下划线拼成新 token：`不 好` → `不_好` | 词袋立刻能区分「好」与「不_好」；实现 < 20 行 | 依赖分词质量；连续否定（「不是不好」）仍会出错；需人工定窗口大小 |
| **保留 n-gram 特征** | `TfidfVectorizer(ngram_range=(1,2))`，让「不 好」「不 推荐」成为独立特征 | 零代码改动，覆盖大部分否定与部分转折 | 特征维度膨胀、稀疏度上升，需要 `min_df` 剪枝 |
| **规则后处理** | 训练完模型后，对「命中否定词窗口」的预测做极性翻转，或把否定计数作为额外特征喂给树模型 | 可解释、可与模型叠加 | 规则需维护，边界情况多 |
| **换 FastText/TextCNN** | 用 wordNgrams 或卷积核捕捉局部「否定+情感词」模式 | 效果优于纯词袋 | 需要深度模型训练；上下文仍有限 |
| **换 BERT** | 上下文相关的表示天然建模否定与远距离依赖 | 效果最好（通常提升显著） | 需要 GPU、推理慢、模型大 |

工程上的推荐顺序：**先加 n-gram（零成本）→ 再试否定拼接（低成本、可解释）→ 用验证集量化收益 → 若仍不足再上 BERT**。

关键是**必须做对照实验**。否定拼接看似显然有效，但在某些数据集上会因为切碎了原有特征、引入稀疏噪声而掉点。正确做法是固定其他条件，只改这一项，比较验证集 macro-F1，并至少跑 3 个种子确认差异稳定。

最后提醒：处理否定时要**区分「否定情感词」与「否定事实」**。"没有窗户」是事实陈述（偏负面），「不算差」是弱正面。规则很难覆盖全部，这也是 BERT 在这个任务上优势明显的原因。

</details>

**Q3. 情感分析项目上线后，产品说「负面评论老是漏掉」。你怎么定位和解决？**

<details><summary>参考答案</summary>

先把它定义成一个可度量的工程问题：**「漏掉」= 负面类的召回率（Recall）不足**，对应混淆矩阵里的 FN 高。按「先量化 → 再归因 → 再修」的流程处理。

**第一步：量化**
从线上抽样 200–500 条被预测为「正面」的评论，人工复核，统计真实的误判率与误判类型分布。同时看离线混淆矩阵：负面类的 Recall 是多少？与线上是否一致（不一致说明训练/线上分布不同）？

**第二步：归因（按可能性排序）**

| 归因 | 检查方法 |
|------|----------|
| 阈值过高 | 固定 0.5 阈值导致负面需要「非常负面」才被判出。看不同阈值下的 P/R 曲线 |
| 类别不均衡 + 训练目标未加权 | 看训练集正负比；检查是否用了 `class_weight` 或焦点损失 |
| 否定/转折建模不足 | 抽出 FN 样本看是否集中在「不…」「…但…」句式 |
| 难以察觉的隐晦负面 | 如「还行吧」「和描述差不多」，字面无负面词但实际不满——词袋无能为力 |
| 领域漂移 | 线上出现新的业务/产品词，训练语料没有 |
| 标注偏置 | 训练集的「负面」定义与业务不一致（如业务把「一般」视为负面，而标注集算正面） |

**第三步：修复（按性价比排序）**
1. **调阈值**：若业务对漏检（FN）更敏感，直接降低正面阈值。这是零成本、当天可上线的修法。
2. **类别加权或重采样**：`class_weight='balanced'` 或对负面类过采样，提升召回。
3. **补充难例**：把线上复核出的 FN 样本加入训练集（这是最有价值的数据，因为它们是真实分布下的难例）。
4. **换更强的模型**：上 BERT 微调，能处理否定、转折和隐晦表达。
5. **明确标注规范**：与业务对齐「什么算负面」，把「一般/还行」这类边界统一。

**第四步：监控**
上线后持续监控负面类的召回与置信度分布；设置**低置信度转人工**通道（如 `Confidence < 0.6` 自动送审），避免误判直接触达用户；定期用线上数据重训。

一句话总结：漏检问题几乎从不只靠「换更大的模型」解决，**阈值调整 + 难例回流 + 标注对齐**通常能拿到大部分收益。

</details>

## 6. 自测题

**1. 某情感分类任务训练集正样本 8000 条、负样本 2000 条。模型在测试集上 accuracy = 0.88。你会对结果做什么判断？**

<details><summary>参考答案</summary>

**首先怀疑 accuracy 被多数类撑起来的**。正负比是 4:1，一个「全部预测为正」的模型 accuracy 就是 0.8。所以 0.88 相对基线（0.8）只提升了 8 个点，实际能力可能远不如 0.88 这个数字给人的印象。

要做的三件事：

1. **看逐类指标**：负类的 Precision/Recall 是多少？如果负类召回只有 0.5，说明模型对负类基本无能——而业务上负面评论往往最重要。
2. **看 macro-F1**：在 4:1 不均衡下，macro-F1 会把两个类等权平均，更能反映真实水平。它可能只有 0.75 左右。
3. **看「相对基线」的提升**：把「全预测多数类」作为基线（accuracy 0.8、macro-F1 约 0.44），模型相对它的提升才是真实价值。

处理方向：

- 用 `class_weight='balanced'` 或对负类过采样，提升负类召回。
- 评估指标从 accuracy 换成 macro-F1 / AUC / PR-AUC，并单独报告负类指标。
- 检查标注：负样本只有 2000 条时，是否覆盖了各类负面表达？可能需补标注。

</details>

**2. 为什么「先划分数据集，再做 TF-IDF」很重要？在情感分析里泄漏的具体表现是什么？**

<details><summary>参考答案</summary>

**原因**：`fit` 阶段会从传入数据中学习**词表**和**IDF（文档频率）**。如果先在全量数据上 `fit`，测试集的统计信息就泄漏进了特征：

1. **IDF 泄漏**：IDF 由包含测试文档的语料统计得到，模型提前"知道"了测试数据的词分布。
2. **词表泄漏**：测试集独有的词进入词表，而线上推理时这些词在训练词表里不存在——离线评估因此高估了覆盖率。
3. **`max_features` 选择泄漏**：被保留的高频特征由全体数据决定。

在情感分析中的具体表现：假设测试集里有一条「退订」这个词只出现在负面评论中，且训练集从未出现。若用全量数据 `fit`，`退订` 会进词表并在测试时得到较高权重，模型轻松判对这条——但线上一旦遇到训练集没有的新词，模型就抓瞎。**离线指标虚高、线上断崖下跌**是其典型症状。

**正确做法**：先 `train_test_split`，然后只在训练集上 `fit_transform`，测试集只能 `transform`，并且把同一个 vectorizer 与模型一起持久化。同样的原则适用于标准化（均值方差）、停用词自动生成、特征选择（卡方/互信息）、SVD 降维、SMOTE 过采样——所有依赖数据统计量的步骤都必须在训练集上拟合。

验证是否泄漏的实用手段：对比「随机划分」与「按时间/来源划分」的指标差距。若随机划分的指标明显更高，往往就存在泄漏（同源样本跨集、近似重复样本等）。

</details>

**3. 请设计一个实验，验证「把否定词与后一词拼接」这个改动是否真的有效。**

<details><summary>参考答案</summary>

核心原则：**单一变量 + 多次重复 + 统计显著**。不要只跑一次就下结论。

**实验设计**

| 项 | 设置 |
|----|------|
| 数据 | 同一份训练/验证/测试划分（固定随机种子，划分文件落盘复用） |
| 对照组 A（baseline） | 原始 jieba 分词 + 去停用词（**保留**否定词与转折词） |
| 实验组 B | A 的基础上，把否定词与后 1 个词拼接（`不_好`） |
| 实验组 C（可选） | 否定窗口 = 2（`不_太_好`），检查窗口大小的影响 |
| 变量控制 | vectorizer 参数、模型、超参、随机种子、训练轮数**全部相同** |
| 模型 | 至少两个：逻辑回归（线性）与 FastText/TextCNN（深度），避免结论只在一种模型上成立 |
| 指标 | 主要指标：验证集 **macro-F1**；辅助：负类（少数类）Recall、accuracy、AUC |
| 重复 | **每个配置跑 5 个随机种子**，报告均值 ± 标准差 |
| 显著性 | 对 A 与 B 的 5 次结果做配对 t 检验（或用 bootstrap 置信区间），确认差异不是噪声 |
| 细分评估 | 单独构造一个「含否定词」的测试子集（如从验证集中筛出含「不/没/无」的样本），看 B 在该子集上的提升幅度 |

**判读标准**

- 如果 B 的 macro-F1 均值提升 > 1 个点，且 5 次中至少 4 次优于 A、配对检验 p < 0.05 → 判定有效，保留改动。
- 如果提升在标准差范围内波动（如 +0.3 ± 0.8 点）→ 判定无显著收益，不值得增加代码复杂度。
- 如果只在否定子集上有提升、整体持平 → 说明该改动**定向有效**，可以作为特征之一保留，并在报告中如实说明。

**额外要记录的信息**：特征维度变化（拼接会改变词表大小）、训练/推理耗时变化、以及在**线上 OOD 数据**（新领域样本）上的表现——离线的提升不一定能迁移到线上。

最后一步是**消融实验（ablation）**：把改动单独关掉，确认收益确实来自这一项，而不是来自同时改动的其他东西。这也是论文里报告结果的标准做法。

</details>

## 7. 延伸阅读

- ChnSentiCorp 中文酒店评论情感语料（第 4 节数据分析所用语料来源）：https://github.com/chatopera/ChnSentiCorp
- 中文情感分析常用数据集汇总（ChnSentiCorp、weibo_senti_100k、online_shopping_10_cats、NLPCC2014）：https://github.com/SophonPlus/ChineseNlpCorpus
- Hugging Face 中文情感模型（可直接 `pipeline('sentiment-analysis')` 调用）：https://huggingface.co/models?language=zh&pipeline_tag=text-classification
- 情感分析综述《Deep Learning for Sentiment Analysis: A Survey》(2018)：https://arxiv.org/abs/1801.07883
- 方面级情感分析综述《A Survey on Aspect-Based Sentiment Analysis: Tasks, Methods, and Challenges》：https://arxiv.org/abs/2203.01054
- 文本数据增强方法综述《A Survey of Data Augmentation Approaches for NLP》(2021)：https://arxiv.org/abs/2105.03075
- scikit-learn 概率校准与阈值选择（`precision_recall_curve`、`CalibratedClassifierCV`）：https://scikit-learn.org/stable/modules/calibration.html

---

[⬅️ 返回 NLP 目录](README.md)
