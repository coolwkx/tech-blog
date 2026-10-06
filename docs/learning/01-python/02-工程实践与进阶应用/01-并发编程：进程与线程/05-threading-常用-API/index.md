---
article_id: kp-e9d12b912993713f
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-45ae177d7738
learning_sourceId: 45ae177d7738
learning_order: 4
learning_objective: 理解并验证：threading 常用 API
---

# threading 常用 API

> **学习目标**：能够解释「threading 常用 API」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数（02 篇）、`if __name__ == "__main__"` 与模块（05 篇）、竞态与锁的直觉（`try/finally`，04 篇）。
>
> **所属主题**：并发编程：进程与线程 · 核心概念

## 本次只学这一点

| 项 | 用法 | 说明 |
| --- | --- | --- |
| 创建线程 | `threading.Thread(target=fn, args=, kwargs={}, name=..., daemon=...)` | 同样传函数名 |
| 启动 / 等待 | `t.start()` / `t.join()` | `join` 阻塞到该线程结束 |
| 守护线程 | `daemon=True` 或 `t.setDaemon(True)`（3.10 起弃用） | 主线程退出即被终止 |
| 当前线程 | `threading.current_thread` | 名字、`ident` |
| 活跃线程数 | `threading.active_count` / `threading.enumerate` | 调试用 |
| 互斥锁 | `threading.Lock` | `with lock:` 或 `acquire` / `release` |
| 可重入锁 | `threading.RLock` | 同一线程可多次获取 |
| 条件变量 | `threading.Condition` | 生产者-消费者 |
| 信号量 | `threading.Semaphore(n)` | 限制并发数 |
| 线程池 | `concurrent.futures.ThreadPoolExecutor(n)` | **生产环境首选**，返回 `Future` |

> 现实建议：手写 `Thread` + `join` 只适合教学和简单的"起几个后台任务"。真正的并发任务编排用 `concurrent.futures` 的 `ThreadPoolExecutor` / `ProcessPoolExecutor`（`ex.map` / `ex.submit` + `as_completed`），异常处理和超时都更规范。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「threading 常用 API」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)
