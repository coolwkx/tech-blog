---
article_id: kp-b9937b3bcbc3f0ea
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-94a81d666c0a
learning_sourceId: 94a81d666c0a
learning_order: 12
learning_objective: 理解并验证：冻结 BERT + 自定义分类头（的核心范式）
---

# 冻结 BERT + 自定义分类头（的核心范式）

> **学习目标**：能够解释「冻结 BERT + 自定义分类头（的核心范式）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 08 篇的 Transformer Encoder 与 self-attention、第 04 篇的静态词向量局限、Python 类与 PyTorch 训练循环。
>
> **所属主题**：BERT 与预训练模型 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch
import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModel

MODEL_NAME = "bert-base-chinese"
device = torch.device("cuda" if torch.cuda.is_available else "cpu")

my_pre_model = AutoModel.from_pretrained(MODEL_NAME).to(device)
my_pre_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class AiModel(nn.Module):
    """预训练模型提特征 + 自定义分类头"""

    def __init__(self, num_labels=2, hidden=768):
        super.__init__
        self.linear = nn.Linear(hidden, num_labels)

        def forward(self, input_ids, token_type_ids, attention_mask):
            # 关键：不更新预训练模型参数，把它当特征提取器
            with torch.no_grad:
                bert_output = my_pre_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                )
                # last_hidden_state: [B, L, 768]；pooler_output: [B, 768]（[CLS] 位置的表示）
                return self.linear(bert_output.pooler_output)

            def collate_fn(batch):
                """DataLoader 的批处理函数：把文本张量化"""
                sents = [item["text"] for item in batch]
                labels = [item["label"] for item in batch]
                inputs = my_pre_tokenizer.batch_encode_plus(
                sents, truncation=True, max_length=64,
                padding="max_length", return_tensors="pt",
                )
                return (inputs["input_ids"], inputs["token_type_ids"],
            inputs["attention_mask"], torch.LongTensor(labels))

            if __name__ == "__main__":
                # 内联小数据集
                dataset = [{"text": "这个酒店位置好，服务热情", "label": 1},
                {"text": "位置很好，房间干净", "label": 1},
                {"text": "早餐很差，服务不到位", "label": 0},
                {"text": "隔音太差，体验不好", "label": 0}] * 8

                model = AiModel.to(device)
                for p in my_pre_model.parameters():
                    p.requires_grad_(False) # 冻结

                    criterion = nn.CrossEntropyLoss(reduction="mean")
                    # 只优化自定义头，学习率可以比全量微调大
                    optimizer = AdamW(model.parameters(), lr=5e-4)

                    model.train
                    for epoch in range(5):
                        total_loss = 0.0
                        for i in range(0, len(dataset), 8):
                            inputs_ids, token_type_ids, attention_mask, labels = collate_fn(dataset[i:i + 8])
                            inputs_ids = inputs_ids.to(device)
                            token_type_ids = token_type_ids.to(device)
                            attention_mask = attention_mask.to(device)
                            labels = labels.to(device)

                            output = model(inputs_ids, token_type_ids, attention_mask)
                            loss = criterion(output, labels)
                            optimizer.zero_grad()
                            loss.backward()
                            optimizer.step
                            total_loss += loss.item
                            print(f"epoch {epoch + 1} loss={total_loss:.4f}")
```

**全部微调**只需三处改动：把 `with torch.no_grad` 去掉、`requires_grad_(True)`、学习率降到 2e-5~5e-5，并把 `my_pre_model.parameters()` 一起加进优化器。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「冻结 BERT + 自定义分类头（的核心范式）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/09-BERT与预训练模型.md)
