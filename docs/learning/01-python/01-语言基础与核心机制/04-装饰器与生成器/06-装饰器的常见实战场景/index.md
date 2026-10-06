---
article_id: kp-16119ebc41fe5bfa
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-2e1a353ffbef
learning_sourceId: 2e1a353ffbef
learning_order: 5
learning_objective: 理解并验证：装饰器的常见实战场景
---

# 装饰器的常见实战场景

> **学习目标**：能够解释「装饰器的常见实战场景」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数是一等对象、高阶函数、LEGB 与 `nonlocal`（02 篇）、可变默认参数陷阱（02 篇）、类与 `@property` 的宿主类（03 篇）。
>
> **所属主题**：装饰器与生成器 · 核心概念

## 本次只学这一点

| 场景 | 关键点 | 标准库支持 |
| --- | --- | --- |
| 计时/性能统计 | `perf_counter`、`functools.wraps` | — |
| 日志记录 | 记录入参、返回值、耗时 | `logging` |
| 结果缓存 | 用参数字典做 memo | `functools.lru_cache` / `cache` |
| 权限校验 | 校验失败抛异常 / 返回错误 | — |
| 参数校验 | 检查类型、范围 | `pydantic` |
| 失败重试 | 捕获指定异常并重试，注意加退避 | `tenacity` |
| 注册路由 | 装饰器把函数登记到全局表 | Flask / FastAPI / pytest fixture |

缓存装饰器实测：
```python
calls = {"n": 0}

@functools.lru_cache(maxsize=None)
def fib(n):
 calls["n"] += 1
 return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(30), calls["n"]) # 832040 31
```
不做缓存时 `fib(30)` 需要约 270 万次调用，加了缓存只要 **31 次**，差距是指数级。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「装饰器的常见实战场景」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/02-函数与装饰器/06-装饰器与生成器.md)
