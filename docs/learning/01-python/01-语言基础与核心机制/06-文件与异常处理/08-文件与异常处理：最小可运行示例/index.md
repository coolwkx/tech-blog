---
article_id: kp-818d7e1e9704322a
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-89378b25b6ef
learning_sourceId: 89378b25b6ef
learning_order: 7
learning_objective: 理解并验证：文件与异常处理：最小可运行示例
---

# 文件与异常处理：最小可运行示例

> **学习目标**：能够解释「文件与异常处理：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与作用域（02 篇）、可变/不可变类型（01 篇）、类与魔法方法 `__enter__` / `__exit__`（03 篇）。
>
> **所属主题**：文件与异常处理 · 最小可运行示例

## 本次只学这一点

```text
import os
import shutil

base = "demo_files"
shutil.rmtree(base, ignore_errors=True) # 清理上次运行残留
os.makedirs(base, exist_ok=True)
path = os.path.join(base, "demo.txt")

# ---------- 1) 写：w 会清空，a 是追加，都要显式编码 ----------
with open(path, "w", encoding="utf-8") as f:
 f.write("第一行\n")
 f.writelines(["第二行\n", "第三行\n", "第四行\n"])

# ---------- 2) 读：三种方式与它们的内存代价 ----------
with open(path, "r", encoding="utf-8") as f:
 print("read 全文长度:", len(f.read)) # 16（含 4 个换行符）

with open(path, "r", encoding="utf-8") as f:
 print("readline:", repr(f.readline())) # '第一行\n'
 print("readlines:", f.readlines()) # ['第二行\n', '第三行\n', '第四行\n']

print("逐行遍历（大文件首选）:")
with open(path, "r", encoding="utf-8") as f:
 for line in f:
 print("", line.rstrip("\n"))

# ---------- 3) 指针：读完想再读必须 seek(0) ----------
with open(path, "r", encoding="utf-8") as f:
 print("起始 tell:", f.tell) # 0
 f.read
 print("读完后 readline:", repr(f.readline())) # '' ← 已在末尾
 f.seek(0)
 print("seek(0) 后:", repr(f.readline())) # '第一行\n'

# ---------- 4) 'w' 截断 vs 'a' 追加 ----------
with open(path, "w", encoding="utf-8") as f:
 f.write("只剩这一行\n")
print("w 之后大小:", os.path.getsize(path)) # 17 字节（utf-8 中文 3 字节）

with open(path, "a", encoding="utf-8") as f:
 f.write("追加一行\n")

# ---------- 5) 异常四件套：else 只在正常完成时执行 ----------
def safe_div(x):
 try:
 result = 10 / x
 except ZeroDivisionError as e:
 print(" except:", e)
 result = None
 else:
 print(" else: 计算成功")
 finally:
 print(" finally: 无论成败都执行（放清理代码）")
 return result

print("safe_div(2) ->", safe_div(2))
print("safe_div(0) ->", safe_div(0))

# ---------- 6) 自定义异常 + 异常链 ----------
class ParseError(Exception):
 """自定义业务异常"""

def to_int(text):
 try:
 return int(text)
 except ValueError as e:
 raise ParseError(f"无法把 {text!r} 转成整数") from e # 保留原始异常

try:
 to_int("abc")
except ParseError as e:
 print("捕获:", e, "| 原始原因:", type(e.__cause__).__name__)
 # 捕获: 无法把 'abc' 转成整数 | 原始原因: ValueError

# ---------- 7) 上下文管理器：自定义 + 异常穿透 ----------
class ManagedFile:
 def __init__(self, name, mode):
 self.name, self.mode, self.fp = name, mode, None

 def __enter__(self):
 self.fp = open(self.name, self.mode, encoding="utf-8")
 return self.fp

 def __exit__(self, exc_type, exc_val, exc_tb):
 self.fp.close()
 print(" __exit__ 收到异常类型:", exc_type) # 正常时为 None
 return False # 不吞异常

with ManagedFile(path, "r") as fp:
 print("首行:", fp.readline.strip())

try:
 with ManagedFile(path, "r") as fp:
 raise RuntimeError("业务出错")
except RuntimeError as e:
 print("异常正常向外传播:", e)

# ---------- 8) 备份：shutil 一行 vs 手动读写 ----------
shutil.copy2(path, os.path.join(base, "demo.bak"))
print("备份文件存在:", os.path.exists(os.path.join(base, "demo.bak")))

shutil.rmtree(base)
```
真实运行输出（节选）：
```text
read 全文长度: 16
readline: '第一行\n'
readlines: ['第二行\n', '第三行\n', '第四行\n']
起始 tell: 0
读完后 readline: ''
seek(0) 后: '第一行\n'
w 之后大小: 17
 except: division by zero
 finally: 无论成败都执行（放清理代码）
safe_div(0) -> None
 else: 计算成功
 finally: 无论成败都执行（放清理代码）
safe_div(2) -> 5.0
捕获: 无法把 'abc' 转成整数 | 原始原因: ValueError
首行: 只剩这一行
 __exit__ 收到异常类型: None
 __exit__ 收到异常类型: <class 'RuntimeError'>
异常正常向外传播: 业务出错
```
**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `encoding="utf-8"` | 不写就跟随平台默认编码，Windows 上是 GBK，跨平台必乱码 |
| `read` 后 `readline` 返回 `''` | 指针已在末尾，必须 `seek(0)` |
| `os.path.getsize` 为 17 | utf-8 下中文占 3 字节，"只剩这一行\n" = 5×3 + 1 + 1 = 17 |
| `else` 分支 | 只在 `try` 正常完成时执行，用来把"成功后的动作"和"可能出错的代码"分开 |
| `finally` | 资源清理的最终防线；不要在里面 `return` |
| `raise ... from e` | 保留 `__cause__`，报错信息里能看到"原始原因"，方便排查 |
| `__exit__` 返回 `False` | 异常继续向外传播；返回 `True` 会静默吞掉异常 |
| `shutil.copy2` | 复制内容 + 元数据（时间戳），比手动 `read`/`write` 更可靠 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/04-文件与异常处理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「文件与异常处理：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/04-文件与异常处理.md)
