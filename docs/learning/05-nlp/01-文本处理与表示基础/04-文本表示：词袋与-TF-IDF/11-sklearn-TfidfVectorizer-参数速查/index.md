---
article_id: kp-8194040f20d92155
learning_kind: article
learning_category: 05-nlp
learning_direction: foundations
learning_topic: topic-7afaf09df2e4
learning_sourceId: 7afaf09df2e4
learning_order: 10
learning_objective: 理解并验证：sklearn TfidfVectorizer 参数速查
---

# sklearn TfidfVectorizer 参数速查

> **学习目标**：能够解释「sklearn TfidfVectorizer 参数速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 01 篇的文本预处理与 n-gram 特征、第 02 篇的分词、numpy 稀疏矩阵的直观理解、余弦相似度。
>
> **所属主题**：文本表示：词袋与 TF-IDF · 方法细节

## 本次只学这一点

| 参数 | 默认 | 作用 | 建议 |
|------|------|------|------|
| `max_features` | None | 只保留词频最高的前 N 个词 | 中文任务常取 5000–50000；先看特征维度再定 |
| `min_df` | 1 | 忽略文档频率低于该值的词 | 取 2–5，可有效剪掉拼写错误与噪声 |
| `max_df` | 1.0 | 忽略文档频率高于该值（比例）的词，相当于自动停用词 | 取 0.8–0.95 |
| `stop_words` | None | 停用词表（list 或 `'english'`） | 中文必须自己传 list |
| `ngram_range` | (1,1) | n-gram 范围 | 短文本用 (1,2)，长文本 (1,1) 即可 |
| `sublinear_tf` | False | 用 $1+\log f$ 替代原始计数 | 词频差异大时开启 |
| `smooth_idf` | True | 加 1 平滑并整体 +1 | 通常保持开启 |
| `norm` | 'l2' | 归一化方式（`l1`/`l2`/None） | 保持 `'l2'` |
| `token_pattern` | `r"(?u)\b\w\w+\b"` | 分词正则 | **中文必须改**，否则单字被丢弃 |
| `lowercase` | True | 是否转小写 | 中文可设 False |

两个中文场景的经典坑：

- `token_pattern` 默认要求 token 至少 2 个 `\w`，中文单字会被直接丢掉。若已用 jieba 分好词并用空格连接，需设为 `r"(?u)\b\w+\b"`。
- `analyzer='char'` 可以做**字符级** TF-IDF，对中文短文本有时比词级更稳（无分词错误），可以作为对照实验。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「sklearn TfidfVectorizer 参数速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/01-预处理与表示/03-文本表示-词袋与TFIDF.md)
