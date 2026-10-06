---
article_id: kp-4a7fc3f617e61c18
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a921e5aac5e4
learning_sourceId: a921e5aac5e4
learning_order: 6
learning_objective: 理解并验证：粘包：TCP 是字节流，没有"消息边界"
---

# 粘包：TCP 是字节流，没有"消息边界"

> **学习目标**：能够解释「粘包：TCP 是字节流，没有"消息边界"」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与异常（02、04 篇）、`with` 与文件读写（04 篇）、多线程（08 篇，用于多客户端）。
>
> **所属主题**：网络编程 · 核心概念

## 本次只学这一点

`send` 一次不代表 `recv` 一次。实测：
```text
客户端: cli.sendall(b"AAA"); cli.sendall(b"BBB")
服务端: recv(1024) -> b'AAABBB' ← 两条消息被合并
```
原因：TCP 只保证**字节顺序**，不保留应用层的消息边界。合并（粘包）与拆分（拆包）都可能发生，取决于发送缓冲区、Nagle 算法、MTU、接收窗口。

**三种解决方案**：

| 方案 | 做法 | 优缺点 |
| --- | --- | --- |
| 固定长度 | 每条消息定长，不足补齐 | 简单；浪费带宽，不适合变长文本 |
| 分隔符 | 用 `\n` 或自定义分隔符切分 | 简单；消息内容不能含分隔符，需要转义 |
| **长度前缀** | 先发 4 字节长度，再发正文 | **推荐**：通用、无歧义，二进制也适用 |

长度前缀实现（本机实测可正确拆分三条变长消息）：
```python
import struct

def send_msg(sock, payload: bytes):
    sock.sendall(struct.pack("!I", len(payload)) + payload) # !I = 4 字节大端无符号整数

    def recv_exact(sock, n):
        buf = b""
        while len(buf) < n: # recv 可能收不满，必须循环
            chunk = sock.recv(n - len(buf))
            if not chunk:
                return None # 对端关闭
            buf += chunk
            return buf

        def recv_msg(sock):
            header = recv_exact(sock, 4)
            if header is None:
                return None
            (length,) = struct.unpack("!I", header)
            return recv_exact(sock, length)
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/09-网络编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「粘包：TCP 是字节流，没有"消息边界"」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/09-网络编程.md)
