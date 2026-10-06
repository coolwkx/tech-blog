---
article_id: kp-f794f46cb5ac1c16
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 10
learning_objective: 理解并验证：多子图：plt.subplots（面向对象风格）
---

# 多子图：plt.subplots（面向对象风格）

> **学习目标**：能够解释「多子图：plt.subplots（面向对象风格）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 可运行示例

## 本次只学这一点

```python
import matplotlib.pyplot as plt, random
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

x = range(60)
y_shanghai = [random.uniform(15, 18) for i in x]
y_beijing = [random.uniform(1, 5) for i in x]
x_ticks_label = ['11点{}分'.format(i) for i in x]

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 8), dpi=100) # 1 行 2 列
axes[0].plot(x, y_shanghai, label='上海')
axes[1].plot(x, y_beijing, color='r', linestyle='--', label='北京')
for ax in axes: # 两个子图的装饰统一处理
 ax.set_xticks(x[::5]); ax.set_yticks(range(0, 40, 5))
 ax.set_xticklabels(x_ticks_label[::5])
 ax.set_xlabel('时间'); ax.set_ylabel('温度')
 ax.grid(True, linestyle='--', alpha=0.5); ax.legend(loc=0)
axes[0].set_title('上海温度变化'); axes[1].set_title('北京温度变化')
plt.savefig('./subplots.png'); plt.show
```

> 面向过程 vs 面向对象：`plt.函数名` 作用于"当前活动坐标系"，写法短但多子图时容易搞混；`axes.set_方法名` 显式指定对象，多子图与复杂布局时更清晰可控。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多子图：plt.subplots（面向对象风格）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
