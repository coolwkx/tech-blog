---
article_id: kp-318c7d4e4c41612b
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-c695752cdddc
learning_sourceId: c695752cdddc
learning_order: 9
learning_objective: 理解并验证：基础语法与数据类型：最小可运行示例
---

# 基础语法与数据类型：最小可运行示例

> **学习目标**：能够解释「基础语法与数据类型：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会安装并运行 Python（3.8+）；知道变量、`print`、`input` 的基本用法；了解 `int / float / str / bool` 四种标量类型。
>
> **所属主题**：基础语法与数据类型 · 最小可运行示例

## 本次只学这一点

下面这段代码覆盖了本篇所有主线，可直接复制运行（Python 3.8+ 输出一致）。
```python
# ---------- 1) 字典遍历 + 条件表达式：items 一次拿到键和值 ----------
scores = {"语文": 88, "数学": 92, "英语": 79}
for subject, score in scores.items():
 level = "优秀" if score >= 90 else ("及格" if score >= 60 else "不及格")
 print(f"{subject}: {score} -> {level}")
# 语文: 88 -> 及格
# 数学: 92 -> 优秀
# 英语: 79 -> 及格
# ---------- 2) 词频统计：dict.get 的经典用法 ----------
text = "hello world hello python world hello"
word_count = {}
for word in text.split():
 word_count[word] = word_count.get(word, 0) + 1
print(word_count) # {'hello': 3, 'world': 2, 'python': 1}

# ---------- 3) set 去重（顺序不保证，所以排序后打印） ----------
print(sorted(set(text.split()))) # ['hello', 'python', 'world']

# ---------- 4) 拆包：*rest 收集"剩下全部" ----------
first, *rest = [10, 20, 30, 40]
print(first, rest) # 10 [20, 30, 40]

# ---------- 5) 切片三件套 ----------
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4], nums[::2], nums[::-1])
# [1, 2, 3] [0, 2, 4] [5, 4, 3, 2, 1, 0]
# ---------- 6) 别名 vs 拷贝 ----------
a = [1, 2, 3]
b = a # 别名
b.append(4)
print("aliasing:", a) # aliasing: [1, 2, 3, 4]

c = a.copy # 浅拷贝
c.append(5)
print("copy:", a, c) # copy: [1, 2, 3, 4] [1, 2, 3, 4, 5]

# ---------- 7) 二维结构：两种写法，只有一种是对的 ----------
bad = [[0] * 3] * 3 # 三行其实是同一个列表对象
bad[0][0] = 1
print("bad matrix:", bad) # [[1, 0, 0], [1, 0, 0], [1, 0, 0]]

good = [[0] * 3 for _ in range(3)] # 每行独立
good[0][0] = 1
print("good matrix:", good) # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

# ---------- 8) tuple 作字典键：坐标映射 ----------
points = {(0, 0): "origin", (1, 2): "A"}
print(points[(1, 2)]) # A
```
**关键点说明**

| 行 | 关键点 | 为什么这么写 |
| --- | --- | --- |
| `scores.items()` | 返回 `(key, value)` 二元组视图 | 比 `for k in d: d[k]` 少一次哈希查找 |
| `word_count.get(word, 0) + 1` | 缺省值 0 | 避免 `KeyError`，一行完成"初始化 + 计数" |
| `sorted(set(...))` | set 无序 | 想稳定输出必须排序或转 list 后处理 |
| `first, *rest` | `*` 收集为 list | 注意收集结果是 list，不是 tuple |
| `b = a` | 别名，非拷贝 | 想独立就 `.copy` / `list(a)` / `a[:]` |
| `[[0]*3]*3` | 外层 `*` 复制的是引用 | 二维以上一律用嵌套推导式 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「基础语法与数据类型：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/01-基础与语法/01-基础语法与数据类型.md)
