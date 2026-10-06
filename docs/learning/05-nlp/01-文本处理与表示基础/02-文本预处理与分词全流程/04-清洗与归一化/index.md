---
article_id: kp-b8a2bd739697f943
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-b5809cd6128d
learning_sourceId: b5809cd6128d
learning_order: 3
learning_objective: 理解并验证：清洗与归一化
---

# 清洗与归一化

> **学习目标**：能够解释「清洗与归一化」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 字符串与 `re` 模块；正则表达式；神经网络需要整数 id（embedding 查表）；Transformer 的 `attention_mask` 概念。
>
> **所属主题**：文本预处理与分词全流程 · 核心思想

## 本次只学这一点

| 形式 | 全称 | 做什么 | 典型效果 |
| --- | --- | --- | --- |
| NFC | Canonical Composition | 规范等价 + 尽可能组合 | `e`+`U+0301` → `é` |
| NFD | Canonical Decomposition | 规范等价 + 拆开 | `é` → `e`+`U+0301` |
| NFKC | Compatibility Composition | 兼容等价 + 组合 | `ＡＢＣ`→`ABC`，`①`→`1`，`㍿`→`株式会社` |
| NFKD | Compatibility Decomposition | 兼容等价 + 拆开 | `km²`→`km2`，`ﬁ`→`fi` |

**NFKC 是 NLP 里最常用的形式**（统一全角、连字、上下标、罗马数字），但它**不是无损的**：兼容等价会把原本语义不同的字符画上等号。中文场景尤其要注意 `ud.normalize("NFKC", "，") == ","`，全角标点会被换成半角 ASCII。

```python
import re, html
import unicodedata as ud

raw = ("<p>限时 5 折&nbsp;仅需&nbsp;<b>￥3.5</b>！</p> ""官网 https://a./x?y=1 活动\u200b截止 12\u202f月\ufeff1 日\x07")
text = html.unescape(raw) # &nbsp; -> \xa0
text = re.sub(r"<[^>]+>", "", text) # 去 HTML 标签
text = re.sub(r"https?://\S+|www\.\S+", " <URL> ", text) # URL 占位，别直接删
text = "".join(ch for ch in text if ud.category(ch)[0] != "C") # 去控制符 / 零宽字符
text = re.sub(r"\s+", "", text).strip() # 合并空白
print(text) # 限时 5 折 仅需 ￥3.5 ！ 官网 <URL> 活动截止 12 月1 日
print(ud.normalize("NFKC", text).lower()) # 限时 5 折 仅需 ¥3.5 ! 官网 <url> 活动截止 12 月1 日
```

`\u200b`（零宽空格）、`\ufeff`（BOM）、`\u00ad`（软连字符）的类别都是 `Cf`，**`str.strip()` 与 `str.split()` 都拿它们没办法**（`isspace` 为 `False`），混进词里就会造出一个词表里不存在的「新词」。

**清洗过度导致信息丢失**（这一栏比「怎么清洗」更值得记住）：

| 过度操作 | 丢掉了什么 | 后果 |
| --- | --- | --- |
| 删除全部标点 | 否定、语气、句边界 | `好，但是太贵了！` → `好但是太贵了`，情感极性可能反转 |
| 删除数字中的 `.` | 数值语义 | `3.5 折` → `35 折`；`v1.2` → `v12` |
| 全局 NFKC | 全角标点、圈号、上标 | `①`→`1` 丢失顺序标记；`km²`→`km2`；中文 `，`→`,` |
| 全局 `lower` | 大小写携带的类别信息 | `Apple`（公司）vs `apple`（水果）；`US`→`us`；`mAh`→`mah` |
| 删除停用词 | 否定词、程度副词 | `not good` → `good`；`非常不好` → `不好` |

经验法则：**清洗规则要么由验证集指标证明有效，要么不进流水线**。标注数据不足时宁可保留噪声，也不要删掉语义。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「清洗与归一化」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/01-文本预处理与分词全流程.md)
