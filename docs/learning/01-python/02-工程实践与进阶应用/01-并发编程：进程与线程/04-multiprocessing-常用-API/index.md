---
article_id: kp-ce32fa8d6d31fba8
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-45ae177d7738
learning_sourceId: 45ae177d7738
learning_order: 3
learning_objective: 理解并验证：multiprocessing 常用 API
---

# multiprocessing 常用 API

> **学习目标**：能够解释「multiprocessing 常用 API」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数（02 篇）、`if __name__ == "__main__"` 与模块（05 篇）、竞态与锁的直觉（`try/finally`，04 篇）。
>
> **所属主题**：并发编程：进程与线程 · 核心概念

## 本次只学这一点

| 项 | 用法 | 说明 |
| --- | --- | --- |
| 创建进程 | `mp.Process(target=fn, name=..., args=, kwargs={})` | `target` 是函数对象（不加括号） |
| 启动 | `p.start()` | 真正 fork/spawn 出子进程 |
| 等待结束 | `p.join(timeout=None)` | 阻塞当前进程直到子进程结束 |
| 是否存活 | `p.is_alive` | 返回布尔 |
| 后台进程 | `p.daemon = True`（必须在 `start` 前设置） | 主进程退出时子进程被强制终止 |
| 强制结束 | `p.terminate` | **不推荐**：可能留下僵尸进程、不清理资源 |
| 当前进程 | `mp.current_process` / `os.getpid` | 取 `pid` 用于日志与调试 |
| 父进程号 | `os.getppid` | 验证"子进程由谁创建" |
| 进程池 | `mp.Pool(n)` / `ProcessPoolExecutor(n)` | 复用进程，避免频繁创建开销 |
| 队列 | `mp.Queue` | 进程安全，可跨进程传对象（需可 pickle） |
| 管道 | `mp.Pipe` | 双向/单向，比 Queue 轻量 |
| 共享状态 | `mp.Value` / `mp.Array` / `mp.Manager` | 需要加锁保护 |

**必须记住的一条**：`target=` 传的是**函数名，不加括号**。写 `target=worker` 会立刻在主进程里执行 `worker` 并把返回值（通常是 `None`）传给 `Process`，然后报 `TypeError: 'NoneType' object is not callable`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「multiprocessing 常用 API」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)
