---
article_id: kp-fe90bdcb1a3aa177
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 10
learning_objective: 理解并验证：三档模型端到端对比（自包含小样本）
---

# 三档模型端到端对比（自包含小样本）

> **学习目标**：能够解释「三档模型端到端对比（自包含小样本）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install scikit-learn jieba numpy
import re
import jieba
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# ---------- 内联构造 13 类医疗问句语料（实际项目换成 train.csv / test.csv） ----------
DATA = [
 ("什么是骨纤维瘤", 0), ("什么是心肌梗死", 0), ("什么叫高血压", 0),
 ("新生儿恶心的原因", 1), ("睡一觉醒睡不着咋搞的", 1), ("小儿发烧是什么引起的", 1),
 ("如何预防丘脑胶质瘤", 2), ("怎么预防糖尿病", 2), ("怎样预防高血压", 2),
 ("请问出血性脑梗死症状是什么", 3), ("心脏病有哪些表现", 3), ("肺炎的症状表现", 3),
 ("心脏病会引发癫痫吗", 4), ("高血压会引起头晕吗", 4),
 ("肾结石一般用什么药", 5), ("输尿管结石怎么治疗效果好", 5), ("脑梗死如何治疗", 5),
 ("肢端纤维角化瘤应该看啥医生", 6), ("失眠挂哪个科室", 6),
 ("甲真菌病容易感染不", 7), ("肺结核传染性强吗", 7),
 ("先天性外展性髋挛缩治愈比例", 8), ("肺癌的治愈率有多高", 8),
 ("阿立哌唑片对人有哪些危害", 9), ("孕期能不能吃这个药", 9),
 ("距骨骨折脱位做啥检查", 10), ("需要做CT还是核磁", 10), ("化验血糖要空腹吗", 10),
 ("艾滋病神经系统损害治好要多少天", 11), ("骨折要多久能恢复", 11),
 ("婴儿会有痔疮吗", 12), ("小孩打呼噜正常吗", 12),
] * 4 # 每条重复 4 次，共 128 条

STOPWORDS = set("的 了 在 是 我 有 和 就 也 很 只 要 一个 上 到 说".split())
QUESTION_WORDS = {"什么", "怎么", "如何", "咋", "多久", "多少", "哪"}

def preprocess(text):
 text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', ' ', text)
 words = jieba.lcut(text)
 return ' '.join(w for w in words
 if w.strip() and (w in QUESTION_WORDS or w not in STOPWORDS))

df = pd.DataFrame(DATA, columns=["text", "label"])
df["words"] = df["text"].apply(preprocess)

X_train, X_test, y_train, y_test = train_test_split(
 df["words"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
)

results = []

# ---------- 第 1 档：TF-IDF + 随机森林 ----------
vec = TfidfVectorizer(max_features=5000, token_pattern=r'(?u)\b\w+\b',
 lowercase=False, ngram_range=(1, 2))
Xtr, Xte = vec.fit_transform(X_train), vec.transform(X_test)

rf = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
rf.fit(Xtr, y_train)
pred_rf = rf.predict(Xte)
results.append(("RandomForest + TF-IDF",
 accuracy_score(y_test, pred_rf),
 f1_score(y_test, pred_rf, average="macro")))

# ---------- 第 1 档的对照：线性模型（医疗小数据上常优于 RF） ----------
lr = LogisticRegression(max_iter=1000, C=5.0, multi_class="multinomial")
lr.fit(Xtr, y_train)
pred_lr = lr.predict(Xte)
results.append(("LogisticRegression + TF-IDF",
 accuracy_score(y_test, pred_lr),
 f1_score(y_test, pred_lr, average="macro")))

# ---------- 特征重要性（解释「模型学到了什么」） ----------
names = np.array(vec.get_feature_names_out)
top = names[np.argsort(rf.feature_importances_)[-10:]][::-1]
print("随机森林 Top-10 重要特征:", list(top))

# ---------- 混淆矩阵 ----------
from sklearn.metrics import confusion_matrix, classification_report
print("\n逐类报告（随机森林）:")
print(classification_report(y_test, pred_rf, digits=3, zero_division=0))

# ---------- 结果汇总 ----------
print("\n模型对比:")
print(f"{'模型':<32}{'accuracy':>10}{'macro-F1':>10}")
for name, acc, f1 in results:
 print(f"{name:<32}{acc:>10.4f}{f1:>10.4f}")
```

把内联数据换成项目真实数据（`pd.read_csv("train.csv")`，列名为 `text` / `label_id` / `label_class`）即可得到与 2.5 节一致的对比结论。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「三档模型端到端对比（自包含小样本）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
