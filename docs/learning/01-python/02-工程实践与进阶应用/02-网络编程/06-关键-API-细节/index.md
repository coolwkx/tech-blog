---
article_id: kp-d5674ceaab4d9aca
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a921e5aac5e4
learning_sourceId: a921e5aac5e4
learning_order: 5
learning_objective: 理解并验证：关键 API 细节
---

# 关键 API 细节

> **学习目标**：能够解释「关键 API 细节」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与异常（02、04 篇）、`with` 与文件读写（04 篇）、多线程（08 篇，用于多客户端）。
>
> **所属主题**：网络编程 · 核心概念

## 本次只学这一点

| API | 语义与坑 |
| --- | --- |
| `recv(bufsize)` | 返回**至多** bufsize 字节，**不保证一次收完一条消息**；返回 `b''` 表示对端已关闭连接（这是判断下线的标准方式） |
| `send(data)` | 返回实际发送的字节数，**可能小于 len(data)**（发送缓冲区满），不保证发完 |
| `sendall(data)` | 循环发送直到全部发完，**推荐用这个** |
| `accept` | 返回 `(conn, addr)`，`addr` 是 `(ip, port)` 元组 |
| `settimeout(t)` | 设置阻塞超时，超时抛 `socket.timeout`（3.10+ 是 `TimeoutError` 的子类） |
| `SO_REUSEADDR` | 允许重用处于 `TIME_WAIT` 的地址，服务端调试必备 |
| `shutdown(SHUT_WR)` | 半关闭：只关闭写方向，仍可读（优雅结束"我发完了"） |
| `socket.timeout` | 超时异常；生产代码应该总是设置超时，避免永久阻塞 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/09-网络编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键 API 细节」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/09-网络编程.md)
