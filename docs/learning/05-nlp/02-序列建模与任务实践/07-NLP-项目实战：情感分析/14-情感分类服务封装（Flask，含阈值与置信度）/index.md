---
article_id: kp-fe2e06ab56ff0fb4
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cea0dd524785
learning_sourceId: cea0dd524785
learning_order: 13
learning_objective: 理解并验证：情感分类服务封装（Flask，含阈值与置信度）
---

# 情感分类服务封装（Flask，含阈值与置信度）

> **学习目标**：能够解释「情感分类服务封装（Flask，含阈值与置信度）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。
>
> **所属主题**：NLP 项目实战：情感分析 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「情感分类服务封装（Flask，含阈值与置信度）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)
