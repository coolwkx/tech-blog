---
article_id: kp-2cea5ca328e97554
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 2
learning_objective: 理解并验证：取数三件套：[] / loc / iloc
---

# 取数三件套：[] / loc / iloc

> **学习目标**：能够解释「取数三件套：[] / loc / iloc」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 核心概念

## 本次只学这一点

| 写法 | 含义 | 切片是否**包右** |
| --- | --- | --- |
| `df["col"]` | 取一列（Series） | — |
| `df[["c1","c2"]]` | 取多列（DataFrame） | — |
| `df[bool_series]` | 布尔过滤行 | — |
| `df.loc[行标签, 列名]` | **按标签**取数 | ✅ **包含右端点** |
| `df.iloc[行号, 列号]` | **按位置**取数 | ❌ 包左不包右（同 Python 切片） |
| `df.at[行, 列]` / `df.iat[行号, 列号]` | 取**单个标量**，最快 | — |
```python
stock.loc[stock.index[0], "open"] # 23.53 按标签
stock.iloc[0, 1] # 25.88 按位置
stock["open"][stock.index[0]] # 链式（先列后行）
stock.loc[:, "open":"low"].shape # 列切片：(643, 4)
```
| 常见误用 | 后果 |
| --- | --- |
| `df[0]` 想取第 0 列 | 按列名 `0` 查找，找不到就 `KeyError`；真正想取列要用 `df.iloc[:, 0]` 或列名 |
| `df[0:3]` 想按标签切片 | `[]` 里的整数切片是**按位置**的，不是 `loc` |
| 链式赋值 `df[df.a>1]["b"] = 1` | pandas 3.x 下**不会生效**并给出告警（CoW），必须用 `df.loc[df.a>1, "b"] = 1` |

**推荐固化的两个习惯**：① 取数据一律用 `loc`（标签）或 `iloc`（位置），不用裸 `[]` 做复杂索引；② 赋值一律用 `df.loc[条件, 列] = 值` 单步完成。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「取数三件套：[] / loc / iloc」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
