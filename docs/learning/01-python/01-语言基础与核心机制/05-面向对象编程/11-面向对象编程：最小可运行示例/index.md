---
article_id: kp-a8c6b1edefba3fdd
learning_kind: article
learning_category: 01-python
learning_direction: foundations
learning_topic: topic-71dac73742c8
learning_sourceId: 71dac73742c8
learning_order: 10
learning_objective: 理解并验证：面向对象编程：最小可运行示例
---

# 面向对象编程：最小可运行示例

> **学习目标**：能够解释「面向对象编程：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与参数传递（02 篇）、可变 vs 不可变类型与对象身份 `id`（01 篇）、元组拆包。
>
> **所属主题**：面向对象编程 · 最小可运行示例

## 本次只学这一点

一段综合了继承、多态、类属性、`__str__`、深浅拷贝的完整示例：
```python
import copy
from abc import ABC, abstractmethod

# ---------- 1) 抽象基类：定义"接口标准" ----------
class Fighter(ABC):
    """所有战机的抽象父类，只规定'必须能报出战斗力'"""

    total = 0 # 类属性：所有子类共享

    def __init__(self, name, power):
        self.name = name # 实例属性
        self.__power = power # 私有属性，外部读不到原名
        Fighter.total += 1

        # 供子类/外部读取私有属性的公共接口
        def power(self):
            return self.__power

        @abstractmethod
        def attack(self):
            """子类必须实现"""

            def __str__(self):
                return f"{self.name}(战斗力={self.power})"

            # ---------- 2) 子类继承 + 重写 ----------
            class HeroFighter(Fighter):
                def attack(self):
                    return self.power

                class AdvHeroFighter(HeroFighter):
                    def attack(self):
                        return self.power * 2 # 重写：二代机攻击翻倍

                    class EnemyFighter(Fighter):
                        def attack(self):
                            return self.power

                        # ---------- 3) 多态：平台代码只依赖抽象接口 ----------
                        def object_play(hero: Fighter, enemy: Fighter):
                            print(f"{hero} VS {enemy} -> ", end="")
                            if hero.attack > enemy.attack:
                                print("英雄胜")
                            else:
                                print("英雄败")

                                if __name__ == "__main__":
                                    enemy = EnemyFighter("敌机", 70)
                                    object_play(HeroFighter("一代机", 60), enemy) # 英雄败
                                    object_play(AdvHeroFighter("二代机", 80), enemy) # 英雄胜

                                    print("战机总数:", Fighter.total) # 3
                                    print("MRO:", [c.__name__ for c in AdvHeroFighter.__mro__])
                                    # ['AdvHeroFighter', 'HeroFighter', 'Fighter', 'ABC', 'object']

                                    # ---------- 4) 深浅拷贝 ----------
                                    squad = [["一代机"], ["二代机"]]
                                    shallow = copy.copy(squad)
                                    deep = copy.deepcopy(squad)
                                    squad[0].append("坠毁")
                                    print("原:", squad) # [['一代机', '坠毁'], ['二代机']]
                                    print("浅:", shallow) # [['一代机', '坠毁'], ['二代机']] ← 受影响
                                    print("深:", deep) # [['一代机'], ['二代机']] ← 不受影响
```
真实运行输出：
```text
一代机(战斗力=60) VS 敌机(战斗力=70) -> 英雄败
二代机(战斗力=80) VS 敌机(战斗力=70) -> 英雄胜
战机总数: 3
MRO: ['AdvHeroFighter', 'HeroFighter', 'Fighter', 'ABC', 'object']
原: [['一代机', '坠毁'], ['二代机']]
浅: [['一代机', '坠毁'], ['二代机']]
深: [['一代机'], ['二代机']]
```
**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `class Fighter(ABC)` | 抽象基类不能直接实例化，`@abstractmethod` 强制子类实现 |
| `self.__power` | 被改写为 `self._Fighter__power`，子类同名属性互不冲突 |
| `Fighter.total += 1` | 改类属性必须用**类名**，用 `self.total += 1` 会新建实例属性 |
| `hero: Fighter` 类型注解 | 只是提示，不是强制；多态真正依赖的是"有没有 `attack`" |
| `AdvHeroFighter.__mro__` | 打印出来才知道方法查找顺序，含 `ABC` 说明元类参与 |
| `copy.copy` vs `deepcopy` | 浅拷贝只复制外层容器，内层列表仍共享 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「面向对象编程：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/03-面向对象与数据模型/03-面向对象编程.md)
