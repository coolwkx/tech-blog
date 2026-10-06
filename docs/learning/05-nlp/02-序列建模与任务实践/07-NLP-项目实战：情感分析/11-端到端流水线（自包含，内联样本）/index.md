---
article_id: kp-dd46158d28d63061
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cea0dd524785
learning_sourceId: cea0dd524785
learning_order: 10
learning_objective: 理解并验证：端到端流水线（自包含，内联样本）
---

# 端到端流水线（自包含，内联样本）

> **学习目标**：能够解释「端到端流水线（自包含，内联样本）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。
>
> **所属主题**：NLP 项目实战：情感分析 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「端到端流水线（自包含，内联样本）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)
