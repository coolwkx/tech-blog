---
article_id: kp-521e5574cfdaecea
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 7
learning_objective: 理解并验证：多态：同一接口，不同实现
---

# 多态：同一接口，不同实现

> **学习目标**：能够解释「多态：同一接口，不同实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 核心概念

## 本次只学这一点

多态的成立条件（的三条）：

1. 有继承（定义父类与子类）；
2. 有方法重写（子类重写父类方法）；
3. 父类引用指向子类对象（把子类实例传给以父类为"接口"的调用者）。
```python
def object_play(hero, enemy): # 平台/框架：只依赖 power 与 attack 两个约定
    if hero.power > enemy.attack:
        print("英雄战机胜利,敌机失败")
    else:
        print("英雄战机失败,敌机胜利")

        object_play(HeroFighter, EnemyFighter) # 一代战机：失败
        object_play(AdvHeroFighter, EnemyFighter) # 二代战机：胜利
```
**多态的价值**：`object_play` 一行都不用改，就能接纳未来任何人写的"英雄战机"。这就是"**对扩展开放、对修改关闭**"，也是反复强调的"解耦合"。

**抽象类（接口）**：父类里把方法体写成 `pass`，只规定"必须有什么方法"，由子类实现。工业级写法用 `abc` 模块强制约束：
```python
from abc import ABC, abstractmethod

class Hero(ABC):
    @abstractmethod
    def power(self): ...

    # Hero # TypeError: 抽象类不能实例化
    class AdvHero(Hero):
        def power(self):
            return 80
```
用 `abc` 的好处：**忘记实现抽象方法的子类在实例化时就直接报错**，而不是等到运行时才炸。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多态：同一接口，不同实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
