---
article_id: kp-e40fcfec18251ca5
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 9
learning_objective: 理解并验证：读写数据
---

# 读写数据

> **学习目标**：能够解释「读写数据」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 格式 | 读 | 写 |
| --- | --- | --- |
| CSV | `pd.read_csv(path, sep=",", usecols=..., encoding=..., index_col=..., nrows=...)` | `df.to_csv(path, sep=",", columns=..., header=, index=, mode="w"/"a", encoding=)` |
| Excel | `pd.read_excel(path, sheet_name=, index_col=, usecols=)` | `df.to_excel(path, sheet_name=, index=False)` |
| JSON | `pd.read_json(path, orient="records", lines=True)` | `df.to_json(path, orient="records", lines=True)` |
| MySQL | `pd.read_sql("select ...", engine)` | `df.to_sql("表名", engine, index=False, if_exists="append"/"replace")` |

**必须记住的三个坑**：

1. **`encoding`**：国内 CSV/Excel 常是 `gbk`/`gb18030`，不写会 `UnicodeDecodeError`；写出时统一 `utf-8`（Excel 想直接打开用 `utf-8-sig`）；
2. **`index`**：`to_csv` 默认把行索引也写成第一列，重新读时会出现 `Unnamed: 0` 这种幽灵列 —— 要么写时 `index=False`，要么读时 `index_col=0`；
3. **`dtype` 推断**：手机号、身份证、邮编这类"数字形态但不该参与运算"的字段会被推断成 `int64`，前导 0 会丢。要写 `dtype={"mobile": str}`。

> 的一个细节值得单独记住：`stock_day.csv` 的表头只有 14 个列名，而每行有 15 个字段。Pandas 发现"数据比表头多一列"，会自动**把第一列当作行索引**。这就是为什么读进来 `df.index` 已经是日期。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「读写数据」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
