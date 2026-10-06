---
article_id: kp-5472ce7fc0b18b3e
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 11
learning_objective: 理解并验证：BERT 微调与推理（含保存/加载）
---

# BERT 微调与推理（含保存/加载）

> **学习目标**：能够解释「BERT 微调与推理（含保存/加载）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
AdamW, get_linear_schedule_with_warmup)

MODEL_NAME = "bert-base-chinese"
MAX_LEN = 128
NUM_LABELS = 13
device = torch.device("cuda" if torch.cuda.is_available else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class MedicalTextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts, self.labels = texts, labels

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            enc = tokenizer(str(self.texts[idx]), add_special_tokens=True,
            max_length=MAX_LEN, padding="max_length",
            truncation=True, return_tensors="pt")
            return {
        "input_ids": enc["input_ids"].flatten,
        "attention_mask": enc["attention_mask"].flatten,
        "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }

        def train_model(texts, labels, epochs=3, batch_size=8, lr=2e-5):
            model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, num_labels=NUM_LABELS).to(device)
            loader = DataLoader(MedicalTextDataset(texts, labels), batch_size=batch_size, shuffle=True)

            optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
            total_steps = len(loader) * epochs
            scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps)
            criterion = nn.CrossEntropyLoss

            for epoch in range(epochs):
                model.train
                total_loss = 0.0
                for batch in loader:
                    batch = {k: v.to(device) for k, v in batch.items()}
                    outputs = model(input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"])
                    loss = criterion(outputs.logits, batch["labels"])
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0) # 梯度裁剪
                    optimizer.step
                    scheduler.step
                    total_loss += loss.item
                    print(f"epoch {epoch + 1} loss={total_loss / len(loader):.4f}")

                    # 保存与加载：只存 state_dict，换机器时用 map_location 处理设备
                    torch.save(model.state_dict, "medical_bert.bin")
                    return model

                def predict(model, text, id_to_name=None):
                    model.eval
                    enc = tokenizer(text, add_special_tokens=True, max_length=MAX_LEN,
                    padding="max_length", truncation=True, return_tensors="pt")
                    enc = {k: v.to(device) for k, v in enc.items()}
                    with torch.no_grad:
                        logits = model(**enc).logits
                        probs = torch.softmax(logits, dim=-1)[0]
                        pred_id = int(probs.argmax)
                        return (id_to_name[pred_id] if id_to_name else pred_id), float(probs[pred_id])

                    if __name__ == "__main__":
                        texts = ["什么是骨纤维瘤", "肾结石一般用什么药", "睡一觉醒睡不着咋搞的",
                        "请问出血性脑梗死症状是什么", "距骨骨折脱位做啥检查"] * 8
                        labels = [0, 5, 1, 3, 10] * 8

                        id_to_name = {0: "定义", 1: "病因", 2: "预防", 3: "临床表现", 4: "相关病症",
                        5: "治疗方法", 6: "所属科室", 7: "传染性", 8: "治愈率",
                        9: "禁忌", 10: "化验/体检方案", 11: "治疗时间", 12: "其他"}

                        model = train_model(texts, labels, epochs=1) # 演示只跑 1 轮
                        for t in ["肾结石一般用什么药", "婴儿会有痔疮吗"]:
                            print(t, "->", predict(model, t, id_to_name))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BERT 微调与推理（含保存/加载）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
