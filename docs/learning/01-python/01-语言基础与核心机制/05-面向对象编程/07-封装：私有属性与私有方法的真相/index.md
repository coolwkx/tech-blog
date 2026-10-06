---
article_id: kp-ca3a58c460816cd7
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 6
learning_objective: 理解并验证：封装：私有属性与私有方法的真相
---

# 封装：私有属性与私有方法的真相

> **学习目标**：能够解释「封装：私有属性与私有方法的真相」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 核心概念

## 本次只学这一点

Python **没有真正的私有**，只有两个约定：

| 写法 | 名称 | 外部能访问吗 | 机制 |
| --- | --- | --- | --- |
| `name` | 公有 | ✅ | 普通属性 |
| `_name` | 单下划线"受保护" | ✅（但约定别碰） | 仅约定，提示"内部使用" |
| `__name` | 双下划线 | ⚠️ 不能按原名访问 | **名称改写**为 `_类名__name` |
| `__name__` | 双下划线且结尾也双 | ✅ | 系统保留名，不要自造 |
```python
class Wallet:
    def __init__(self, money):
        self.__money = money # 实际存成 _Wallet__money
        def get_money(self):
            return self.__money

        w = Wallet(100)
        print(w.get_money) # 100
        # print(w.__money) # AttributeError
        print(w._Wallet__money) # 100 ← "私有"只是改了名字，并非访问不到
```
名称改写的**真正目的**不是安全，而是防止子类意外覆盖父类的内部属性。子类里写 `self.__money = x` 会变成 `_子类名__money`，与父类的 `_父类名__money` 是两个不同的属性，互不干扰。

标准的读写接口是 `get_xx` / `set_xx`，Pythonic 的写法是 `@property`（见 06 篇）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「封装：私有属性与私有方法的真相」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
