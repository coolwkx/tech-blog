---
article_id: kp-1c1f6bdf05444441
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a66bd7ad2f1
learning_sourceId: 3a66bd7ad2f1
learning_order: 11
learning_objective: 理解并验证：字级 B/M/E/S 标注：把分词变成序列标注
---

# 字级 B/M/E/S 标注：把分词变成序列标注

> **学习目标**：能够解释「字级 B/M/E/S 标注：把分词变成序列标注」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理流水线、序列标注的基本概念、Python 正则与字典操作。
>
> **所属主题**：中文分词与子词分词 · 可运行示例

## 本次只学这一点

```python
def word_to_bmes(words):
    """把分词结果转成 B/M/E/S 标签序列（字符级）"""
    labels = []
    for w in words:
        if len(w) == 1:
            labels.append("S")
        else:
            labels.append("B")
            labels.extend(["M"] * (len(w) - 2))
            labels.append("E")
            return labels

        def bmes_to_words(chars, labels):
            """从 B/M/E/S 标签还原分词结果，并顺带校验标签合法性"""
            words, buf = [], ""
            for ch, tag in zip(chars, labels):
                buf += ch
                if tag in ("E", "S"):
                    words.append(buf)
                    buf = ""
                    if buf: # 结尾残留说明标签序列不合法
                        words.append(buf)
                        return words

                    chars = list("我喜欢自然语言处理")
                    labels = word_to_bmes(["我", "喜欢", "自然语言处理"])
                    print("".join(chars))
                    print(labels)
                    print(bmes_to_words(chars, labels))
```

预期输出：`['B', 'B', 'E', 'B', 'M', 'M', 'M', 'M', 'E']`，还原得到 `['我', '喜欢', '自然语言处理']`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「字级 B/M/E/S 标注：把分词变成序列标注」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)
