---
article_id: "71094c625b7f"
learning_kind: "reference"
learning_category: "02-data"
---

# -数据可视化-matplotlib与seaborn


> **一句话总结**：Matplotlib 的绘图流程永远是"**建画布（`plt.figure`）→ 画图（`plot/bar/hist/pie/scatter`）→ 加装饰（刻度、网格、标签、图例）→ 保存（`savefig`）→ 显示（`show`）**"五步；选图型只取决于你要表达"趋势、对比、分布、占比还是关系"。
> **前置知识**：[05-NumPy数值计算](../02-NumPy与Pandas/05-NumPy数值计算.md)（`linspace`、`random`）；[07-Pandas分组聚合与透视](../02-NumPy与Pandas/07-Pandas分组聚合与透视.md)（`Series`/`DataFrame` 的 `.plot`）。
> **学完能做到**：1. 独立完成一张规范图表：中文字体、刻度、网格、轴标签、标题、图例、保存一步不落；2. 按分析目的正确选择折线/柱状/直方/饼/散点图，并用 `subplots` 画多子图；3. 说清 `savefig` 与 `show` 的顺序问题，以及直方图与柱状图的本质区别。

## 1. 核心概念

### 1.1 为什么学 Matplotlib

可视化是数据挖掘的关键辅助工具：把数据**直观呈现**，一眼看出趋势、异常与分布；让结论更**客观有说服力**；还能**反哺分析方法**——看图发现异常点后回头调整策略。Matplotlib 是 Python 中使用最多的绘图库，专做 2D（含 3D）图表，入口模块是 `matplotlib.pyplot`（提供一系列类似 MATLAB 的函数）。

### 1.2 绘图五步法与核心 API

| 步骤 | API | 说明 |
| --- | --- | --- |
| ① 准备数据 | `x`、`y` | 列表、`range`、`ndarray` 均可 |
| ② 创建画布 | `plt.figure(figsize=(w,h), dpi=)` | `figsize` 单位英寸，决定长宽比；`dpi` 决定清晰度；返回 `Figure` 对象 |
| ③ 绘制图形 | `plt.plot/bar/hist/pie/scatter(...)` | 面向过程风格 |
| ④ 添加辅助元素 | `plt.xticks/yticks/grid/xlabel/ylabel/title/legend` | 见 1.3 |
| ⑤ 保存与显示 | `plt.savefig(path)` → `plt.show` | **顺序不能反** |

图像结构（自外向内）：`Figure`（整张画布）→ `Axes`（坐标系/绘图区，可多个）→ `Axis`（坐标轴）→ 刻度与刻度标签 → 数据图形 → 图例与标题。

### 1.3 辅助功能 API 速查

| 功能 | API | 关键点 |
| --- | --- | --- |
| 自定义 x 轴刻度与标签 | `plt.xticks(x, labels)` | 标签数量必须与刻度数量一致，常用 `x[::5]` 抽稀 |
| 自定义 y 轴刻度 | `plt.yticks(y)` | 同上 |
| 网格 | `plt.grid(True, linestyle='--', alpha=0.5)` | `alpha` 是**透明度** 0~1，越小越淡 |
| 轴名称 | `plt.xlabel('时间')` / `plt.ylabel('温度')` | — |
| 标题 | `plt.title('...', fontsize=20)` | `fontsize` 控制字号 |
| 图例 | `plt.plot(..., label='上海')` + `plt.legend(loc='best')` | **只写 `label` 不会显示图例**，必须调 `legend` |
| 保存图片 | `plt.savefig('./test.png')` | 必须在 `show` **之前** |
| 多子图 | `fig, axes = plt.subplots(nrows, ncols, figsize=, dpi=)` | 返回画布与坐标系数组，用 `axes[i].set_xxx` |

### 1.4 颜色与线型字符表

| 颜色 | 线型 | 样式 |
| --- | --- | --- |
| `r` 红 / `g` 绿 / `b` 蓝 / `w` 白 | `-` | 实线 |
| `c` 青 / `m` 洋红 / `y` 黄 / `k` 黑 | `--` | 虚线 |
| | `-.` | 点划线 |
| | `:` | 点虚线 |
| | （空格） | 不画线 |

用法：`plt.plot(x, y, color='r', linestyle='--', label='北京')`。

### 1.5 legend 的 loc 参数

| String | 编码 | String | 编码 |
| --- | --- | --- | --- |
| `'best'` | 0 | `'center left'` | 6 |
| `'upper right'` | 1 | `'center right'` | 7 |
| `'upper left'` | 2 | `'lower center'` | 8 |
| `'lower left'` | 3 | `'upper center'` | 9 |
| `'lower right'` | 4 | `'center'` | 10 |
| `'right'` | 5 | | |

推荐 `loc='best'`，让 Matplotlib 自动选择遮挡最少的位置。

### 1.6 常见图形选型对照表

| 图形 | API | 表达什么 | 数据特征 | 典型场景 |
| --- | --- | --- | --- | --- |
| **折线图** | `plt.plot(x, y)` | **变化趋势** | 有序、连续的序列 | 日活、App 下载量、功能上线后点击量随时间变化 |
| **柱状图** | `plt.bar(x, height, width, align, color)` | **对比大小** | **离散**的类别 | 各城市销售额对比、品类销量排名 |
| **直方图** | `plt.hist(x, bins)` | **数据分布** | **连续**数值，自动分箱 | 订单金额分布、考试分数分布 |
| **饼图** | `plt.pie(x, labels, autopct, colors)` | **占比结构** | 少量类别（建议 ≤ 6 类） | 各渠道收入占比、用户构成 |
| **散点图** | `plt.scatter(x, y)` | **变量间关系**、离群点 | 成对的两个连续变量 | 广告投入与销量、房价与面积 |

关键区分：**柱状图 vs 直方图**——柱状图横轴是**离散类别**（可任意排序，柱间有间隔）；直方图横轴是**连续区间**（bins，柱间紧挨，体现频数分布）。

### 1.7 中文字体问题的两种解决方案

**方案一：改配置文件（全局生效）**：① 下载支持中文的字体（如 `SimHei.ttf`）；② 安装到系统（Linux：`sudo cp ~/SimHei.ttf /usr/share/fonts/SimHei.ttf`；Windows/macOS 双击安装）；③ 删除字体缓存 `cd ~/.matplotlib && rm -r *`；④ 修改 `~/.matplotlib/matplotlibrc` 为 `font.family: sans-serif`、`font.sans-serif: SimHei`、`axes.unicode_minus: False`。

**方案二：代码里动态设置（推荐，随代码走、不污染环境）**：

```python
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 正常显示中文
mpl.rcParams['axes.unicode_minus'] = False # 正常显示负号
```

### 1.8 Pandas 集成的绘图接口

`Series`/`DataFrame` 自带 `.plot`（对 Matplotlib 的封装，默认折线图）：`s.plot` 折线、`s.plot(kind='bar')` / `'barh'` 柱状/横向柱状、`s.plot(kind='pie')` 饼图、`s.plot(kind='hist')` 直方图、`s.plot(legend=True)` 带图例、`pro.plot(kind='bar', stacked=True)` 堆叠柱状图（看比例构成）。注意在脚本里 `.plot` 之后仍需 `plt.show`。

### 1.9 关于 Seaborn

> 本**只系统讲解 Matplotlib**，Seaborn 仅在"常用 Python 数据分析开源库介绍"里被点名，原话是：*"Seaborn 是一个 Python 数据可视化开源库，建立在 matplotlib 之上，并集成了 pandas 的数据结构；通过更简洁的 API 来绘制信息更丰富、更具吸引力的图像；面向数据集的 API，与 Pandas 配合使用起来比直接使用 Matplotlib 更方便。"*

因此本章以 Matplotlib 为唯一考核范围，Seaborn 放在第 2 节末尾的**延伸补充**中做入门示例。

## 2. 可运行示例

### 2.1 主线示例：城市温度变化图（逐步加功能）

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

### 2.2 多子图：plt.subplots（面向对象风格）

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

### 2.3 五种常见图形

```python
import numpy as np, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

# 1. 柱状图：离散类别对比
plt.figure(figsize=(8, 5))
plt.bar(['A', 'B', 'C', 'D'], [3, 7, 5, 4], color='blue', width=0.6)
plt.title('各分类数值对比'); plt.xlabel('分类'); plt.ylabel('数值'); plt.show

# 2. 直方图：连续数据分布（bins 区间个数；alpha 透明度；rwidth 条形宽度占比）
plt.figure(figsize=(10, 6))
plt.hist(np.random.randn(500), bins=30, color='blue', alpha=0.7, rwidth=0.85)
plt.title('正态分布数据直方图'); plt.xlabel('取值'); plt.ylabel('频数')
plt.grid(True); plt.show

# 3. 饼图：占比结构（autopct 中的 %% 是"百分号字符"的转义）
plt.figure(figsize=(7, 7))
plt.pie([25, 35, 25, 15], labels=['分类A', '分类B', '分类C', '分类D'],
autopct='%1.1f%%', startangle=90, counterclock=False)
plt.title('各分类占比'); plt.show

# 4. 散点图：两变量关系
plt.figure(figsize=(8, 6))
plt.scatter([1, 2, 3, 4, 5], [2, 3, 5, 7, 11], color='red')
plt.title('两变量关系'); plt.xlabel('X'); plt.ylabel('Y'); plt.show

# 5. 折线图：趋势
days = range(1, 8)
plt.figure(figsize=(10, 5))
plt.plot(days, [1200, 1350, 1100, 1500, 1800, 1650, 2000], marker='o', label='日活')
plt.xticks(list(days), ['周一', '周二', '周三', '周四', '周五', '周六', '周日'])
plt.xlabel('星期'); plt.ylabel('活跃用户数'); plt.title('一周日活趋势')
plt.grid(True, linestyle='--', alpha=0.5); plt.legend; plt.show
```

### 2.4 Pandas 集成绘图

```python
import pandas as pd, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

gdp = pd.DataFrame({'中国': [100, 200, 350, 500], '美国': [400, 420, 450, 480],
'日本': [300, 280, 260, 240]}, index=[2016, 2017, 2018, 2019])
gdp.plot(legend=True, title='三国 GDP 趋势') # 多条折线并自动出图例
plt.xlabel('年份'); plt.ylabel('GDP'); plt.show

s = pd.Series([2.62, 1.44, 1.57, 2.02, 8.51, -1.23],
index=pd.date_range('2024-01-01', periods=6))
s.cumsum.plot(title='累计涨跌幅'); plt.show # 累计走势

pd.Series({'高价值': 355, '中价值': 1200, '低价值': 2400}) \
.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.ylabel(''); plt.title('客户价值分层占比'); plt.show # 隐藏多余的 y 轴标签
```

### 延伸补充：Seaborn（这里仅点名，未展开）

> 以下 API **未在讲解**，属进阶延伸，考试/作业以 Matplotlib 为准。Seaborn 建立在 Matplotlib 之上并直接接受 DataFrame，在"按分类字段拆分绘图"场景下代码更短。

```python
import seaborn as sns, matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

sns.set_theme(style='whitegrid') # 相当于 seaborn 版的 rcParams
df = sns.load_dataset('tips') # 内置示例数据集

sns.scatterplot(data=df, x='total_bill', y='tip', hue='sex') # 散点 + 分类着色
sns.barplot(data=df, x='day', y='total_bill', hue='sex') # 自动分组的柱状图
sns.histplot(data=df, x='total_bill', bins=20, kde=True) # 直方图 + 核密度
sns.boxplot(data=df, x='day', y='total_bill') # 箱线图：分布与离群点
sns.heatmap(df.select_dtypes('number').corr, annot=True, cmap='coolwarm') # 相关性热力图
plt.show
```

分工：Seaborn 负责**统计图形的语义层**（自动分组、自动算置信区间、直接吃 DataFrame），Matplotlib 负责**底层渲染与精细控制**，两者可混用。

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `savefig` 写在 `show` 之后 | 保存出来是空白图 | `show` 会**释放 Figure 资源** | `savefig` 必须在 `show` **之前** |
| 图例不显示 | `label` 写了却看不到图例 | `label` 只是给线起名，还需显式调图例 | 补上 `plt.legend(loc='best')` |
| 中文显示成方框 `□□□` | 标题、轴标签都是方块 | 默认字体不含中文字形 | `mpl.rcParams['font.sans-serif'] = ['SimHei']` |
| 负号显示成方框 | `-1` 变成 `□1` | 中文字体缺少 Unicode 负号字形 | `mpl.rcParams['axes.unicode_minus'] = False` |
| 把直方图当柱状图用 | 想对比类别却得到不等宽区间 | 二者本质不同：直方图横轴是**连续区间** | 离散类别用 `plt.bar`，连续分布用 `plt.hist` |
| `bins` 理解成"柱宽" | 不知该怎么调分布粒度 | `bins` 是**区间个数**（或边界序列） | 想更细就增大 `bins`，也可传自定义边界列表 |
| `autopct` 写成 `'%1.1f%'` | `ValueError: unsupported format character` | 格式化字符串里字面百分号必须转义 | 写 `autopct='%1.1f%%'` |
| 多子图用 `plt.xxx` 装饰 | 所有设置都加到了最后一个子图上 | `plt.xxx` 作用于"当前活动坐标系" | 多子图统一用 `axes[i].set_xxx` |
| 1×1 子图时写 `axes[0]` | `TypeError: 'Axes' object is not subscriptable` | `plt.subplots(1,1)` 返回单个 `Axes`，**不是数组** | 用 `(1, 2)`；或 `axes = np.atleast_1d(axes)` 统一处理 |
| `figsize=(10, 10)` 画时间序列 | 图被压得很扁 | 长宽比与数据形状不匹配 | 时间序列用宽幅比例，如 `(20, 8)` |
| 只调 `linestyle` 忘了 `color` | 两条线颜色相同，分不清 | 颜色与线型是两个独立参数 | 同时指定 `color` 与 `linestyle`，并加 `label` |

## 4. 面试问答

### Q1：为什么 `plt.savefig` 必须写在 `plt.show` 前面？

<details markdown="1"><summary markdown="1">参考答案</summary>

因为 `plt.show` 在渲染并展示图像后会**释放（销毁）Figure 对象占用的资源**，当前画布随之变空。若在 `show` 之后再 `savefig`，保存的就是这张已清空的画布，得到的是一张空白图片。

```python
plt.figure(figsize=(20, 8), dpi=100)
plt.plot(x, y); plt.title('...')
plt.savefig('./test.png') # 先存
plt.show # 再显示
```

补充：Jupyter 常用的内联后端会在 cell 结束时自动渲染并关闭图形，所以"跨 cell 先 show 再 save"同样拿到空图，稳妥做法是在**同一个 cell** 里先 `savefig` 再 `show`。`savefig` 还支持 `dpi=`（单独指定导出清晰度，如 300）、`bbox_inches='tight'`（裁掉多余白边）、`transparent=True`。

</details>

### Q2：柱状图和直方图有什么区别？分别用在什么场景？

<details markdown="1"><summary markdown="1">参考答案</summary>

| 维度 | 柱状图 `plt.bar` | 直方图 `plt.hist` |
| --- | --- | --- |
| 横轴含义 | **离散类别**（城市、品类、渠道） | **连续数值区间**（bins，由数据分箱） |
| 柱的含义 | 一个类别的值 | 一个区间内的**频数/密度** |
| 排列 | 类别可任意排序，柱间**留有间隙** | 按数值连续排列，柱间**紧挨** |
| 是否分组统计 | 否，直接画给定值 | **是**，内部先分箱计数 |
| 表达目的 | **对比**大小 | 看**分布形状**（对称、双峰、离群） |
| 典型场景 | 各城市销售额对比、品类销量排名 | 订单金额分布、考试成绩分布 |

判断方法：**横轴是"名字"还是"数字刻度"**——是名字（可随便换顺序）→ 柱状图；是数字且需分箱统计频数 → 直方图。`plt.hist` 的核心参数是 `bins`：增大 `bins` 分布更细但更"毛躁"，减少则更平滑但可能掩盖双峰；实践中可叠加核密度曲线（seaborn 的 `kde=True`）辅助判断分布形态。

</details>

### Q3：`plt.subplots` 的面向对象写法和 `plt.xxx` 面向过程写法有什么区别？

<details markdown="1"><summary markdown="1">参考答案</summary>

- **面向过程（`plt.xxx`）**：`matplotlib.pyplot` 维护"当前活动 Figure / Axes"的概念，`plt.plot`、`plt.title` 都作用在它上面，写法短，画单张图方便。
- **面向对象（`fig, axes = plt.subplots(...)` + `axes[i].set_xxx`）**：显式拿到画布 `fig` 与坐标系数组 `axes`，每一步都明确指定作用对象。

| 维度 | `plt.xxx` | `axes[i].set_xxx` |
| --- | --- | --- |
| 表达力 | 单图够用 | 多子图、复杂布局、精细控制更强 |
| 多子图风险 | 容易把所有设置加到"最后一个子图" | 每个子图独立设置，不会串台 |
| 方法命名 | `plt.xlabel/xticks/title` | `axes.set_xlabel/set_xticks/set_title` |
| 图例 | `plt.legend` | `axes[i].legend` |

官方推荐 `subplots`（旧的 `subplot` 使用不便）。注意 `nrows=1, ncols=1` 时返回的 `axes` 是**单个 Axes 对象而非数组**，不能写 `axes[0]`，这是最常见的报错来源。`fig` 对象还提供图级操作，如 `fig.suptitle('总标题')`、`fig.tight_layout`（自动调整子图间距）。

</details>

## 5. 自测题

### 1. 写出绘制折线图的完整骨架：尺寸 20×8、清晰度 100、中文正常、有轴标签与标题、有网格与图例，并保存为 `chart.png`。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 中文
mpl.rcParams['axes.unicode_minus'] = False # 负号

x = [1, 2, 3, 4, 5]
plt.figure(figsize=(20, 8), dpi=100) # ① 建画布
plt.plot(x, [17, 17, 18, 15, 11], label='上海') # ② 画图
plt.plot(x, [2, 3, 2, 1, 3], color='r', linestyle='--', label='北京')
plt.xticks(x, ['第1天', '第2天', '第3天', '第4天', '第5天']) # ③ 装饰
plt.grid(True, linestyle='--', alpha=0.5)
plt.xlabel('时间'); plt.ylabel('温度'); plt.title('两地温度变化对比', fontsize=20)
plt.legend(loc='best')
plt.savefig('./chart.png') # ④ 保存（在 show 之前）
plt.show # ⑤ 显示
```

评分要点：中文字体两行设置、`legend` 不能省、`savefig` 在 `show` 之前、`figsize` 长宽比合理（不要 `(10,10)`）。

</details>

### 2. 运行后中文标题显示成方框、负号也异常，原因是什么？给出修复代码。

<details markdown="1"><summary markdown="1">参考答案</summary>

**原因**：Matplotlib 默认字体（`DejaVu Sans`）**不包含中文字形**，中文被渲染成方框（"豆腐块"）；同时该字体的负号字形与 Matplotlib 期望的 Unicode 减号（U+2212）不一致，负号也显示为方框。

```python
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 指定支持中文的字体
mpl.rcParams['axes.unicode_minus'] = False # 用 ASCII 连字符代替 Unicode 减号

plt.plot([1, 2, 3], [-1, 0, 1]); plt.title('温度变化')
plt.show
```

说明：这两行是**全局设置**，脚本开头运行一次即可；也可写进 `~/.matplotlib/matplotlibrc` 长期生效（改完需删字体缓存）。`SimHei` 是 Windows 常见可用项；Linux 可换 `WenQuanYi Micro Hei`、`Noto Sans CJK SC`，macOS 常用 `Arial Unicode MS`。

</details>

### 3. 按分析目的选图形：① 一周日活变化；② 各城市销售额排名；③ 用户年龄分布；④ 广告投入与销量的关系；⑤ 各渠道收入占比。

<details markdown="1"><summary markdown="1">参考答案</summary>

| 目的 | 选择 | API | 理由 |
| --- | --- | --- | --- |
| ① 日活随时间变化 | **折线图** | `plt.plot(days, uv)` | 有序时间序列，重点表达**趋势** |
| ② 各城市销售额排名 | **柱状图** | `plt.bar(cities, sales)` | 离散类别比**大小**，按降序排列更直观 |
| ③ 用户年龄分布 | **直方图** | `plt.hist(ages, bins=20)` | 连续数值看**分布形态** |
| ④ 广告投入与销量 | **散点图** | `plt.scatter(ad, sales)` | 两连续变量的**相关性**，并发现离群点 |
| ⑤ 各渠道收入占比 | **饼图**（或横向柱状图） | `plt.pie(sizes, labels=..., autopct='%1.1f%%')` | 部分与整体的**占比**；类别多时改用 `barh` |

选图口诀：**趋势折线、对比柱状、分布直方、占比饼图、关系散点。**

补充建议：图表要能独立看懂——必须有标题、轴标签（带单位）、图例；类别较多时按数值排序；颜色区分要明显；导出用 `dpi=300` 保证清晰度。

</details>

## 6. 延伸阅读

- [Matplotlib 官方文档：Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)
- [Matplotlib 官方文档：Pyplot tutorial](https://matplotlib.org/stable/tutorials/pyplot.html)
- [Matplotlib 官方 Gallery（按图形类型浏览示例）](https://matplotlib.org/stable/gallery/index.html)
- [Matplotlib 官方文档：Customizing with style sheets and rcParams](https://matplotlib.org/stable/users/explain/customizing.html)
- [Seaborn 官方 Tutorial（本主题展开，进阶参考）](https://seaborn.pydata.org/tutorial.html)

---

[⬅️ 返回数据处理目录](README.md)
