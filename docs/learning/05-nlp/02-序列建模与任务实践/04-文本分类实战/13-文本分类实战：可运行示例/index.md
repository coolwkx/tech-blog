---
article_id: kp-b02cdd32cb0edae5
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d8ba07ef6cec
learning_sourceId: d8ba07ef6cec
learning_order: 12
learning_objective: 理解并验证：文本分类实战：可运行示例
---

# 文本分类实战：可运行示例

> **学习目标**：能够解释「文本分类实战：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 02 篇分词、第 03 篇 TF-IDF 与稀疏矩阵、第 04 篇词向量与 FastText、sklearn 的基本用法。
>
> **所属主题**：文本分类实战 · 可运行示例

## 本次只学这一点

下面是一个**自包含**的端到端中文文本分类示例：内联造 60 条三分类短文本，走完「分词 → TF-IDF → 逻辑回归 → 多指标评估 → 混淆矩阵 → 错误分析」。

```python
# 依赖: pip install scikit-learn jieba numpy
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
confusion_matrix, f1_score)
from sklearn.model_selection import train_test_split

# ---------- 1. 内联构造数据（实际项目改从 train.txt 读取 `文本\t标签`） ----------
raw = [
# 体育
("湖人队赢得总冠军，詹姆斯发挥出色", "sports"),
("国足客场逼平对手，晋级希望仍在", "sports"),
("奥运会游泳决赛，中国队再添一金", "sports"),
("nba季后赛首轮，勇士淘汰国王", "sports"),
("中超联赛第10轮，泰山主场取胜", "sports"),
# 财经
("美联储宣布加息25个基点，美股震荡", "finance"),
("央行下调存款准备金率，释放流动性", "finance"),
("人民币汇率小幅升值，出口企业承压", "finance"),
("A股三大指数集体收跌，成交量萎缩", "finance"),
("国际油价上涨，能源板块走强", "finance"),
# 科技
("国产芯片实现新突破，性能提升明显", "science"),
("人工智能大模型发布，支持多模态输入", "science"),
("量子计算原型机完成新一轮测试", "science"),
("新型电池材料量产，续航提升三成", "science"),
("航天器成功着陆月球背面", "science"),
] * 4 # 每条重复 4 次，共 60 条

texts = [t for t, _ in raw]
labels = [y for _, y in raw]

# ---------- 2. 分词（保持训练与推理同一函数） ----------
def cut(text: str) -> str:
    return "".join(jieba.lcut(text))

texts = [cut(t) for t in texts]

# ---------- 3. 划分数据（类别均衡，用 stratify 保证每类比例一致） ----------
X_train, X_test, y_train, y_test = train_test_split(
texts, labels, test_size=0.25, random_state=42, stratify=labels
)

# ---------- 4. 特征：TF-IDF（fit 只在训练集上做！） ----------
vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", ngram_range=(1, 2), min_df=1)
Xtr = vec.fit_transform(X_train)
Xte = vec.transform(X_test) # 注意：transform，不是 fit_transform
print("特征维度:", Xtr.shape)

# ---------- 5. 模型 ----------
clf = LogisticRegression(max_iter=1000, C=5.0, multi_class="multinomial")
clf.fit(Xtr, y_train)

# ---------- 6. 评估：多指标 + 逐类报告 ----------
pred = clf.predict(Xte)
print("accuracy : %.4f" % accuracy_score(y_test, pred))
print("macro-F1 : %.4f" % f1_score(y_test, pred, average="macro"))
print("weighted-F1 : %.4f" % f1_score(y_test, pred, average="weighted"))
print
print(classification_report(y_test, pred, digits=4))

# ---------- 7. 混淆矩阵 + 错误分析 ----------
classes = sorted(set(labels))
cm = confusion_matrix(y_test, pred, labels=classes)
print("混淆矩阵（行=真实，列=预测）")
print("" + "".join(f"{c[:7]:>9}" for c in classes))
for i, c in enumerate(classes):
    print(f"{c[:7]:>7} " + "".join(f"{v:>9}" for v in cm[i]))

    print("\n错例抽样：")
    for text, true, p in zip(X_test, y_test, pred):
        if true != p:
            print(f" 真实={true:<8} 预测={p:<8} 文本={text}")

            # ---------- 8. 特征重要性（线性模型看系数） ----------
            names = np.array(vec.get_feature_names_out)
            for cls, coef in zip(clf.classes_, clf.coef_):
                top = names[np.argsort(coef)[-6:]][::-1]
                print(f"{cls} 的关键词: {list(top)}")
```

**预期效果**：数据由三类高度可分的关键词构成，测试集准确率会到 1.0 左右。这不是「模型强」，而是**数据太干净** —— 真实项目里 accuracy 通常在 0.8–0.95 区间，且一定会有错例。把内联数据换成真实数据后，`classification_report` 与混淆矩阵才是真正有用的部分。

再看一眼「实际项目会怎么用」的对照写法（**不要直接运行**，因为需要数据文件）：

```python
# 说明：以下对应原始路径，仅作对照，请勿在无数据环境下运行
# import pandas as pd
# content = pd.read_csv("data/data/train.txt", sep="\t", names=["sentence", "label"])
# content["words"] = content["sentence"].apply(lambda s: "".join(jieba.cut(s))[:30])
# content.to_csv("./data/data/train_new.csv") # 只保留 30 个字符
# stop_words = open("./data/data/stopwords.txt", encoding="utf-8").read.split()
# tfidf = TfidfVectorizer(stop_words=stop_words)
# x_train, x_test, y_train, y_test = train_test_split(
# tfidf.fit_transform(content["words"]), content["label"],
# test_size=0.2, random_state=0)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「文本分类实战：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/05-文本分类实战.md)
