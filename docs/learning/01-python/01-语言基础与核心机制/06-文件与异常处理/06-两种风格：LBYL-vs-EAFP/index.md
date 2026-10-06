---
article_id: kp-c1242026f980a7fb
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-89378b25b6ef
learning_sourceId: 89378b25b6ef
learning_order: 5
learning_objective: 理解并验证：两种风格：LBYL vs EAFP
---

# 两种风格：LBYL vs EAFP

> **学习目标**：能够解释「两种风格：LBYL vs EAFP」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与作用域（02 篇）、可变/不可变类型（01 篇）、类与魔法方法 `__enter__` / `__exit__`（03 篇）。
>
> **所属主题**：文件与异常处理 · 核心概念

## 本次只学这一点

| 风格 | 全称 | 写法 | 适用 |
| --- | --- | --- | --- |
| LBYL | Look Before You Leap | `if os.path.exists(p): ...` | 检查便宜、失败常见 |
| EAFP | Easier to Ask Forgiveness than Permission | `try: ... except FileNotFoundError: ...` | **Python 推荐**：省一次系统调用，且天然避免检查与使用之间的竞态 |
```python
# LBYL：两次访问文件系统，且两次之间文件可能被删掉
if os.path.exists(path):
 with open(path) as f: ...

# EAFP：一次访问，异常即答案
try:
 with open(path) as f: ...
except FileNotFoundError:
 ...
```
**但要遵守一条铁律**：`try` 块只包"你确定会抛这种异常"的最小代码范围。把 20 行代码一股脑塞进 `try`，会导致真正的 bug 被 `except` 误吞。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/04-文件与异常处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「两种风格：LBYL vs EAFP」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/04-文件与异常处理.md)
