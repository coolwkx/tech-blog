---
article_id: kp-8ab3c10160358fb7
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-25d313dff349
learning_sourceId: 25d313dff349
learning_order: 7
learning_objective: 理解并验证：迭代器与内置函数：最小可运行示例
---

# 迭代器与内置函数：最小可运行示例

> **学习目标**：能够解释「迭代器与内置函数：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：序列与字典（01 篇）、函数作为参数与 lambda（02 篇）、`yield` 生成器（06 篇）。
>
> **所属主题**：迭代器与内置函数 · 最小可运行示例

## 本次只学这一点

```python
from functools import reduce
from operator import itemgetter

# ---------- 1) 手动复现 for 循环 ----------
data = [10, 20, 30]
it = iter(data) # ① 取迭代器
while True:
    try:
        print(" next:", next(it)) # ② 反复取
    except StopIteration: # ③ 靠异常判断结束
        print(" 循环结束")
        break

    # ---------- 2) 自定义可迭代对象：每次遍历都产生新迭代器 ----------
    class Sentence:
        """可迭代对象：__iter__ 返回一个全新的迭代器对象"""

        def __init__(self, text):
            self.words = text.split()

            def __iter__(self):
                return SentenceIterator(self.words)

            class SentenceIterator:
                """迭代器：自己维护游标，耗尽即停"""

                def __init__(self, words):
                    self.words = words
                    self.index = 0

                    def __iter__(self):
                        return self # 迭代器的 __iter__ 返回 self

                    def __next__(self):
                        if self.index >= len(self.words):
                            raise StopIteration # 结束信号
                        word = self.words[self.index]
                        self.index += 1
                        return word

                    s = Sentence("hello python world")
                    print("第一次:", list(s)) # ['hello', 'python', 'world']
                    print("第二次:", list(s)) # 仍然完整 → 可重复遍历

                    # ---------- 3) 自定义迭代器：一次性 ----------
                    class OnceRange:
                        """__iter__ 直接返回 self，所以只能遍历一次"""

                        def __init__(self, n):
                            self.n = n
                            self._cur = 0

                            def __iter__(self):
                                return self

                            def __next__(self):
                                if self._cur >= self.n:
                                    raise StopIteration
                                self._cur += 1
                                return self._cur

                            o = OnceRange(3)
                            print("第一次:", list(o), "第二次:", list(o)) # [1, 2, 3] []

                            # ---------- 4) 反向迭代：__reversed__ ----------
                            class Countdown:
                                def __init__(self, n):
                                    self.n = n

                                    def __iter__(self):
                                        for i in range(self.n): # 用 yield 写，自动可重复遍历
                                            yield i

                                            def __reversed__(self):
                                                for i in range(self.n - 1, -1, -1):
                                                    yield i

                                                    print("正向:", list(Countdown(4)), "反向:", list(reversed(Countdown(4))))
                                                    # 正向: [0, 1, 2, 3] 反向: [3, 2, 1, 0]
                                                    # ---------- 5) 常用内置函数 ----------
                                                    nums = [3, 1, 4, 1, 5]
                                                    print("enumerate:", list(enumerate("abc", start=1))) # [(1,'a'),(2,'b'),(3,'c')]
                                                    print("zip 最短截断:", list(zip([1, 2], "abcd"))) # [(1,'a'),(2,'b')]
                                                    print("zip → dict:", dict(zip(["a", "b"], [1, 2]))) # {'a': 1, 'b': 2}
                                                    print("map:", list(map(lambda x: x * 2, nums))) # [6,2,8,2,10]
                                                    print("filter:", list(filter(lambda x: x > 2, nums))) # [3,4,5]
                                                    print("reduce:", reduce(lambda a, b: a + b, nums, 0)) # 14
                                                    print("sorted:", sorted(nums), "| reverse:", sorted(nums, reverse=True))
                                                    print("any/all:", any(x > 4 for x in nums), all(nums)) # True True
                                                    print("divmod:", divmod(17, 5)) # (3, 2)
                                                    print("round:", round(2.567, 2)) # 2.57

                                                    # ---------- 6) key 参数：从单级到多级排序 ----------
                                                    students = [
                                                    {"name": "酒窝", "score": 90, "age": 21},
                                                    {"name": "刘浩存", "score": 90, "age": 22},
                                                    {"name": "王月半", "score": 10, "age": 20},
                                                    ]

                                                    print("按分数升序:", [s["name"] for s in sorted(students, key=lambda s: s["score"])])
                                                    print("用 itemgetter:", [s["name"] for s in sorted(students, key=itemgetter("score"))])
                                                    print("多级(分数降序, 年龄升序):",
                                                    [s["name"] for s in sorted(students, key=lambda s: (-s["score"], s["age"]))])
                                                    print("按绝对值:", sorted([-3, 1, -2], key=abs)) # [1, -2, -3]
                                                    print("按长度:", sorted(["bb", "a", "ccc"], key=len)) # ['a', 'bb', 'ccc']

                                                    # ---------- 7) 推导式 vs map/filter ----------
                                                    print("列表推导:", [x * 2 for x in nums if x > 2]) # [6, 8, 10]
                                                    print("map+filter:", list(map(lambda x: x * 2, filter(lambda x: x > 2, nums))))
                                                    print("字典推导:", {k: v for k, v in zip("abc", [1, 2, 3])})
                                                    print("生成器表达式类型:", type(x for x in range(3)).__name__) # generator

                                                    # ---------- 8) 迭代器耗尽 ----------
                                                    gen = (x for x in range(3))
                                                    print("sum 第一次:", sum(gen), "第二次:", sum(gen)) # 3 0

                                                    # ---------- 9) 经典案例：按批次产出数据（dataloader 的前身） ----------
                                                    import math

                                                    def dataset_loader(total, batch_size):
                                                        """把 0..total-1 按 batch_size 分批产出，最后一批允许不足"""
                                                        batch_count = math.ceil(total / batch_size) # 向上取整，不足一批也算一批
                                                        for batch_id in range(batch_count):
                                                            start = batch_id * batch_size
                                                            yield list(range(start, min(start + batch_size, total)))

                                                            print("分 3 批:", list(dataset_loader(8, 3)))
                                                            # [[0,1,2], [3,4,5], [6,7]]
```
真实运行输出（节选）：
```text
 next: 10
 next: 20
 next: 30
 循环结束
第一次: ['hello', 'python', 'world']
第二次: ['hello', 'python', 'world']
第一次: [1, 2, 3] 第二次: []
正向: [0, 1, 2, 3] 反向: [3, 2, 1, 0]
enumerate: [(1, 'a'), (2, 'b'), (3, 'c')]
zip 最短截断: [(1, 'a'), (2, 'b')]
zip → dict: {'a': 1, 'b': 2}
map: [6, 2, 8, 2, 10]
filter: [3, 4, 5]
reduce: 14
sorted: [1, 1, 3, 4, 5] | reverse: [5, 4, 3, 1, 1]
any/all: True True
divmod: (3, 2)
round: 2.57
按分数升序: ['王月半', '酒窝', '刘浩存']
多级(分数降序, 年龄升序): ['酒窝', '刘浩存', '王月半']
按绝对值: [1, -2, -3]
按长度: ['a', 'bb', 'ccc']
列表推导: [6, 8, 10]
生成器表达式类型: generator
sum 第一次: 3 第二次: 0
分 3 批: [[0, 1, 2], [3, 4, 5], [6, 7]]
```
**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `iter(data)` | 列表本身不是迭代器，必须先取迭代器才能 `next` |
| `except StopIteration` | 迭代结束的**唯一**信号，不是返回 `None` |
| `Sentence.__iter__` | 每次都 `return SentenceIterator(...)`，所以可重复遍历 |
| `OnceRange.__iter__` | 返回 `self`，游标存在对象里 → 只能遍历一次 |
| `Countdown.__iter__` 用 `yield` | 用生成器方法实现 `__iter__`，天然可重复遍历，代码最短 |
| `zip` 按最短截断 | 长度不等时"多出来的直接丢弃"，容易静默丢数据 |
| `key=lambda s: (-s["score"], s["age"])` | 元组依次比较，负号实现"数值降序" |
| `sum(gen)` 两次结果 3 和 0 | 生成器是迭代器，被消费后耗尽 |
| `math.ceil(total / batch_size)` | 分批必须向上取整，否则最后一批会被丢掉 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「迭代器与内置函数：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/07-迭代器与内置函数.md)
