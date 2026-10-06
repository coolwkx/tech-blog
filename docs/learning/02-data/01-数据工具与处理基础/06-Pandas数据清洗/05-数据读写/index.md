---
article_id: kp-73f0a145e1799f69
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 4
learning_objective: 理解并验证：数据读写
---

# 数据读写

> **学习目标**：能够解释「数据读写」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 核心概念

## 本次只学这一点

| 方向 | API | 常用参数 |
| --- | --- | --- |
| 读 CSV | `pd.read_csv(path, sep=',', usecols=[...], index_col=0, encoding='gbk')` | `usecols` 只读指定列；`index_col` 指定索引列；中文文件常需 `encoding='gbk'` |
| 写 CSV | `df.to_csv(path, columns=[...], header=True, index=False, mode='w')` | **`index=False` 才不把索引写成单独一列**；`mode='a'` 为追加 |
| 读 MySQL | `pd.read_sql('表名或select语句', engine)` | 需先 `create_engine` |
| 写 MySQL | `df.to_sql('表名', engine, index=False, if_exists='append')` | `if_exists` 取 `fail`/`replace`/`append` |
| 读/写 JSON | `pd.read_json(path, orient='records', lines=True)` / `df.to_json(...)` | `lines=True` 表示每行一个 JSON 对象 |

```python
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8')
# └类型┘└─驱动─┘ └账号┘└密码┘ └───主机:端口/库名───┘ └──编码──┘
```

`read_json` 的 `orient` 取值：`'split'`（index/columns/data 三部分分开）、**`'records'`（`[{列:值}, ...]`，最常用）**、`'index'`、`'columns'`（默认）、`'values'`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「数据读写」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
