---
article_id: kp-ed55b252972de5e7
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-0f9e190924a9
learning_sourceId: 0f9e190924a9
learning_order: 8
learning_objective: 理解并验证：-Pandas数据清洗：可运行示例
---

# -Pandas数据清洗：可运行示例

> **学习目标**：能够解释「-Pandas数据清洗：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-NumPy数值计算](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)（`ndarray`、广播、`np.nan`、`np.where`）；会读写文件、了解 CSV/JSON 格式。
>
> **所属主题**：-Pandas数据清洗 · 可运行示例

## 本次只学这一点

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

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-Pandas数据清洗：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/06-Pandas数据清洗.md)
