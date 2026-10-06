---
article_id: kp-9d71fb26fc01023d
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 5
learning_objective: 理解并验证：增删改查速查
---

# 增删改查速查

> **学习目标**：能够解释「增删改查速查」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 核心概念

## 本次只学这一点

| 目的 | API | 注意 |
| --- | --- | --- |
| 加列 | `df['新列'] = 标量 / 等长列表 / Series / 表达式` | 列表长度必须等于行数 |
| 加列（链式） | `df.assign(新列=值或函数)` | 返回**新 df**；函数需接收 df 作参数 |
| 删行/删列 | `df.drop([标签], axis=0/1)` | 默认删行；`axis=1` 删列；**默认返回新对象** |
| 删列（原地） | `del df['列']` | 永久删除，慎用 |
| 去重 | `df.drop_duplicates(subset=None, keep='first')` | `keep` 可取 `'first'/'last'/False` |
| Series 去重 | `s.drop_duplicates` / `s.unique` | 前者返回 Series，后者返回数组 |
| 替换值 | `s.replace(旧, 新, inplace=False)` | **精确整值匹配**；默认不改原数据 |
| 条件查询 | `df[布尔条件]` / `df.query('表达式')` / `s.isin([...])` | 多条件用 `&`、`\|`，**必须加括号** |
| 取头尾 / 切片 | `df.head(n)` / `df.tail(n)` / `df[起:止:步长]` | 默认 5 行；切片顾头不顾尾 |
| 排序 / 排名 | `df.sort_values(by, ascending=)` / `df.sort_index` / `s.rank(method=)` | 多字段传列表；`rank` 的 `pct=True` 返回百分比排名 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「增删改查速查」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
