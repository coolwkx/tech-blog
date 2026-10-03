> **一句话总结**：数据清洗就是把"原始文件里的脏数据"变成"可信、结构整齐的 DataFrame"——链路是**读进来 → 看清结构 → 定位与改写 → 补缺失 → 合并**；`Series`（一维）与 `DataFrame`（二维）两个对象加上"索引对齐"这条隐含规则，贯穿每一步。
> **前置知识**：[05-NumPy数值计算](05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
> **学完能做到**：1. 用 `read_csv/read_json/read_sql` 把各种来源的数据读成 DataFrame 并指定索引与列；2. 用 `loc/iloc/drop/assign/replace/drop_duplicates` 精准增删改查；3. 系统处理缺失值（含 `'?'` 这类伪缺失标记），并用 `concat/merge` 把多份数据拼成一张表。

## 1. 核心概念

### 1.1 两个核心数据结构

Pandas 是最流行的**结构化数据**工具集，用于数据清洗、处理与分析；底层基于 NumPy（快）、有专门的缺失值 API、分组聚合能力强。适用于"数据量大到 Excel 卡顿但仍是单机数据"的场合，以及数据仓库 ETL 中的清洗环节。

| 对象 | 维度 | 组成 | 类比 |
| --- | --- | --- | --- |
| `Series`（s 对象） | 一维 | `values`（`ndarray`）+ `index`（索引标签） | Excel 的**一列** |
| `DataFrame`（df 对象） | 二维 | 行索引 `index`（axis=0）+ 列索引 `columns`（axis=1） | Excel 的**一张表** |

层级关系：`DataFrame` → 多个 `Series` → 每个 `Series` 分"索引列"（索引名、索引值、索引下标）与"数据列"（列名、列值）。

### 1.2 Pandas 数据类型

| Pandas 类型 | 说明 | 对应 Python 类型 |
| --- | --- | --- |
| `object` | 字符串 / 混合类型 | `str` |
| `int64` / `float64` | 整数 / 浮点数 | `int` / `float` |
| `datetime64[ns]` | 日期时间 | `datetime` |
| `timedelta64[ns]` | 时间差 | `timedelta` |
| `category` | 分类类型，**内存更小、运算更快** | 无原生类型 |
| `bool` / `NaN` | 布尔 / 空值 | `bool` / `None` |

查看方式：`s.dtypes`、`df.dtypes`、`df.info`（`Series` 没有 `info`）。

### 1.3 索引设置三件套

| 方法 | 作用 | 关键参数 |
| --- | --- | --- |
| `df.index = 新列表` | 整体替换行索引 | 必须**等长整体替换**，不能只改其中一个 |
| `df.set_index(keys, drop=True)` | 用某列（或多列）作为新索引 | `drop=True` 该列不再保留为普通列；传列表得 MultiIndex |
| `df.reset_index(drop=False)` | 索引还原为普通列，生成新自增下标 | `drop=True` 则直接丢弃原索引 |

### 1.4 三种定位方式（务必分清）

| 写法 | 依据 | 顺序 | 示例 |
| --- | --- | --- | --- |
| `df['列名']` | 列名 | **先列后行** | `df['open']['2018-02-27']` |
| `df.loc[行标签, 列标签]` | **标签**（名字） | **先行后列** | `df.loc['2018-02-27':'2018-02-22', 'open']` |
| `df.iloc[行下标, 列下标]` | **位置下标**（整数） | **先行后列** | `df.iloc[:3, :5]` |

不支持的写法：`df['2018-02-27']['open']`（顺序反了）、`df[:1, :2]`（`[]` 不支持逗号同时切行列）。

### 1.5 数据读写

| 方向 | API | 常用参数 |
| --- | --- | --- |
| 读 CSV | `pd.read_csv(path, sep=',', usecols=[...], index_col=0, encoding='gbk')` | `usecols` 只读指定列；`index_col` 指定索引列；中文文件常需 `encoding='gbk'` |
| 写 CSV | `df.to_csv(path, columns=[...], header=True, index=False, mode='w')` | **`index=False` 才不把索引写成单独一列**；`mode='a'` 为追加 |
| 读 MySQL | `pd.read_sql('表名或select语句', engine)` | 需先 `create_engine` |
| 写 MySQL | `df.to_sql('表名', engine, index=False, if_exists='append')` | `if_exists` 取 `fail`/`replace`/`append` |
| 读/写 JSON | `pd.read_json(path, orient='records', lines=True)` / `df.to_json(...)` | `lines=True` 表示每行一个 JSON 对象 |

```python
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8')
# └类型┘└─驱动─┘ └账号┘└密码┘ └───主机:端口/库名───┘ └──编码──┘
```

`read_json` 的 `orient` 取值：`'split'`（index/columns/data 三部分分开）、**`'records'`（`[{列:值}, ...]`，最常用）**、`'index'`、`'columns'`（默认）、`'values'`。

### 1.6 增删改查速查

| 目的 | API | 注意 |
| --- | --- | --- |
| 加列 | `df['新列'] = 标量 / 等长列表 / Series / 表达式` | 列表长度必须等于行数 |
| 加列（链式） | `df.assign(新列=值或函数)` | 返回**新 df**；函数需接收 df 作参数 |
| 删行/删列 | `df.drop([标签], axis=0/1)` | 默认删行；`axis=1` 删列；**默认返回新对象** |
| 删列（原地） | `del df['列']` | 永久删除，慎用 |
| 去重 | `df.drop_duplicates(subset=None, keep='first')` | `keep` 可取 `'first'/'last'/False` |
| Series 去重 | `s.drop_duplicates` / `s.unique` | 前者返回 Series，后者返回数组 |
| 替换值 | `s.replace(旧, 新, inplace=False)` | **精确整值匹配**；默认不改原数据 |
| 条件查询 | `df[布尔条件]` / `df.query('表达式')` / `s.isin([...])` | 多条件用 `&`、`\|`，**必须加括号** |
| 取头尾 / 切片 | `df.head(n)` / `df.tail(n)` / `df[起:止:步长]` | 默认 5 行；切片顾头不顾尾 |
| 排序 / 排名 | `df.sort_values(by, ascending=)` / `df.sort_index` / `s.rank(method=)` | 多字段传列表；`rank` 的 `pct=True` 返回百分比排名 |

### 1.7 缺失值处理的决策表

| 情况 | 判断 | 处理方式 |
| --- | --- | --- |
| 以 `np.nan` 标记 | `df.isnull` / `pd.notnull(df)` | ① 删除 `df.dropna`；② 填充 `df.fillna(value, inplace=True)` |
| 以其他标记表示（`'?'`、`0`） | 先确认业务含义 | **第一步** `df.replace('?', np.nan)` 转标准 NaN，**第二步**再按上面处理 |

常用判断组合：`df.isnull.sum`（每列缺失个数）、`df.isnull.any(axis=1)`（每行是否有缺失）、`np.any(pd.isnull(df))`（整表是否有缺失）、`np.all(pd.notnull(df))`（是否全部非空）。

### 1.8 数据合并

| API | 场景 | 关键参数 |
| --- | --- | --- |
| `pd.concat([df1, df2], axis=0)` | 纵向摞起来（union） | `axis=0` 按行、`axis=1` 按列；`ignore_index=True` 重建索引 |
| `pd.merge(left, right, how=, on=)` | 按共同键横向关联（join） | `how` 取 `inner`/`left`/`right`/`outer`；`on` 指定键 |

| `how` | 对应 SQL | 结果集 |
| --- | --- | --- |
| `'left'` | `LEFT OUTER JOIN` | 只用左表的键 |
| `'right'` | `RIGHT OUTER JOIN` | 只用右表的键 |
| `'outer'` | `FULL OUTER JOIN` | 两表键的并集 |
| `'inner'` | `INNER JOIN` | 两表键的交集（**默认**） |

## 2. 可运行示例

```python
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', None); pd.set_option('display.max_columns', None)

# ================= 1. Series 与 DataFrame 创建 =================
s1 = pd.Series([1, 2, 3]) # 默认自增索引
s2 = pd.Series([1, 2, 3], index=['A', 'B', 'C']) # 自定义索引
s3 = pd.Series({'A': 1, 'B': 2, 'C': 3}) # 字典创建
s4 = pd.Series(np.arange(6), index=list('ABCDEF'))
print(s4.index, s4.values(), s4['A'])

df1 = pd.DataFrame({'日期': ['2021-08-21', '2021-08-22', '2021-08-23'],
'温度': [25, 26, 50], '湿度': [81, 50, 56]}) # 字典+列表
df2 = pd.DataFrame([('2021-08-21', 25, 81), ('2021-08-22', 26, 50)],
columns=['日期', '温度', '湿度'],
index=['row_1', 'row_2']) # 列表+元组+自定义索引

score = np.random.randint(40, 100, (10, 5)) # 10 人 5 门课
data = pd.DataFrame(score, columns=['语文', '数学', '英语', '政治', '体育'],
index=['同学' + str(i) for i in range(10)])
print(data.shape, data.index, data.columns, data.T.shape)
print(data.head(3), data.tail(3), data.dtypes, data.info)

# ================= 2. 索引设置 =================
df = pd.DataFrame({'month': [1, 4, 7, 10], 'year': [2012, 2014, 2013, 2014],
'sale': [55, 40, 84, 31]})
print(df.set_index('month')) # 某列成为索引
print(df.set_index(['year', 'month'])) # 多级索引
print(df.set_index('month').reset_index) # 索引还原为列
print(df.set_index('month').reset_index(drop=True)) # 索引直接丢弃
# data.index[3] = '学生_3' # 错误！索引必须整体替换
data.index = ['学生_' + str(i) for i in range(data.shape[0])]

# ================= 3. 定位：三种方式对比 =================
stock = pd.DataFrame(
{'open': [23.53, 22.80, 22.88], 'close': [24.16, 23.53, 22.82]},
index=['2018-02-27', '2018-02-26', '2018-02-23'])
print(stock['open']['2018-02-27']) # 先列后行
print(stock.loc['2018-02-27':'2018-02-23', 'open']) # 先行后列（标签）
print(stock.iloc[:3, :2]) # 先行后列（下标）
# stock['2018-02-27']['open'] # 错误：顺序反了
# stock[:1, :2] # 错误：[] 不支持逗号切行列

# ================= 4. 读写：CSV / MySQL / JSON =================
# df_csv = pd.read_csv('./data/stock_day.csv', usecols=['open', 'close'], index_col=0)
stock.to_csv('./data/test.csv', columns=['open'], index=False) # index=False 才不多出一列
# from sqlalchemy import create_engine
# engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8')
# df.to_sql('test_pdtosql', engine, index=False, if_exists='append')
# print(pd.read_sql('select name, AKA from test_pdtosql', engine))
# js = pd.read_json('./data/Sarcasm_Headlines_Dataset.json', orient='records', lines=True)
# js.to_json('./data/test.json', orient='records', lines=True)

# ================= 5. 增删改查 =================
gdp = pd.DataFrame({'country': ['中国', '美国', '日本', '英国', '法国'],
'year': [2019] * 5,
'GDP': [14342903, 21433226, 5081770, 2827113, 2715518]})
df5 = gdp.copy
df5['new_col_1'] = 33 # 固定值（广播到每行）
df5['new_col_2'] = [1, 2, 3, 4, 5] # 等长列表
df5['new_col_3'] = df5['GDP'] / 10000 # 表达式
df5 = df5.assign(rank_no=df5['GDP'].rank(ascending=False),
is_asia=lambda d: d['country'].isin(['中国', '日本']))
print(df5.drop([0, 2])) # 删行（按索引标签）
print(df5.drop(['new_col_1'], axis=1)) # 删列
# del df5['new_col_1'] # 原地永久删除列，慎用

dup = pd.concat([gdp, gdp], ignore_index=True) # 造重复数据（append 已废弃）
print(dup.shape, dup.drop_duplicates.shape) # (10,3) -> (5,3)
print(dup['country'].drop_duplicates, dup['country'].unique)

# replace：不加 inplace 不会改动原数据
print(gdp['country'].replace('日本', '扶桑'))
gdp2 = gdp.copy; gdp2['country'].replace('日本', '扶桑', inplace=True)
print(gdp2)

# 查询
print(gdp['country'], gdp[['country', 'GDP']], gdp[0:2]) # 取列 / 多列 / 切片
print(gdp[gdp['GDP'] > 5000000]) # 布尔索引
print(gdp.query('GDP > 5000000')) # query
print(gdp.query('country == "中国" or country == "日本"'))
print(gdp[gdp['country'].isin(['中国', '日本'])]) # isin
print(gdp.sort_values(['GDP'], ascending=False)) # 排序

# rank：四种 method 的差异（成绩 100, 90, 90, 80）
rk = pd.DataFrame({'姓名': ['小明', '小美', '小强', '小兰'], '成绩': [100, 90, 90, 80]})
for m in ['average', 'min', 'max', 'dense']:
    rk[f'rank_{m}'] = rk['成绩'].rank(method=m, ascending=False)
    print(rk) # 100 都是 1；两个 90 分别为 2.5/2.5、2/2、3/3、2/2；80 为 4/4/4/3

    # ================= 6. 缺失值处理 =================
    movie = pd.DataFrame({'Title': ['A', 'B', 'C', 'D'],
    'Rating': [8.1, np.nan, 7.5, 9.0],
    'Revenue': [100.0, 200.0, np.nan, 400.0],
    'Metascore': [70, 80, 60, np.nan]})
    print(movie.isnull, movie.isnull.sum) # 逐格判断 / 每列缺失个数
    print(movie.isnull.any(axis=1)) # 哪些行有缺失
    print(np.any(pd.isnull(movie)), np.all(pd.notnull(movie))) # True / False
    print(movie.dropna) # 删掉任何含 NaN 的行
    print(movie.dropna(how='all')) # 只删全为 NaN 的行

    m1 = movie.copy # 填充：按列选择不同策略
    m1['Rating'] = m1['Rating'].fillna(m1['Rating'].mean)
    m1['Revenue'] = m1['Revenue'].fillna(m1['Revenue'].median)
    m1['Metascore'] = m1['Metascore'].fillna(0)
    print(m1)

    m2 = movie.copy # 批量填充：每列用其均值
    for col in m2.columns:
        if not np.all(pd.notnull(m2[col])):
            m2[col] = m2[col].fillna(m2[col].mean)
            print(m2)

            wis = pd.DataFrame({'col': ['5', '?', '3', '?', '7']}) # 伪缺失标记
            wis = wis.replace(to_replace='?', value=np.nan) # 先转标准 NaN
            print(wis.dropna) # 再统一处理

            # ================= 7. 合并：concat 与 merge =================
            top = pd.DataFrame({'城市': ['上海', '北京'], '温度': [18, 3]})
            bottom = pd.DataFrame({'城市': ['广州', '深圳'], '温度': [26, 27]})
            print(pd.concat([top, bottom], ignore_index=True)) # 行变多
            print(pd.concat([top, top], axis=1)) # 列变多

            left = pd.DataFrame({'key1': ['K0', 'K0', 'K1', 'K2'], 'key2': ['K0', 'K1', 'K0', 'K1'],
            'A': ['A0', 'A1', 'A2', 'A3']})
            right = pd.DataFrame({'key1': ['K0', 'K1', 'K1', 'K2'], 'key2': ['K0', 'K0', 'K0', 'K0'],
            'B': ['B0', 'B1', 'B2', 'B3']})
            print(pd.merge(left, right, on=['key1', 'key2'])) # inner（默认）
            print(pd.merge(left, right, how='left', on=['key1', 'key2'])) # 左表全集
            print(pd.merge(left, right, how='right', on=['key1', 'key2'])) # 右表全集
            print(pd.merge(left, right, how='outer', on=['key1', 'key2'])) # 两侧并集
```

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `drop`/`replace`/`fillna` 后原数据没变 | 打印原 df 还是老数据 | 这些方法**默认返回新对象** | 接收返回值 `df = df.drop(...)`，或显式 `inplace=True` |
| `df.drop([...])` 想删列却删了行 | 报 `labels not found` 或结果不对 | `drop` 默认 `axis=0`（删行） | 删列传 `axis=1` |
| `to_csv` 后读回来多一列 `Unnamed: 0` | 列数变多 | `to_csv` 默认 `index=True` | 写文件加 `index=False` |
| 用 `df.append()` | 报 `AttributeError` | `DataFrame.append()` 已在 Pandas 2.0 移除 | 改用 `pd.concat([df1, df2], ignore_index=True)` |
| `del df['列']` 后重复运行报错 | 第二次执行 `KeyError` | `del` 是**原地永久删除** | 需要可重复执行就用 `drop` 并接收返回值 |
| `df['a']['b'] = 值` 报 `SettingWithCopyWarning` | 有时改了、有时没改 | 链式索引可能作用在**临时副本**上 | 用 `.loc` 一步到位：`df.loc['b', 'a'] = 值` |
| 用 `==` 判断缺失值 | 筛选结果永远为空 | `np.nan != np.nan` 恒为真 | 用 `df.isnull` / `df.notnull` |
| 用 `'?'` 直接 `dropna` | 一条都没删掉 | `dropna` 只识别标准缺失标记 | 先 `replace('?', np.nan)` 再 `dropna` |
| `merge` 后行数暴涨 | 结果远大于任一输入 | 关联键在某侧**不唯一**，产生笛卡尔积 | 合并前先验证键唯一性（`is_unique`/`duplicated`），必要时先去重 |
| `read_csv` 读中文乱码 | 中文变问号 | 默认按 UTF-8 解码，而文件是 GBK | 加 `encoding='gbk'`（或 `'utf-8-sig'`） |
| `sort_values` 后索引还是乱的 | 索引与新顺序不匹配 | 排序只重排行，不重排索引 | 需要连续新索引时加 `.reset_index(drop=True)` |

## 4. 面试问答

### Q1：`loc` 和 `iloc` 有什么区别？为什么 `df['a']['b']` 会报警告？

<details><summary>参考答案</summary>

| 维度 | `df.loc` | `df.iloc` |
| --- | --- | --- |
| 依据 | **标签**（索引名、列名） | **整数下标**（位置） |
| 切片是否含末端 | **包含**（`loc['a':'c']` 取 a、b、c） | **不包含**（`iloc[0:3]` 取 0、1、2） |
| 典型场景 | 索引是有业务含义的日期、ID | 想按"第几行第几列"取值 |

两者都是"**先行后列**"，与 `df['列']['行']` 的"先列后行"相反。

`df['a']['b'] = 1` 是**链式索引**：第一步 `df['a']` 可能返回副本（copy）而非视图（view），第二步在副本上赋值，原 DataFrame 不会变化，于是 Pandas 抛 `SettingWithCopyWarning` 提醒"这次赋值可能没生效"。正确写法是合并成一次索引：

```python
df.loc['b', 'a'] = 1 # 推荐：一次定位到单元格
df.loc[df['a'] > 10, 'b'] = 1 # 条件赋值也用 loc
```

同时建议避免 `inplace=True`：它返回 `None`，会打断链式调用（`df.fillna(0, inplace=True).mean` 直接报错），也不利于回溯。

</details>

### Q2：处理缺失值有哪几种思路？遇到 `'?'` 或 `0` 这种"伪缺失"怎么办？

<details><summary>参考答案</summary>

**第一步永远是识别标记方式**：若以 `np.nan` 标记，可直接处理；若以 `'?'`、`'NULL'`、`-1`、`0` 等业务自定义标记出现，**必须先 `df.replace('?', np.nan)` 转成标准 NaN**，否则 `dropna` 和 `fillna` 都识别不到。

**第二步选择"删"还是"填"**：

| 策略 | API | 适用条件 |
| --- | --- | --- |
| 删除行 | `df.dropna`（可配 `how='all'`、`thresh=n`、`subset=[...]`） | 缺失比例很低（如 < 5%），样本充足 |
| 删除列 | `df.dropna(axis=1)` | 某列缺失极高（如 > 80%），几乎无信息 |
| 均值/中位数填充 | `s.fillna(s.mean)` / `s.fillna(s.median)` | 数值型；**有极端值时优先中位数** |
| 众数填充 | `s.fillna(s.mode[0])` | 类别型字段 |
| 固定值填充 | `s.fillna(0)` / `s.fillna('未知')` | 有业务含义的缺省状态 |
| 前向/后向填充 | `s.ffill` / `s.bfill` | 时间序列，用相邻时点补 |

**判断依据**：缺失比例、字段重要性、以及**缺失是否随机**。如果缺失本身携带信息（如"没填收入"往往对应低收入人群），直接删或填均值都会引入偏差，更稳妥的是**额外加一个"是否缺失"的布尔指示列**，把缺失信息显式建模。

</details>

### Q3：`pd.concat` 和 `pd.merge` 有什么区别？

<details><summary>参考答案</summary>

- **`pd.concat` 是"拼接"（union）**：把多个结构相似的表沿某个轴接起来，**不需要关联键**。`axis=0`（默认）纵向堆叠，行数相加，列名取并集，缺失处填 NaN；`axis=1` 横向拼接，按索引对齐；`ignore_index=True` 丢弃原索引生成新的自增索引。
- **`pd.merge` 是"关联"（join）**：按**共同的键**把两张表的列横向组合，本质是 SQL JOIN。`how` 决定结果集：`inner` 交集（默认）、`left` 左表全集、`right` 右表全集、`outer` 并集；`on` 指定关联键，两侧键名不同时用 `left_on`/`right_on`。

一句话区分：**要"摞起来"用 `concat`，要"对起来"用 `merge`**。

实务提醒：`merge` 前务必检查关联键唯一性。若左表某键出现 3 次、右表 4 次，`inner merge` 会产生 3×4=12 行（笛卡尔积），结果行数暴涨且聚合指标被重复计数。用 `df['key'].is_unique` 或 `df['key'].duplicated.sum` 先验证，是数据清洗的标准动作；合并时还可用 `validate='many_to_one'` 让基数不匹配直接报错。

</details>

## 5. 自测题

### 1. 创建行索引为 `A`~`D`、列为 `name`/`score` 的 DataFrame，并新增 `level` 列：score ≥ 90 为 `'优'`，≥ 60 为 `'良'`，否则 `'差'`。

<details><summary>参考答案</summary>

```python
import pandas as pd, numpy as np
df = pd.DataFrame({'name': ['甲', '乙', '丙', '丁'], 'score': [95, 82, 58, 90]},
index=list('ABCD'))

df['level'] = np.where(df['score'] >= 90, '优', np.where(df['score'] >= 60, '良', '差'))
df['level2'] = pd.cut(df['score'], bins=[-1, 60, 90, 100], labels=['差', '良', '优'])
def grade(x): return '优' if x >= 90 else ('良' if x >= 60 else '差')
df['level3'] = df['score'].apply(grade)
print(df)
```

要点：分段赋值优先用 `pd.cut`（向量化、可读、可复用）；`bins` 的**最左边界要小于最小值**，因为 `pd.cut` 默认**左开右闭** `(a, b]`，等于最小值的点会落不进任何区间。

</details>

### 2. `df.to_csv('a.csv')` 之后读回来多了一列 `Unnamed: 0`，为什么？怎么解决？

<details><summary>参考答案</summary>

因为 `to_csv` 的 `index` 参数默认为 `True`，会把行索引也写成一个真实数据列，但表头行没有这一列的名字（索引本身无名），读取时 Pandas 自动命名为 `Unnamed: 0`。

```python
df.to_csv('a.csv', index=False) # 方式一（推荐）：写就不带索引
pd.read_csv('a.csv', index_col=0) # 方式二：读时把第一列当索引
```

补充：`to_csv` 常用参数还有 `columns=[...]`（只导出指定列）、`header=False`（不写表头）、`mode='a'`（追加）、`encoding='utf-8-sig'`（让 Excel 打开不乱码）。

</details>

### 3. 用 `merge` 合并订单表和商品表后，行数从 1000 变成 3000，可能是什么原因？如何排查和解决？

<details><summary>参考答案</summary>

**最可能的原因：关联键在某一侧不唯一，产生多对多笛卡尔积。** 若商品表某商品 ID 重复 3 次，对应每一行订单都会与 3 行商品匹配，行数被放大 3 倍。

**排查**：

```python
print(df_order['product_id'].is_unique)
print(df_prod['product_id'].duplicated.sum)
print(df_prod['product_id'].value_counts.head)
```

**解决**：

1. **先去重再合并**：明确业务口径后对商品表按 `product_id` 去重（`drop_duplicates(subset='product_id', keep='last')`）——通常维度表应当唯一；
2. **加 `validate` 防御**：`pd.merge(a, b, on='id', validate='many_to_one')`，基数关系不满足时直接报错；
3. **改用 `map`/`join`**：若只是补一个商品名称，`df_order['product_id'].map(prod_name_series)` 更高效且不会放大行数；
4. **确认口径**：若确实是一对多（一个订单含多个商品），3000 行可能正确——此时应先在订单明细层聚合，再与商品表关联。

核心原则：**合并前先想清楚"键的基数关系"（一对一/一对多/多对多），并用 `is_unique` 或 `validate` 显式表达出来。**

</details>

## 6. 延伸阅读

- [Pandas 官方用户指南：IO tools（read_csv / to_csv / read_json / to_sql）](https://pandas.pydata.org/docs/user_guide/io.html)
- [Pandas 官方用户指南：Indexing and selecting data（loc / iloc）](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Pandas 官方用户指南：Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Pandas 官方用户指南：Merge, join, concatenate and compare](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Pandas API：DataFrame.drop_duplicates / replace / assign](https://pandas.pydata.org/docs/reference/frame.html)

---

[⬅️ 返回数据处理目录](README.md)
