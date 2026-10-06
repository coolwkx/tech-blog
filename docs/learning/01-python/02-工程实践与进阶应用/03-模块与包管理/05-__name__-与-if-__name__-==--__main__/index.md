---
article_id: kp-369747d2dd1ebc5d
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-035144ef44a8
learning_sourceId: 035144ef44a8
learning_order: 4
learning_objective: '理解并验证：__name__ 与 if __name__ == "__main__":'
---

# __name__ 与 if __name__ == "__main__":

> **学习目标**：能够解释「__name__ 与 if __name__ == "__main__":」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与全局变量（02 篇）、类与对象（03 篇）、`try/except ImportError`（04 篇）。
>
> **所属主题**：模块与包管理 · 核心概念

## 本次只学这一点

每个模块都有一个 `__name__` 属性：

| 场景 | `__name__` 的值 |
| --- | --- |
| 直接运行 `python app.py` | `"__main__"` |
| 被导入 `import app` | `"app"` |
| 用 `python -m mypkg.math_utils` 运行 | `"__main__"` |
| 包 `mypkg/__init__.py` | `"mypkg"` |
```python
# student.py
if __name__ == "__main__":
 s = Student("乔峰", 33, "男", "13800138000", "丐帮帮主")
 print(s)
```
**作用**：让这个文件既能当"库"被别人 `import`（不执行测试代码），又能当"脚本"自己跑。的 `student.py`、`main.py`、`08-异常处理.py` 都用了这个写法，原因就在这里。

> 补充：`__name__` 与包名是两个概念。包里的 `__init__.py` 的 `__name__` 就是包名本身，所以那里写 `if __name__ == "__main__":` 永远不会为真。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「__name__ 与 if __name__ == "__main__":」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)
