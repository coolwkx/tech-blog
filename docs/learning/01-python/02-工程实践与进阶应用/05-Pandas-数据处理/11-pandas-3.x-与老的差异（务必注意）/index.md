---
article_id: kp-92e4b0caa43eb556
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-3ced58665e5a
learning_sourceId: 3ced58665e5a
learning_order: 10
learning_objective: 理解并验证：pandas 3.x 与老的差异（务必注意）
---

# pandas 3.x 与老的差异（务必注意）

> **学习目标**：能够解释「pandas 3.x 与老的差异（务必注意）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：NumPy 的 ndarray、广播与 `axis` 语义（11 篇）、列表/字典（01 篇）、文件读写与编码（04 篇）。
>
> **所属主题**：Pandas 数据处理 · 最小可运行示例

## 本次只学这一点

基于 pandas 1.x/2.x，本机是 **pandas 3.0.1**，以下写法已经变化：

| 老写法 | 现状 | 新写法 |
| --- | --- | --- |
| `df.append(other)` | ❌ **已移除**（实测 `hasattr(df,"append")` 为 `False`） | `pd.concat([df, other], ignore_index=True)` |
| `df.applymap(f)` | ❌ **已移除**（实测 `hasattr` 为 `False`） | `df.map(f)`（元素级） |
| `pd.errors.SettingWithCopyWarning` | ❌ 该类已不存在 | 用 Copy-on-Write 语义，见下 |
| 链式赋值 `df[mask]["col"] = v` | ⚠️ 不生效，并给出 `ChainedAssignmentError` 告警 | `df.loc[mask, "col"] = v` |
| `pd.options.mode.copy_on_write = False` | ⚠️ 弃用告警，pandas ≥ 3.0 **始终开启 CoW** | 不要再设置该选项 |
| 字符串列 `dtype` 是 `object` | 现在默认是新的 `str`（`StringDtype`） | `dtype == object` 的判断要更新 |

**Copy-on-Write（CoW）意味着什么**：任何从别的 DataFrame 派生出来的对象（切片、筛选、列选择）都是**惰性视图**，一旦被修改，pandas 会自动复制，因此**永远不会影响源数据**。两个后果：① `df[df.a > 1]["a"] = 99` 这类链式赋值**静默失效**（同时给出告警），必须改成单步 `loc` 赋值；② 以前为了消除 `SettingWithCopyWarning` 而到处写的 `.copy`，现在大多数情况可以省掉。

```python
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
sub = df[df["a"] > 1]
sub["a"] = 99 # CoW：只改 sub，df 不受影响
df.loc[df["a"] > 1, "a"] = 88 # 正确：单步 loc 赋值，直接改 df
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「pandas 3.x 与老的差异（务必注意）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/12-Pandas数据处理.md)
