---
article_id: kp-98fa8d9546ea09c2
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 2
learning_objective: 理解并验证：编码层：四个「长度」概念
---

# 编码层：四个「长度」概念

> **学习目标**：能够解释「编码层：四个「长度」概念」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 核心思想

## 本次只学这一点

「这个字符串有多长」有四种答案，混用就会出错。

| 层级 | 定义 | Python 里怎么数 | `é` | `e`+U+0301 | `👩‍👩‍👧‍👦` |
| --- | --- | --- | --- | --- | --- |
| byte | UTF-8 编码单元 | `len(s.encode("utf-8"))` | 2 | 3 | 25 |
| code unit | UTF-16 编码单元（JS/Java 的 `length`） | `len(s.encode("utf-16-le")) // 2` | 1 | 2 | 11 |
| code point | Unicode 码位 | `len(s)` | 1 | 2 | 7 |
| grapheme cluster | 用户感知的「一个字」 | 需 `regex` 的 `\X` | 1 | 1 | 1 |

`👩‍👩‍👧‍👦` 由 4 个 emoji + 3 个 ZWJ（U+200D）组成：7 个码位、11 个 UTF-16 单元、25 字节，但用户只当它是 1 个字。推论：`len(s)` 在中文里约等于字数，在 emoji 与组合字符上完全不可靠；前端 `maxlength="10"` 数的是 UTF-16 单元，与后端 `len(s)` 不是一回事；按字符截断必须按 grapheme cluster 切，否则会把 `é` 截成孤立的 `e`。

```python
import unicodedata as ud

pre, dec = "caf\u00e9", "cafe\u0301" # NFC 预组合 vs NFD 分解
print(len(pre), len(dec)) # 4 5 —— 长度不同
print(pre == dec) # False —— 码位序列不同
print(ud.normalize("NFC", pre) == ud.normalize("NFC", dec)) # True
for ch in ["A", "中", "é", "👍"]:
 print(repr(ch), hex(ord(ch)), len(ch.encode("utf-8"))) # 1 / 3 / 2 / 4 字节
family = "\U0001F469\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"
print(len(family), len(family.encode("utf-8")), # 7 码位 / 25 字节
 len(family.encode("utf-16-le")) // 2) # 11 UTF-16 单元
```

要点：`ud.normalize("NFC", s)` 只做**规范等价**，不会展开 `ﬁ` 这类连字；`s.encode("utf-8")` 才是磁盘 / HTTP 上的真实字节（中文 3 字节、emoji 4 字节）；`ud.combining(ch)` 非 0 只说明是组合记号，不等于「独立字符」。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「编码层：四个「长度」概念」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
