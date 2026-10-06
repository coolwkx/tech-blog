---
article_id: kp-57152182c4ac4c51
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a7ffbbd54d5
learning_sourceId: 3a7ffbbd54d5
learning_order: 13
learning_objective: 理解并验证：完整预处理流水线 + 语料体检
---

# 完整预处理流水线 + 语料体检

> **学习目标**：能够解释「完整预处理流水线 + 语料体检」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础语法、numpy / pandas 基本操作、正则表达式、PyTorch 的 `nn.Embedding` 概念。
>
> **所属主题**：NLP 概述与文本预处理 · 可运行示例

## 本次只学这一点

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
 return re.sub(r"\s+", "", text).strip()

def preprocess(text: str, max_len: int = 30) -> str:
 words = [w for w in jieba.lcut(clean(text)) if w.strip() and w not in STOPWORDS]
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
vocab = set(w for s in df["words"] for w in s.split())
print("词表大小:", len(vocab))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「完整预处理流水线 + 语料体检」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-NLP概述与文本预处理.md)
