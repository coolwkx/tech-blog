---
article_id: kp-3cb7a2c311eb19d9
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-00dabbf9e8f9
learning_sourceId: 00dabbf9e8f9
learning_order: 10
learning_objective: 理解并验证：BIO 与 BIOES 互转 + 实体抽取
---

# BIO 与 BIOES 互转 + 实体抽取

> **学习目标**：能够解释「BIO 与 BIOES 互转 + 实体抽取」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的词性标注与 NER 两阶段拆解、概率论基础（条件概率、贝叶斯）、softmax 与交叉熵。
>
> **所属主题**：序列标注与实体识别 · 可运行示例

## 本次只学这一点

```python
def bio_to_spans(tokens, tags):
    """从 BIO 标签序列抽取实体片段 [(type, start, end_exclusive, text), ...]"""
    spans, cur = [], None
    for i, tag in enumerate(tags):
        if tag == "O":
            if cur:
                spans.append(cur)
                cur = None
                continue
            prefix, etype = tag.split("-", 1)
            if prefix == "B" or cur is None or cur[0] != etype:
                if cur:
                    spans.append(cur)
                    cur = [etype, i, i + 1, tokens[i]]
                else: # I- 连续
                    cur[2] = i + 1
                    cur[3] += tokens[i]
                    if cur:
                        spans.append(cur)
                        return spans

                    def spans_to_bioes(tokens, spans):
                        tags = ["O"] * len(tokens)
                        for etype, s, e, _ in spans:
                            if e - s == 1:
                                tags[s] = f"S-{etype}"
                            else:
                                tags[s] = f"B-{etype}"
                                tags[e - 1] = f"E-{etype}"
                                for i in range(s + 1, e - 1):
                                    tags[i] = f"I-{etype}"
                                    return tags

                                tokens = ["张", "三", "在", "北", "京", "大", "学", "工", "作"]
                                bio_tags = ["B-PER", "I-PER", "O", "B-ORG", "I-ORG", "I-ORG", "I-ORG", "O", "O"]

                                spans = bio_to_spans(tokens, bio_tags)
                                print("抽取到的实体:", spans) # [('PER', 0, 2, '张三'), ('ORG', 3, 7, '北京大学')]
                                print("转成 BIOES :", spans_to_bioes(tokens, spans))
                                # ['S-PER', 'O', 'O', 'B-ORG', 'I-ORG', 'I-ORG', 'E-ORG', 'O', 'O']
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BIO 与 BIOES 互转 + 实体抽取」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/06-序列标注与实体识别.md)
