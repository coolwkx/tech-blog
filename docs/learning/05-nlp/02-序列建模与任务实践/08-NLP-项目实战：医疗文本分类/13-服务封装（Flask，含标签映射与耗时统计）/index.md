---
article_id: kp-0d93bdf5f810da5e
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 12
learning_objective: 理解并验证：服务封装（Flask，含标签映射与耗时统计）
---

# 服务封装（Flask，含标签映射与耗时统计）

> **学习目标**：能够解释「服务封装（Flask，含标签映射与耗时统计）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 可运行示例

## 本次只学这一点

```text
# 依赖: pip install flask torch transformers
import json
import time

import torch
from flask import Flask, Response, request
from transformers import AutoModelForSequenceClassification, AutoTokenizer

CLS = "[CLS]"
id_to_name = {0: "finance", 1: "realty", 2: "stocks", 3: "education", 4: "science",
 5: "society", 6: "politics", 7: "sports", 8: "game", 9: "entertainment"}
# 医疗 13 类的映射同理，务必从 class.txt 统一读取，训练/推理共用同一份

MODEL_DIR = "./medical_bert"
device = torch.device("cuda" if torch.cuda.is_available else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR).to(device)
model.eval

app = Flask(__name__)

def inference(text, pad_size=128):
 enc = tokenizer(text, add_special_tokens=True, max_length=pad_size,
 padding="max_length", truncation=True, return_tensors="pt")
 enc = {k: v.to(device) for k, v in enc.items()}
 with torch.no_grad:
 logits = model(**enc).logits
 probs = torch.softmax(logits, dim=-1)[0]
 pred_id = int(probs.argmax)
 return id_to_name[pred_id], float(probs[pred_id])

@app.route("/v1/medical/", methods=["POST"])
def main_server:
 request_json = request.get_json
 content = request_json["content"]

 t1 = time.time
 label, confidence = inference(content)
 t2 = time.time

 return Response(
 status=200,
 response=json.dumps({
 "Status": "success",
 "Result": label,
 "Confidence": round(confidence, 4),
 "Time": "{:.4f}s".format(t2 - t1),
 }, ensure_ascii=False),
 mimetype="application/json",
 )

if __name__ == "__main__":
 app.run(host="127.0.0.1", port=5000)
```

三个工程要点：① **标签映射必须从 `class.txt` 统一读取**，训练与推理共用一份，否则会出现「静默的标签错位」（预测结果全部偏移一位）；② **返回置信度**，低置信度样本转人工，避免错误分诊直接触达患者；③ **推理必须 `model.eval` + `torch.no_grad`**，前者关闭 dropout 保证结果稳定，后者省显存。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「服务封装（Flask，含标签映射与耗时统计）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
