---
article_id: kp-6a4b3332628c5f29
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-cea0dd524785
learning_sourceId: cea0dd524785
learning_order: 12
learning_objective: 理解并验证：BERT 微调（第 3 档，替代方案）
---

# BERT 微调（第 3 档，替代方案）

> **学习目标**：能够解释「BERT 微调（第 3 档，替代方案）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 08/09 篇 BERT 微调、第 01 篇的文本数据分析。
>
> **所属主题**：NLP 项目实战：情感分析 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 微调（第 3 档，替代方案）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/11-NLP项目实战-情感分析.md)
