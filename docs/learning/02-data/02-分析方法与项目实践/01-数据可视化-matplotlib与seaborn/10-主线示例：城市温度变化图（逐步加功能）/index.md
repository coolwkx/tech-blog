---
article_id: kp-3ee795f65ee760e9
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-71094c625b7f
learning_sourceId: 71094c625b7f
learning_order: 9
learning_objective: 理解并验证：主线示例：城市温度变化图（逐步加功能）
---

# 主线示例：城市温度变化图（逐步加功能）

> **学习目标**：能够解释「主线示例：城市温度变化图（逐步加功能）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../../../../../02-data/02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
>
> **所属主题**：-数据可视化-matplotlib与seaborn · 可运行示例

## 本次只学这一点

```python
import matplotlib.pyplot as plt, random
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

x = range(60)
y_shanghai = [random.uniform(15, 18) for i in x] # 上海 15~18 度
y_beijing = [random.uniform(1, 3) for i in x] # 北京 1~3 度

# ---- 第 1 步：最小可运行版本 ----
plt.figure(figsize=(20, 8), dpi=100) # ① 建画布，长宽比 2.5:1
plt.plot(x, y_shanghai) # ② 画图
plt.show # ③ 显示

# ---- 第 2 步：加刻度、网格、标签、标题、图例 ----
plt.figure(figsize=(20, 8), dpi=100)
plt.plot(x, y_shanghai, label='上海')
plt.plot(x, y_beijing, color='r', linestyle='--', label='北京')
x_ticks_label = ['11点{}分'.format(i) for i in x]
plt.xticks(x[::5], x_ticks_label[::5]) # 抽稀：每 5 分钟一个刻度
plt.yticks(range(0, 40, 5))
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlabel('时间'); plt.ylabel('温度')
plt.title('中午11点--12点某城市温度变化图', fontsize=20)
plt.legend(loc='best') # 不调用这一行，图例不会出现
plt.savefig('./test.png') # 必须在 show 之前
plt.show

# ---- 第 3 步：画数学函数图像（plt.plot 也能画曲线） ----
import numpy as np
xs = np.linspace(-10, 10, 1000) # 1000 个点，足够平滑
plt.figure(figsize=(20, 8), dpi=100)
plt.plot(xs, np.sin(xs)); plt.grid; plt.title('y = sin(x)')
plt.show
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「主线示例：城市温度变化图（逐步加功能）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/03-可视化与统计/08-数据可视化-matplotlib与seaborn.md)
