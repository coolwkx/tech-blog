---
article_id: kp-781afb78b21bbeb0
learning_kind: article
learning_category: 02-data
learning_direction: practice
learning_topic: topic-91025ff85275
learning_sourceId: 91025ff85275
learning_order: 8
learning_objective: 理解并验证：端到端骨架：从取数到交付
---

# 端到端骨架：从取数到交付

> **学习目标**：能够解释「端到端骨架：从取数到交付」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：本目录 [01-Linux基础命令](../../../../../02-data/01-Linux与SQL/01-Linux基础命令.md) ～ [10-RFM用户价值分析实战](../../../../../02-data/04-分析实战/10-RFM用户价值分析实战.md) 的全部内容；会安装软件、使用命令行与 Jupyter。
>
> **所属主题**：-数据分析项目流程 · 可运行示例

## 本次只学这一点

```python
# ================= 阶段 0：环境与显示设置 =================
import time
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 中文
mpl.rcParams['axes.unicode_minus'] = False # 负号
pd.set_option('display.max_columns', None)
# 用过之后可恢复：pd.reset_option('all')

# ================= 阶段 1：数据获取（三种典型来源） =================
# df = pd.read_csv('./data/1960-2019全球GDP数据.csv', encoding='gbk') # CSV
# sheet_datas = pd.read_excel('./data/sales.xlsx',
# sheet_name=['2015','2016','2017','2018','会员等级']) # Excel 多 sheet -> dict
# from sqlalchemy import create_engine # MySQL
# engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8')
# df = pd.read_sql('select * from orders where order_date >= "2024-01-01"', engine)

np.random.seed(7) # 本例用内存数据演示
n = 1500
df = pd.DataFrame({
'会员ID': np.random.choice(np.arange(2001, 2031), n),
'订单号': np.arange(5000000000, 5000000000 + n),
'提交日期': pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365, n), unit='D'),
'订单金额': np.round(np.random.lognormal(5, 1.1, n), 1),
})
df.loc[df.sample(20, random_state=1).index, '订单金额'] = np.nan # 造缺失

# ================= 阶段 2：数据探索（EDA）六必做 =================
print('【规模】', df.shape) # 多少行多少列
print('【结构】'); df.info # 每列 dtype + 非空数量 + 内存
print('【样例】'); print(df.head)
print('【缺失】'); print(df.isnull.sum) # 每列缺失个数
print('【分布】'); print(df.describe) # 均值 / 分位数 / 极值
print('【类别】'); print(df['会员ID'].value_counts.head)

plt.figure(figsize=(10, 5))
plt.hist(df['订单金额'].dropna, bins=40, color='steelblue', alpha=0.8)
plt.title('订单金额分布'); plt.xlabel('金额'); plt.ylabel('频数')
plt.show

# ================= 阶段 3：数据清洗 =================
data = df.copy
data = data.dropna # 缺失比例很低，直接删除
data = data[data['订单金额'] > 1] # 与业务确认："无意义的优惠券订单"才剔除
data['订单金额'] = pd.to_numeric(data['订单金额'], errors='coerce') # 类型转换
data['提交日期'] = pd.to_datetime(data['提交日期'])
data = data.drop_duplicates(subset=['订单号']) # 去重
print('清洗前后条数:', len(df), '->', len(data))

# ================= 阶段 4：特征计算（以 RFM 为例） =================
deadline = data['提交日期'].max # 截止时间节点
data['recency_days'] = (deadline - data['提交日期']).dt.days
rfm = data.groupby('会员ID', as_index=False).agg(
r=('recency_days', 'min'), # 最近一次消费距截止日的天数
f=('订单号', 'count'), # 订单次数
m=('订单金额', 'sum'), # 消费总额
)
print(rfm.describe)

# ================= 阶段 5：分析与分群 =================
dist = rfm[['r', 'f', 'm']].describe
r_bins = [-1, dist.loc['25%', 'r'], dist.loc['75%', 'r'], dist.loc['max', 'r'] + 1]
f_bins = [0, 2, 5, dist.loc['max', 'f'] + 1] # F 分布极端，用业务经验值
m_bins = [0, dist.loc['25%', 'm'], dist.loc['75%', 'm'], dist.loc['max', 'm'] + 1]

rfm['r_label'] = pd.cut(rfm['r'], bins=r_bins, labels=[3, 2, 1]) # R 倒序
rfm['f_label'] = pd.cut(rfm['f'], bins=f_bins, labels=[1, 2, 3])
rfm['m_label'] = pd.cut(rfm['m'], bins=m_bins, labels=[1, 2, 3])
assert rfm[['r_label', 'f_label', 'm_label']].isnull.sum.sum == 0, '存在未分箱数据，检查边界'

rfm['rfm_wscore'] = (rfm['r_label'].astype(int) * 0.2 + rfm['f_label'].astype(int) * 0.2
+ rfm['m_label'].astype(int) * 0.6)
tmp = rfm[['r_label', 'f_label', 'm_label']].astype(str)
rfm['rfm_group'] = tmp['r_label'] + tmp['f_label'] + tmp['m_label']

group_stat = rfm['rfm_group'].value_counts.rename_axis('rfm_group').reset_index(name='users')
group_stat['ratio'] = (group_stat['users'] / group_stat['users'].sum).round(4)
print(group_stat.head(10))

# ================= 阶段 6：可视化与结论 =================
group_stat.head(10).set_index('rfm_group')['users'].plot(kind='bar', title='Top10 群体规模')
plt.xlabel('RFM 组合'); plt.ylabel('人数'); plt.tight_layout; plt.show
# 结论（示例写法，必须可执行、可量化）
# 1. 规模最大的群体是 212/211/112 一类"可发展/可挽回群体"，占比超过 X%，
# 基数大，必须靠系统批量运营（礼品兑换、签到、免运费）。
# 2. 333 群体人数极少但三维度全优，应倾斜 VIP 资源。
# 3. R 分位最低的一组（久未购买）占比 Y%，建议优先启动短信/邮件召回。

# ================= 阶段 7：交付物落地 =================
rfm.to_excel('./output/rfm_result.xlsx', index=False)
group_stat.to_excel('./output/rfm_group_stat.xlsx', index=False)
# from sqlalchemy import create_engine # 写库供其他模型复用
# engine = create_engine('mysql+pymysql://root:123456@localhost:3306/rfm_db?charset=utf8')
# rfm.to_sql('rfm_table', engine, index=False, if_exists='append')
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「端到端骨架：从取数到交付」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/04-分析实战/11-数据分析项目流程.md)
