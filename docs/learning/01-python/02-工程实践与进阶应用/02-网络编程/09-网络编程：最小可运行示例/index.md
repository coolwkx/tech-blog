---
article_id: kp-dac49d7567069e07
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a921e5aac5e4
learning_sourceId: a921e5aac5e4
learning_order: 8
learning_objective: 理解并验证：网络编程：最小可运行示例
---

# 网络编程：最小可运行示例

> **学习目标**：能够解释「网络编程：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与异常（02、04 篇）、`with` 与文件读写（04 篇）、多线程（08 篇，用于多客户端）。
>
> **所属主题**：网络编程 · 最小可运行示例

## 本次只学这一点

下面这段代码在**一个脚本**里同时跑服务端线程和客户端，可直接复制运行，覆盖最小 C/S、粘包现象、长度前缀协议、文件上传协议。

```python
import json
import os
import socket
import struct
import threading
import time

HOST = "127.0.0.1"

# ==================== A. 最小 C/S ====================
def server_once(port, results):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True) # 端口复用，必须在 bind 前
    srv.bind((HOST, port)) # 注意：一个元组参数
    srv.listen(5) # backlog
    conn, addr = srv.accept # 阻塞，返回交互套接字
    with conn:
        data = conn.recv(1024) # 最多 1024 字节
        results["recv"] = data.decode("utf-8")
        conn.sendall("服务端收到啦".encode("utf-8")) # sendall 保证发完
        srv.close()

        def demo_basic(port):
            results = {}
            threading.Thread(target=server_once, args=(port, results)).start()
            time.sleep(0.2)
            cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cli.connect((HOST, port))
            cli.sendall("你好，服务端".encode("utf-8"))
            print("客户端收到:", cli.recv(1024).decode("utf-8"))
            cli.close()
            time.sleep(0.2)
            print("服务端收到:", results["recv"])

            # ==================== B. 粘包现象 ====================
            def server_sticky(port, results):
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                srv.bind((HOST, port)); srv.listen(5)
                conn, _ = srv.accept
                with conn:
                    time.sleep(0.3) # 等两次 send 的数据都到达
                    results["raw"] = conn.recv(1024)
                    srv.close()

                    def demo_sticky(port):
                        results = {}
                        threading.Thread(target=server_sticky, args=(port, results)).start()
                        time.sleep(0.2)
                        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        cli.connect((HOST, port))
                        cli.sendall(b"AAA") # 两次独立的 send
                        cli.sendall(b"BBB")
                        time.sleep(0.6)
                        cli.close()
                        time.sleep(0.2)
                        print("一次 recv 收到:", results["raw"]) # b'AAABBB' —— 粘包了

                        # ==================== C. 长度前缀协议（解决粘包的正解） ====================
                        def send_msg(sock, payload: bytes):
                            sock.sendall(struct.pack("!I", len(payload)) + payload) # !I = 4 字节大端无符号整数

                            def recv_exact(sock, n):
                                buf = b""
                                while len(buf) < n: # recv 可能收不满，必须循环
                                    chunk = sock.recv(n - len(buf))
                                    if not chunk:
                                        return None # b'' 表示对端已关闭
                                    buf += chunk
                                    return buf

                                def recv_msg(sock):
                                    header = recv_exact(sock, 4)
                                    if header is None:
                                        return None
                                    (length,) = struct.unpack("!I", header)
                                    return recv_exact(sock, length)

                                def server_framed(port, results):
                                    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                                    srv.bind((HOST, port)); srv.listen(5)
                                    conn, _ = srv.accept
                                    got = []
                                    with conn:
                                        for _ in range(3):
                                            msg = recv_msg(conn)
                                            if msg is None:
                                                break
                                            got.append(msg.decode("utf-8"))
                                            results["msgs"] = got
                                            srv.close()

                                            def demo_framed(port):
                                                results = {}
                                                threading.Thread(target=server_framed, args=(port, results)).start()
                                                time.sleep(0.2)
                                                cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                cli.connect((HOST, port))
                                                for text in ["第一条", "第二条很长很长很长很长很长很长很长", "第三条"]:
                                                    send_msg(cli, text.encode("utf-8"))
                                                    cli.close()
                                                    time.sleep(0.3)
                                                    print("服务端完整收到:", results["msgs"])

                                                    # ==================== D. 文件上传：先发元信息，再发内容 ====================
                                                    def server_upload(port, save_dir, results):
                                                        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                                                        srv.bind((HOST, port)); srv.listen(5)
                                                        conn, _ = srv.accept
                                                        with conn:
                                                            meta = json.loads(recv_msg(conn).decode("utf-8")) # {"name": ..., "size": ...}
                                                            remaining = meta["size"] # 先知道该收多少字节
                                                            saved = os.path.join(save_dir, "uploaded_" + meta["name"])
                                                            with open(saved, "wb") as f: # 二进制写
                                                                while remaining > 0:
                                                                    chunk = conn.recv(min(1024, remaining))
                                                                    if not chunk:
                                                                        break
                                                                    f.write(chunk)
                                                                    remaining -= len(chunk)
                                                                    results["size"] = os.path.getsize(saved)
                                                                    conn.sendall(b"OK") # 回执
                                                                    srv.close()

                                                                    def demo_upload(port, save_dir):
                                                                        src = os.path.join(save_dir, "source.bin")
                                                                        with open(src, "wb") as f:
                                                                            f.write(os.urandom(3000)) # 造一个 3000 字节的文件

                                                                            results = {}
                                                                            threading.Thread(target=server_upload, args=(port, save_dir, results)).start()
                                                                            time.sleep(0.2)
                                                                            cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                                            cli.connect((HOST, port))
                                                                            size = os.path.getsize(src)
                                                                            send_msg(cli, json.dumps({"name": "source.bin", "size": size}).encode("utf-8"))
                                                                            with open(src, "rb") as f:
                                                                                while True:
                                                                                    chunk = f.read(1024)
                                                                                    if not chunk:
                                                                                        break
                                                                                    cli.sendall(chunk)
                                                                                    print("服务端回执:", cli.recv(1024).decode) # OK
                                                                                    cli.close()
                                                                                    time.sleep(0.3)
                                                                                    print(f"源 {size} 字节 -> 落盘 {results['size']} 字节")

                                                                                    # ==================== E. 长连接 + 下线检测 + 超时 ====================
                                                                                    def server_echo(port, results):
                                                                                        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                                                        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
                                                                                        srv.bind((HOST, port)); srv.listen(5)
                                                                                        conn, _ = srv.accept
                                                                                        conn.settimeout(2.0) # 避免永久阻塞
                                                                                        lines = []
                                                                                        with conn:
                                                                                            while True:
                                                                                                try:
                                                                                                    data = conn.recv(1024)
                                                                                                except socket.timeout:
                                                                                                    lines.append("<超时>"); break
                                                                                                    if not data: # b'' 表示客户端已 close
                                                                                                        lines.append("<客户端已下线>"); break
                                                                                                        text = data.decode("utf-8").strip()
                                                                                                        if text == "886":
                                                                                                            lines.append("<收到 886，主动结束>"); break
                                                                                                            conn.sendall(f"echo: {text}".encode("utf-8"))
                                                                                                            lines.append(text)
                                                                                                            results["lines"] = lines
                                                                                                            srv.close()

                                                                                                            if __name__ == "__main__":
                                                                                                                base = "./_tmp09"
                                                                                                                os.makedirs(base, exist_ok=True)
                                                                                                                demo_basic(20101)
                                                                                                                demo_sticky(20102)
                                                                                                                demo_framed(20103)
                                                                                                                demo_upload(20104, base)
```

本机实测输出：

```text
客户端收到: 服务端收到啦
服务端收到: 你好，服务端
一次 recv 收到: b'AAABBB'
服务端完整收到: ['第一条', '第二条很长很长很长很长很长很长很长', '第三条']
服务端回执: OK
源 3000 字节 -> 落盘 3000 字节
```

**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `setsockopt(SO_REUSEADDR)` | 必须在 `bind` **之前**，否则重启服务端会 `Address already in use` |
| `bind((HOST, port))` | 参数是**一个元组**；写成 `bind(HOST, port)` 直接 `TypeError` |
| `listen(5)` | 5 是等待队列长度，不是"最多允许 5 个客户端" |
| `accept` 返回 `(conn, addr)` | `conn` 是**新的**套接字，只服务这一个客户端 |
| 用 `with conn:` | 套接字支持上下文管理器，退出时自动 `close` |
| `sendall` 而非 `send` | `send` 可能只发出去一部分，必须自己循环 |
| `recv` 返回 `b''` | 对端已关闭，这是判断客户端下线的标准信号 |
| `struct.pack("!I", n)` | `!` 表示网络字节序（大端），`I` 是 4 字节无符号整数 |
| `recv_exact` 循环 | `recv` 可能只收到一部分，必须循环凑满期望长度 |
| 先发 `json` 元信息再发内容 | 服务端才知道"该收多少字节、存成什么文件名" |
| 文件用 `"wb"` / `"rb"` | 二进制模式，避免换行符转换与编码问题 |
| `settimeout(2.0)` | 生产代码必须设超时，否则一个卡住的客户端会永久占住服务线程 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/04-并发与网络/09-网络编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「网络编程：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/04-并发与网络/09-网络编程.md)
