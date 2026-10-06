---
article_id: kp-928d88457ce73a42
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-ab1dbc27d73f
learning_sourceId: ab1dbc27d73f
learning_order: 15
learning_objective: 理解并验证：用 BERT 做句子对分类（贴合的中文句子关系案例）
---

# 用 BERT 做句子对分类（贴合的中文句子关系案例）

> **学习目标**：能够解释「用 BERT 做句子对分类（贴合的中文句子关系案例）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇的 TF-IDF 与余弦相似度、第 04 篇的词向量、第 08 篇的 attention、第 09 篇的 BERT 与句对任务。
>
> **所属主题**：文本相似度与语义匹配 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install transformers torch
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel

MODEL = "bert-base-chinese"
tok = AutoTokenizer.from_pretrained(MODEL)
bert = AutoModel.from_pretrained(MODEL)
bert.eval

class SentencePairClassifier(nn.Module):
    """3 分类：蕴含 / 中立 / 矛盾（案例是 2 分类：是否下半句）"""

    def __init__(self, num_labels=2, hidden=768):
        super.__init__
        self.classifier = nn.Linear(hidden, num_labels)

        def forward(self, input_ids, token_type_ids, attention_mask):
            with torch.no_grad:
                out = bert(input_ids=input_ids, token_type_ids=token_type_ids,
                attention_mask=attention_mask)
                # 句对任务取 [CLS] 的表示（pooler_output）
                return self.classifier(out.pooler_output)

            model = SentencePairClassifier
            sent1 = "我想订一张明天去北京的机票"
            sent2 = "帮我查一下明天飞北京的航班"

            enc = tok(sent1, sent2, return_tensors="pt", truncation=True, max_length=128)
            print("input_ids :", enc["input_ids"].shape)
            print("token_type_ids :", enc["token_type_ids"].tolist()[0][:20], "...（前段为0，后段为1）")
            print("attention_mask :", enc["attention_mask"].shape)

            with torch.no_grad:
                logits = model(enc["input_ids"], enc["token_type_ids"], enc["attention_mask"])
                print("logits:", logits.tolist())
```

注意 `token_type_ids` 的输出：句子 A 的部分是 0、句子 B 的部分是 1，这正是 Segment Embedding 的来源。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 BERT 做句子对分类（贴合的中文句子关系案例）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/10-文本相似度与语义匹配.md)
