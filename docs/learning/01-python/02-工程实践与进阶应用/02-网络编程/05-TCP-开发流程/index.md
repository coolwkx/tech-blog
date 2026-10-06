---
article_id: kp-34a10b4f19ef7a97
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a921e5aac5e4
learning_sourceId: a921e5aac5e4
learning_order: 4
learning_objective: 理解并验证：TCP 开发流程
---

# TCP 开发流程

> **学习目标**：能够解释「TCP 开发流程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与异常（02、04 篇）、`with` 与文件读写（04 篇）、多线程（08 篇，用于多客户端）。
>
> **所属主题**：网络编程 · 核心概念

## 本次只学这一点

**服务端（固定 7 步）**：

| 步骤 | 代码 | 关键点 |
| --- | --- | --- |
| 1 创建套接字 | `srv = socket.socket(AF_INET, SOCK_STREAM)` | `AF_INET`=IPv4，`SOCK_STREAM`=TCP |
| 2 端口复用 | `srv.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)` | **必须在 bind 之前**，解决"Address already in use" |
| 3 绑定 | `srv.bind(("0.0.0.0", 8888))` | 参数是**一个元组**，不是两个参数 |
| 4 监听 | `srv.listen(128)` | 128 是等待队列长度（backlog），不是最大连接数 |
| 5 接受连接 | `conn, addr = srv.accept` | **阻塞**；返回一个**新套接字** `conn` 专门跟这个客户端通信 |
| 6 收发 | `conn.recv(1024)` / `conn.sendall(b"...")` | `recv` 阻塞，返回 `bytes` |
| 7 关闭 | `conn.close()`；`srv` 服务端一般不主动关 | 只关交互套接字 |

**客户端（固定 5 步）**：

| 步骤 | 代码 |
| --- | --- |
| 1 创建套接字 | `cli = socket.socket(AF_INET, SOCK_STREAM)` |
| 2 连接 | `cli.connect(("127.0.0.1", 8888))` |
| 3 发送 | `cli.sendall("你好".encode("utf-8"))` |
| 4 接收 | `data = cli.recv(1024)` |
| 5 关闭 | `cli.close()` |

**"被动套接字"与"交互套接字"的区别**（强调的重点）：

- `srv`（`accept` 之前的套接字）只负责**接收新连接**，不能收发业务消息；
- `conn`（`accept` 返回的套接字）才是**跟某个具体客户端**通信的通道；
- 关掉 `conn` 表示"和这个客户端聊完了"，关掉 `srv` 表示"整个服务不再接受新连接"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/09-网络编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「TCP 开发流程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/09-网络编程.md)
