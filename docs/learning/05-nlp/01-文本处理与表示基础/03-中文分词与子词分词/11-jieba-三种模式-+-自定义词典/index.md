---
article_id: kp-d78fe47f7a84498b
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-3a66bd7ad2f1
learning_sourceId: 3a66bd7ad2f1
learning_order: 10
learning_objective: 理解并验证：jieba 三种模式 + 自定义词典
---

# jieba 三种模式 + 自定义词典

> **学习目标**：能够解释「jieba 三种模式 + 自定义词典」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理流水线、序列标注的基本概念、Python 正则与字典操作。
>
> **所属主题**：中文分词与子词分词 · 可运行示例

## 本次只学这一点

```python
# 依赖: pip install jieba
import jieba

content = "教育是一家上市公司，旗下有品牌。我是在这里学习人工智能"

print("精确模式:", jieba.lcut(content))
print("全模式 :", jieba.lcut(content, cut_all=True))
print("搜索模式:", jieba.lcut_for_search(content))

# 繁体支持
print("繁体 :", jieba.lcut("煩惱即是菩提，我暫且不提"))

# 自定义词典: 每行「词语 词频 词性」，后两项可省略
with open("userdict.txt", "w", encoding="utf-8") as f:
 f.write("教育 100 n\n")
 f.write(" 100 n\n")
# 也可以直接 add_word，避免写文件
jieba.add_word("", freq=100, tag="n")

print("加词典后:", jieba.lcut(content))
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「jieba 三种模式 + 自定义词典」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/02-中文分词与子词分词.md)
