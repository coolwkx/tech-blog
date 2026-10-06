---
article_id: kp-58955c66480a9090
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-45ae177d7738
learning_sourceId: 45ae177d7738
learning_order: 9
learning_objective: 理解并验证：进程间通信（IPC）
---

# 进程间通信（IPC）

> **学习目标**：能够解释「进程间通信（IPC）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数（02 篇）、`if __name__ == "__main__"` 与模块（05 篇）、竞态与锁的直觉（`try/finally`，04 篇）。
>
> **所属主题**：并发编程：进程与线程 · 最小可运行示例

## 本次只学这一点

进程之间不共享内存，所以要把数据传回去必须用 `Queue` 等机制：

```python
import multiprocessing as mp

def producer(queue):
    for i in range(3):
        queue.put(i)
        queue.put(None) # 哨兵值表示"生产结束"

        def consumer(queue):
            while True:
                item = queue.get
                if item is None:
                    break
                print("消费:", item)

                if __name__ == "__main__":
                    q = mp.Queue
                    p1 = mp.Process(target=producer, args=(q,))
                    p2 = mp.Process(target=consumer, args=(q,))
                    p1.start(); p2.start()
                    p1.join(); p2.join()
```

| 机制 | 特点 | 适用 |
| --- | --- | --- |
| `Queue` | 进程安全、可传任意可 pickle 对象、内部自带锁 | 生产者-消费者，最常用 |
| `Pipe` | 更轻量，两端 `send` / `recv` | 只有两个进程通信 |
| `Value` / `Array` | 共享内存，快但要自己加锁 | 共享计数器、大数组 |
| `Manager.dict/list` | 代理对象实现"像共享变量"，方便但慢 | 结构复杂、性能不敏感 |

> `Queue` 里的元素必须能被 `pickle` 序列化，所以 lambda、打开的文件对象、socket 都传不过去。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「进程间通信（IPC）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/08-并发编程-进程与线程.md)
