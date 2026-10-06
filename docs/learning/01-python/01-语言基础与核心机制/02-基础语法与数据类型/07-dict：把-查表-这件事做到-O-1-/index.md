---
article_id: kp-24dee4d49906d18a
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-c695752cdddc
learning_sourceId: c695752cdddc
learning_order: 6
learning_objective: 理解并验证：dict：把"查表"这件事做到 O(1)
---

# dict：把"查表"这件事做到 O(1)

> **学习目标**：能够解释「dict：把"查表"这件事做到 O(1)」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会安装并运行 Python（3.8+）；知道变量、`print`、`input` 的基本用法；了解 `int / float / str / bool` 四种标量类型。
>
> **所属主题**：基础语法与数据类型 · 核心概念

## 本次只学这一点

- **键必须是可哈希的**：`str / int / float / bool / tuple` 可以，`list / dict / set` 不行。
- 常用方法：

| 方法 | 作用 | 备注 |
| --- | --- | --- |
| `d[key]` | 取值 | 键不存在抛 `KeyError` |
| `d.get(key, default)` | 安全取值 | 键不存在返回 `default`（默认 `None`） |
| `d[key] = v` | 新增或覆盖 | 键存在即修改 |
| `d.update(other)` | 批量合并 | 同名键会被覆盖 |
| `del d[key]` / `d.pop(key)` | 删除 | `pop` 返回被删的值 |
| `d.keys() / d.values() / d.items()` | 视图对象 | `items` 最常用，配合 `for k, v in ...` |
| `key in d` | 成员判断 | **判断的是键**，不是值 |

**词频统计范式**（务必背下来，后面 NLP 章节仍在使用）：
```python
word_count = {}
for word in text.split():
 word_count[word] = word_count.get(word, 0) + 1
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「dict：把"查表"这件事做到 O(1)」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)
