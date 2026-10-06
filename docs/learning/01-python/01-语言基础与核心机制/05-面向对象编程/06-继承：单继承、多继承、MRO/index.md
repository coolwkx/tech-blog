---
article_id: kp-643ed1cddcbe5d32
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 5
learning_objective: 理解并验证：继承：单继承、多继承、MRO
---

# 继承：单继承、多继承、MRO

> **学习目标**：能够解释「继承：单继承、多继承、MRO」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 核心概念

## 本次只学这一点

```python
class Father(object): ... # Python 3 中 (object) 可省略，所有类默认继承 object
class Son(Father): ... # 单继承
class Son(Father, Mother): ... # 多继承
```
| 术语 | 含义 |
| --- | --- |
| 父类 / 基类 base class | 被继承的类 |
| 子类 / 派生类 derived class | 继承得到的类 |
| 重写 override | 子类定义了与父类同名的方法/属性 |
| 多层继承 | 类 → 子类 → 孙子类 的链条 |
| MRO | Method Resolution Order，方法解析顺序 |

**多继承时用哪个父类的同名方法？** 按 **MRO** 顺序，即"深度优先 + 从左到右"再经过 C3 线性化：
```python
class School: ...
class Master: ...
class Prentice(School, Master): ...

print(Prentice.__mro__)
# (<class 'Prentice'>, <class 'School'>, <class 'Master'>, <class 'object'>)
```
所以 `Prentice` 会优先用 `School` 的实现。**不要靠猜测，用 `类名.__mro__` 或 `类名.mro` 打印出来看。**

**调用父类方法的两条路：**

| 方式 | 写法 | 特点 |
| --- | --- | --- |
| 显式指父类 | `Father.__init__(self)` / `Father.make_cake(self)` | 直观，但硬编码父类名，改继承结构要一起改 |
| `super` | `super.__init__` | 沿 MRO 找**下一个**类，配合多继承/菱形继承才正确 |
```python
class Prentice(School):
    def __init__(self):
        self.kongfu = "[独创煎饼果子技术]"
        def make_old_cake(self):
            super.__init__ # 让父类初始化（会覆盖 self.kongfu）
            super.make_cake # 调用父类的同名方法
```
> 注意 `super.__init__` 可能**覆盖子类刚设好的属性** —— 上面的例子里 `self.kongfu` 最终会变成 `[煎饼果子配方]`。这是初学阶段一个真实存在的"结果与预期不符"的来源：先用 `super.__init__`，再设置子类自己的属性。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「继承：单继承、多继承、MRO」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
