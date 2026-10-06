---
article_id: kp-6283dd3476f8ad36
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-035144ef44a8
learning_sourceId: 035144ef44a8
learning_order: 1
learning_objective: 理解并验证：四种导入形式对比
---

# 四种导入形式对比

> **学习目标**：能够解释「四种导入形式对比」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：函数与全局变量（02 篇）、类与对象（03 篇）、`try/except ImportError`（04 篇）。
>
> **所属主题**：模块与包管理 · 核心概念

## 本次只学这一点

| 写法 | 命名空间效果 | 优点 | 缺点 |
| --- | --- | --- | --- |
| `import math` | 只有 `math` 一个名字 | 来源清晰，`math.sqrt` 一眼看出出处 | 调用时要写前缀 |
| `from math import sqrt` | 直接得到 `sqrt` | 调用简洁 | 名字来源不明确，可能被覆盖 |
| `from math import *` | 导入所有公开名字 | 写起来最短 | **污染命名空间**，与本地名字冲突难排查 |
| `import numpy as np` | 得到 `np` | 短前缀 + 来源清晰 | 需要记住别名约定 |
| `from math import sqrt as sq` | 得到 `sq` | 解决命名冲突、统一接口名 | 可能有多个名字指向同一实现 |
```python
import math
print(math.sqrt(16)) # 4.0

from math import sqrt
print(sqrt(16)) # 4.0

import math as m
print(m.sqrt(16)) # 4.0

from math import sqrt as sq
print(sq(16)) # 4.0
```
**实践建议**：生产代码优先用 `import 模块` 或 `import 模块 as 别名`；`from ... import *` 只应该出现在 `__init__.py` 的受控导出里（配合 `__all__`）。

**别名约定（读别人的代码必备）**：

| 约定 | 包 |
| --- | --- |
| `np` | numpy |
| `pd` | pandas |
| `plt` | matplotlib.pyplot |
| `sns` | seaborn |
| `tf` / `torch` | tensorflow / pytorch |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「四种导入形式对比」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/05-模块与包管理.md)
