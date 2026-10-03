> **一句话总结**：`groupby` 是 Pandas 里"化整为零再汇总"的总开关，遵循 **split（按 key 切分）→ apply（对每组算）→ combine（拼回一张表）** 三步；`crosstab`（交叉表）与 `pivot_table`（透视表）是同一思想的两种"表单化"表达——前者数**频数**，后者聚合**数值**。
> **前置知识**：[06-Pandas数据清洗](06-Pandas数据清洗.md)（索引、`loc/iloc`、缺失值、`merge`）；[05-NumPy数值计算](05-NumPy数值计算.md) 的聚合函数与 `np.where`。
> **学完能做到**：1. 用 `groupby + agg` 一次完成"多字段分组 + 不同列不同聚合"；2. 用 `crosstab` 与 `pivot_table` 把明细数据变成二维汇总表并算出比例；3. 独立完成"股票涨跌与星期几的关系"这类分组对比分析并出图。

## 1. 核心概念

### 1.1 groupby 的三步心智模型

```text
原始明细表
 │ ① split：按 key 把行切成若干组
 ├── 组 A（key = 男）
 ├── 组 B（key = 女）
 │ ② apply：对每组施加聚合/转换/过滤函数
 │ ③ combine：把每组的计算结果拼成一张新表
 ▼
汇总结果表（每组一行）
```

为什么比手写 `for` 循环好：

| 维度 | 手写循环 | `groupby` |
| --- | --- | --- |
| 代码量 | 需手动分桶、累加、拼结果 | 一行表达 |
| 正确性 | 容易漏组、漏空值、索引错乱 | 统一处理分组键与索引 |
| 性能 | Python 层逐行操作，慢 | 底层 C 实现 + 向量化 |
| 可组合 | 很难叠加多种聚合 | `agg` 一次给多列多种函数 |

### 1.2 分组对象与常用操作

| 操作 | API | 说明 |
| --- | --- | --- |
| 按一列分组 | `df.groupby('列')` | 返回 `DataFrameGroupBy`，**惰性求值**，不立即计算 |
| 按多列分组 | `df.groupby(['列1','列2'])` | 结果以 MultiIndex 组织 |
| 只取某列 | `df.groupby('列')['目标列']` | 返回 `SeriesGroupBy`，只对该列计算 |
| 组内第一条/最后一条 | `gb.first` / `gb.last` | 取每组第一行、最后一行 |
| 取指定组 | `gb.get_group('组名')` / `gb.get_group(('A','B'))` | 多字段分组时传元组 |
| 分组聚合 | `gb.agg(...)` / `gb.sum` / `gb.mean` | 见 1.3 |
| 分组过滤 | `gb.filter(lambda s: 条件)` | **保留满足条件的整组行**，行数不一定变 |
| 分组转换 | `gb.transform(f)` | 返回**与原表等长**的结果，常用于组内填充/标准化 |
| 分组应用 | `gb.apply(f)` | 最通用可返回任意形状，但**最慢** |

### 1.3 聚合函数与 agg 的四种写法

| 函数 | 含义 | 与 `count` 的差别 |
| --- | --- | --- |
| `count` | 非空值个数 | **不统计 NaN** |
| `size` | 元素个数 | **统计 NaN**（统计的是行数） |
| `sum` / `mean` / `median` | 求和 / 均值 / 中位数 | 中位数不受极值影响 |
| `max` / `min` | 最大 / 最小 | 也可用于日期、字符串 |
| `std` / `var` | 标准差 / 方差 | 方差开根号即标准差 |
| `nunique` | 去重后个数 | 常用来数"有多少个不同客户" |

```python
gb.agg('sum') # ① 所有列同一个函数
gb.agg(['sum', 'mean', 'max']) # ② 所有列多个函数（MultiIndex 列）
gb.agg({'revenue': 'mean', 'unit_cost': 'sum'}) # ③ 不同列不同函数（最常用）
gb.agg(平均销售额=('revenue', 'mean')) # ④ 命名聚合，可自定义结果列名
```

`as_index` 的作用：`df.groupby('city', as_index=False)` 把分组键作为**普通列**返回，等价于 `groupby(...).reset_index`。

### 1.4 交叉表 crosstab

用于**计算一列数据对另一列数据的分组个数**——"统计分组频数的特殊透视表"。

```python
pd.crosstab(index, columns, values=None, aggfunc=None, normalize=False, margins=False)
```

| 参数 | 作用 |
| --- | --- |
| `index` / `columns` | 行方向 / 列方向的分类字段 |
| `normalize` | `True`/`'all'` 全部占比、`'index'` 每行占比、`'columns'` 每列占比 |
| `margins=True` | 增加"总计"行列 |
| `values` + `aggfunc` | 不数频数，改为对某数值列聚合 |

### 1.5 透视表 pivot_table

把原 DataFrame 的列**分别作为行索引和列索引**，再对指定列应用聚合函数。

```python
df.pivot_table(values=None, index=None, columns=None, aggfunc='mean',
fill_value=None, margins=False)
```

| 参数 | 作用 |
| --- | --- |
| `index` / `columns` | 行方向键 / 列方向键（把该列不同取值展开成多列） |
| `values` / `aggfunc` | 要聚合的数值列 / 聚合函数（默认 `'mean'`，可传列表或字典） |
| `fill_value` | 填补缺失的交叉格 |
| `margins=True` | 增加总计行列 |

### 1.6 crosstab vs pivot_table vs groupby

| 维度 | `groupby.agg` | `pd.crosstab` | `df.pivot_table` |
| --- | --- | --- | --- |
| 输出形态 | 一维/多级索引汇总表 | **二维**频数表（行×列） | **二维**聚合表（行×列） |
| 聚合对象 | 任意列 | 默认数**频数**；给 `values` 后可聚合 | 必须是**数值列** |
| 默认函数 | 需显式指定 | 计数 | `mean` |
| 适合场景 | 多层分组统计 | 两个分类字段的交叉分布 | 行列两个维度下的指标汇总 |
| 结果等价于 | — | `groupby.size.unstack` | `groupby.agg.unstack` |

一句话选择：**要"每组的指标"用 groupby，要"两个分类字段的交叉分布"用 crosstab，要"行维度 × 列维度下的数值汇总"用 pivot_table。**

### 1.7 完整案例的业务逻辑：股票涨跌与星期几的关系

| 步骤 | 做法 |
| --- | --- |
| ① 提取分类维度 | `pd.to_datetime(df.index).weekday` → 0=周一 … 6=周日 |
| ② 目标变量二值化 | `np.where(df['p_change'] > 0, 1, 0)` → 1 表示涨、0 表示跌 |
| ③ 交叉计数 | `pd.crosstab(df['week'], df['posi_neg'])` 得每个星期几的涨/跌天数 |
| ④ 转成比例 | 按行求和后用 `div(..., axis=0)` 相除，得到"上涨占比" |
| ⑤ 可视化 | `pro.plot(kind='bar', stacked=True)` 堆叠柱状图 |
| ⑥ 一行替代 ③④ | `df.pivot_table(['posi_neg'], index='week')` 直接得均值（即上涨占比） |

## 2. 可运行示例

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']; mpl.rcParams['axes.unicode_minus'] = False

# ================= 0. 模拟优衣库门店销售明细 =================
df = pd.DataFrame({
'store_id': [1, 2, 3, 4, 5, 6, 7, 8],
'city': ['上海', '上海', '北京', '北京', '深圳', '深圳', '广州', '广州'],
'channel': ['线上', '线下', '线上', '线下', '线上', '线下', '线上', '线下'],
'gender_group': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
'customer': [120, 150, 90, 130, 200, 180, 160, 140],
'revenue': [24000.0, 31500.0, 16200.0, 26000.0, 44000.0, 37800.0, 33600.0, 29400.0],
'unit_cost': [12000.0, 18000.0, 8000.0, 14000.0, 22000.0, 19000.0, 17000.0, 15000.0],
})

# ================= 1. 分组对象与组内取值 =================
gb = df.groupby('gender_group') # DataFrameGroupBy（惰性）
print(type(gb)); print(gb['city']) # SeriesGroupBy
print(gb.get_group('Female')) # 取指定组的数据
gb2 = df.groupby(['gender_group', 'city'])
print(gb2.first, gb2.last) # 每组第一条 / 最后一条

# ================= 2. 分组聚合：三种等价写法 =================
print(df.groupby('city').customer.sum) # ① 链式
print(df.groupby('city').customer.agg('sum')) # ② agg + 函数名
print(df.groupby('city').agg({'customer': 'sum'})) # ③ agg + 字典

# 按城市、渠道分组，分别算销售额均值与成本总和（不同列不同函数）
print(df.groupby(['city', 'channel']).agg({'revenue': 'mean', 'unit_cost': 'sum'}))

# 同一列多种聚合
print(df.groupby('city').agg({'revenue': ['sum', 'mean', 'max'],
'customer': ['sum', 'count']}))

# 命名聚合：直接指定结果列名，避免 MultiIndex 列
print(df.groupby('city', as_index=False).agg(
总销售额=('revenue', 'sum'), 平均销售额=('revenue', 'mean'), 门店数=('store_id', 'nunique')))

# size 与 count 的差异
print(df.groupby('city').size) # 每组行数
print(df.groupby('city')['revenue'].count) # 每组 revenue 的非空个数

# ================= 3. 分组过滤 filter 与分组转换 transform =================
# 保留"该城市平均销售额 > 30000"的所有明细行
print(df.groupby('city').filter(lambda s: s['revenue'].mean > 30000))
# 换 SQL 思路：select * from df where city in
# (select city from df group by city having avg(revenue) > 30000);

# transform：返回与原表等长的结果，常用于"组内均值填充"
df2 = df.copy
df2['city_avg'] = df2.groupby('city')['revenue'].transform('mean')
df2['revenue_ratio'] = df2['revenue'] / df2['city_avg'] # 相对本城市均值的倍数
print(df2)

# apply：最灵活（可返回任意形状）但性能最差；能用 agg/transform 就不要用 apply
print(df.groupby('city').apply(lambda g: g.nlargest(1, 'revenue'), include_groups=False))

# ================= 4. value_counts =================
print(df['city'].value_counts)
print(df['city'].value_counts(normalize=True)) # 占比
df['city'].value_counts.plot(kind='bar'); plt.show

# ================= 5. 交叉表 crosstab =================
print(pd.crosstab(df['gender_group'], df['channel'])) # 频数
print(pd.crosstab(df['gender_group'], df['channel'], margins=True)) # 加总计
print(pd.crosstab(df['city'], df['channel'], normalize='index')) # 每行占比
print(pd.crosstab(df['city'], df['channel'], normalize='columns')) # 每列占比
print(pd.crosstab(df['city'], df['channel'], normalize='all')) # 占总体比例
print(df.groupby(['gender_group', 'channel']).size.unstack(fill_value=0)) # 等价写法

# ================= 6. 透视表 pivot_table =================
print(df.pivot_table(index='city', values='customer', aggfunc='sum')) # 基础
print(df.pivot_table(index='city', columns='channel', # 行列转置
values='customer', aggfunc='sum'))
print(df.pivot_table(index=['city', 'channel'], values=['revenue', 'unit_cost'],
aggfunc={'revenue': 'mean', 'unit_cost': 'sum'})) # 不同列不同函数
print(df.pivot_table(index='city', values=['revenue', 'unit_cost'],
aggfunc=['mean', 'sum'])) # 全部函数
print(df.pivot_table(index='city', columns='channel', values='revenue',
aggfunc='sum', fill_value=0, margins=True)) # 填 0 + 总计

# ================= 7. 完整案例：股票涨跌与星期几的关系 =================
dates = pd.date_range('2024-01-01', periods=20, freq='D')
stock = pd.DataFrame({'p_change': [2.62, 1.44, 1.57, 2.02, 8.51, -1.23, 0.85, 3.11,
-0.66, 1.98, -2.10, 0.45, 4.20, -1.85, 0.92, 2.33,
-0.57, 1.11, 3.05, -1.40]}, index=dates)

stock['week'] = pd.to_datetime(stock.index).weekday # 0=周一 … 6=周日
stock['posi_neg'] = np.where(stock['p_change'] > 0, 1, 0) # 涨为 1，跌为 0

count = pd.crosstab(stock['week'], stock['posi_neg']) # 每个星期几的涨/跌天数
row_sum = count.sum(axis=1).astype(np.float32) # 每个星期几的总天数
pro = count.div(row_sum, axis=0) # 逐行相除得比例
print(count); print(pro)

pro.plot(kind='bar', stacked=True)
plt.title('各星期几的涨跌比例'); plt.xlabel('星期（0=周一，6=周日）'); plt.ylabel('比例')
plt.show

# 用透视表一行完成：posi_neg 是 0/1，其"均值"恰好等于"1 的占比"= 上涨占比
print(stock.pivot_table(values='posi_neg', index='week', aggfunc='mean'))
```

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `count` 与 `size` 结果不一致 | 同一组一个 10 行一个 8 行 | `count` **不计 NaN**，`size` 数行数 | 要"行数"用 `size`；要"有效值个数"用 `count` |
| `groupby` 后取值报 `KeyError` | 访问被分组的列失败 | 分组键被移到了索引里（`as_index=True` 默认） | 加 `as_index=False` 或 `.reset_index` |
| 分组键结果变成 MultiIndex 列 | 导出或画图时列名是元组 | `agg(['sum','mean'])` 产生多级列索引 | 用**命名聚合** `agg(新名=('列','函数'))`，或 `.droplevel(0, axis=1)` |
| `filter` 当成"过滤行"用 | 结果行数没减少到预期 | `filter` 的粒度是**组**：组条件为真则整组保留 | 想过滤单行用布尔索引；要"每组前 N 行"用 `groupby.head(n)` 或 `nlargest` |
| `transform` 结果被误解 | 以为返回的是每组一行 | `transform` 返回**与原表等长**的序列 | 要"每组一行"用 `agg`；要"广播回原表"用 `transform` |
| 到处用 `apply` | 大数据量下非常慢 | `apply` 在 Python 层逐组调用，无向量化 | 能用 `agg`/`transform`/内置函数就不用 `apply` |
| `pivot_table` 报 `No numeric types to aggregate` | 无法计算 | 透视表默认聚合**数值列**，而 `values` 指向了字符串列 | 换数值列；或先用 `crosstab` 数频数 |
| `pivot_table` 行列写混 | 结果方向反了 | `index` 是行、`columns` 是列，容易与分组字段顺序混淆 | 记住 `index` 竖着排、`columns` 横着铺；不确定先跑一次看形状 |
| `pivot_table` 出现 NaN | 交叉格里是空 | 该行列组合没有数据 | 加 `fill_value=0` |
| `crosstab` 占比算错 | 比例加起来不等于 1 | `normalize` 方向选错 | `'index'` 每行和为 1；`'columns'` 每列和为 1；`'all'` 总和为 1 |
| 手动 `count.sum(axis=1)` 后相除报错 | 结果全是 NaN | 除数是 Series，默认按**列**对齐 | 用 `count.div(row_sum, axis=0)` 显式指定按行对齐 |
| `to_datetime(df.index).weekday` 报错 | 索引不是日期类型 | 索引是字符串而非 `DatetimeIndex` | 先 `pd.to_datetime(df.index)` 再取 `.weekday` |

## 4. 面试问答

### Q1：描述一下 `groupby` 的执行过程，它为什么比手写循环更好？

<details markdown="1"><summary markdown="1">参考答案</summary>

`groupby` 遵循 **split-apply-combine（拆分—应用—合并）** 三步：

1. **split**：按 `by` 指定的键把原始行分配到不同的组。这一步是**惰性**的——`df.groupby('city')` 只生成一个 `DataFrameGroupBy` 对象，不会立刻计算。
2. **apply**：对每个组施加函数，函数可以是：
 - **聚合** `agg`：每组返回**一个标量**，结果行数 = 组数；
 - **转换** `transform`：每组返回**与组等长的序列**，结果与原表行数相同；
 - **过滤** `filter`：每组返回**布尔值**，决定整组保留还是丢弃；
 - **通用** `apply`：可返回任意形状（最灵活也最慢）。
3. **combine**：把各组的返回值拼装成新的 DataFrame/Series，分组键成为结果索引（`as_index=False` 时成为普通列）。

比手写循环更好的原因：① **表达力**——一行完成"多字段分组 + 多列不同聚合"；② **正确性**——自动处理分组键组合、索引对齐、空组，避免漏组与类型错误；③ **性能**——底层 C 实现并向量化，利用哈希表分组；④ **可组合**——结果可继续 `.unstack`、`.plot`、`.to_excel`。

实战建议：优先用内置聚合函数（`sum/mean/count`），其次 `agg`，再其次 `transform`，**最后才用 `apply`**。

</details>

### Q2：`crosstab` 和 `pivot_table` 有什么区别？什么时候用哪个？

<details markdown="1"><summary markdown="1">参考答案</summary>

| 维度 | `pd.crosstab` | `df.pivot_table` |
| --- | --- | --- |
| 默认行为 | **数频数**（计数） | 对数值列求**均值** |
| 输入 | 传两个 Series/数组 | 传 DataFrame + 列名 |
| 聚合对象 | 默认是"行数"；给 `values`+`aggfunc` 才能聚合数值 | 必须指定数值列（`values`） |
| 典型用途 | 两个**分类字段**的交叉分布（性别×渠道、星期几×涨跌） | **行 × 列**两个维度下的**指标**汇总（城市×渠道的销售额） |
| 底层等价 | `groupby(...).size.unstack` | `groupby(...).agg(...).unstack` |

选择原则：想回答"**有多少**"（频数、占比）→ 用 `crosstab`，并用 `normalize='index'/'columns'/'all'` 直接得到比例；想回答"**指标是多少**"（销售额、均值、总和）→ 用 `pivot_table`，它能同时把两个维度铺开成行列，比多级 `groupby` 直观得多。两者都能加 `margins=True` 显示总计。

实用技巧：**二值变量的均值就是它的占比**。案例中 `posi_neg` 是 0/1，因此 `pivot_table(values='posi_neg', index='week', aggfunc='mean')` 直接得到"每周上涨的比例"，一步替代"crosstab → 行求和 → 相除"三步。

</details>

### Q3：`agg`、`transform`、`apply`、`filter` 分别适合什么场景？

<details markdown="1"><summary markdown="1">参考答案</summary>

| 方法 | 返回形状 | 典型用途 | 性能 |
| --- | --- | --- | --- |
| `agg` | **每组一行**（行数 = 组数） | 求每组均值/总和/计数，出报表 | 最快 |
| `transform` | **与原表等长** | 组内填充缺失值、组内标准化、算"该行相对组均值的倍数" | 快 |
| `filter` | 原表的**子集**（整组保留或丢弃） | "保留平均销售额 > 3 万的城市的所有明细" | 中 |
| `apply` | 任意形状 | 每组做复杂逻辑（`nlargest`、自定义返回结构） | **最慢** |

选择顺序按"输出粒度"判断：输出"每组一行"→ `agg`；输出"和原表一样的行数"→ `transform`；输出"原表的部分行且以组为单位决定去留"→ `filter`；以上都不满足（粒度不规则）→ 才用 `apply`。

```python
df.groupby('city').agg(avg_rev=('revenue', 'mean')) # 每组一行
df['city_avg'] = df.groupby('city')['revenue'].transform('mean') # 行数不变
df.groupby('city').filter(lambda g: g['revenue'].mean > 30000) # 整组保留
df.groupby('city').apply(lambda g: g.nlargest(1, 'revenue')) # 任意形状
```

注意：能用 `agg`/`transform` 表达的逻辑，性能通常比 `apply` 快数倍到数十倍，因为前者走向量化的 C 路径，后者要回到 Python 层逐组调用。

</details>

## 5. 自测题

### 1. 用 `groupby` 求出"每个城市、每个渠道的客户数之和与销售额均值"，并把分组键变成普通列。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
result = df.groupby(['city', 'channel']).agg({'customer': 'sum', 'revenue': 'mean'})

# 分组键变成普通列（而不是索引）
result2 = df.groupby(['city', 'channel'], as_index=False).agg(
{'customer': 'sum', 'revenue': 'mean'})

# 自定义结果列名，用命名聚合
result3 = df.groupby(['city', 'channel'], as_index=False).agg(
客户数=('customer', 'sum'), 销售额均值=('revenue', 'mean'))
```

要点：`agg` 传字典可实现"**不同列不同聚合**"，一次 `groupby` 顶三次单独计算；`as_index=False`（或 `.reset_index`）让分组键回到普通列，便于后续拼接与导出。

</details>

### 2. 用 `pivot_table` 把上题结果变成"行=城市、列=渠道"的二维表，并加上总计。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
pivot = df.pivot_table(index='city', columns='channel', values='customer',
aggfunc='sum', fill_value=0, margins=True)
print(pivot)
```

参数作用：`index` 竖着排（每行一个城市）、`columns` 横着铺（每个渠道一列）、`values` 指定聚合的数值列、`aggfunc` 指定函数、`fill_value=0` 填补没有数据的交叉格、`margins=True` 输出行列总计。结果结构示意：

```text
channel 线下 线上 All
city
上海 150 120 270
北京 130 90 220
```

</details>

### 3. 算出"星期几上涨的比例"，用 `crosstab` 与 `pivot_table` 两种方式实现。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
import numpy as np, pandas as pd

# 公共准备
stock['week'] = pd.to_datetime(stock.index).weekday # 0=周一 … 6=周日
stock['posi_neg'] = np.where(stock['p_change'] > 0, 1, 0)

# 方式一：crosstab + 手动求比例
count = pd.crosstab(stock['week'], stock['posi_neg']) # 每星期几的涨/跌天数
row_sum = count.sum(axis=1).astype(np.float32) # 每个星期几的总天数
pro = count.div(row_sum, axis=0) # 逐行相除得到比例
print(pro)

# 方式二：pivot_table（一行搞定）
print(stock.pivot_table(values='posi_neg', index='week', aggfunc='mean'))

# 可视化
pro.plot(kind='bar', stacked=True); plt.show
```

关键点：① `pd.to_datetime(stock.index)` 把字符串索引转成时间索引才能取 `.weekday`；② `np.where(cond,1,0)` 把连续变量转 0/1 才能做交叉统计；③ `count.div(row_sum, axis=0)` 的 `axis=0` **不能省**——两个 Series 相除默认按列对齐，方向错了结果全是 NaN；④ 方式二利用了"0/1 变量的均值 = 1 的占比"这一性质。

</details>

## 6. 延伸阅读

- [Pandas 官方用户指南：Group by（split-apply-combine）](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Pandas 官方用户指南：Reshaping and pivot tables](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- [Pandas API：pandas.crosstab](https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html)
- [Pandas API：pandas.pivot_table](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html)
- [Pandas API：GroupBy.agg / transform / filter](https://pandas.pydata.org/docs/reference/groupby.html)

---

[⬅️ 返回数据处理目录](README.md)
