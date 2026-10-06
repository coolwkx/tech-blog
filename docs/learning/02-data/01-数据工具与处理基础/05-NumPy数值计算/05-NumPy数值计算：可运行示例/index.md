---
article_id: kp-001b5bd951243ab6
learning_kind: article
learning_category: 02-data
learning_direction: foundations
learning_topic: topic-c0a892e8e152
learning_sourceId: c0a892e8e152
learning_order: 4
learning_objective: 理解并验证：-NumPy数值计算：可运行示例
---

# -NumPy数值计算：可运行示例

> **学习目标**：能够解释「-NumPy数值计算：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
>
> **所属主题**：-NumPy数值计算 · 可运行示例

## 本次只学这一点

```python
import numpy as np

# ================= 1. 属性与形状 =================
arr = np.arange(15).reshape(3, 5) # 0~14 排成 3 行 5 列
print(arr.shape, arr.ndim, arr.size, arr.itemsize, arr.dtype) # (3,5) 2 15 8 int64
print(np.shape(arr), np.ndim(arr), np.size(arr), type(arr)) # 函数写法等价

# ================= 2. 创建数组 =================
print(np.zeros((3, 4))) # 3 行 4 列，float64
print(np.ones((2, 3, 4)).shape) # 三维：2 个 3x4
print(np.zeros_like(np.ones((2, 2)))) # 形状同前者的全 0 数组

a = np.array([[1, 2, 3], [4, 5, 6]])
a2 = np.asarray(a) # 浅拷贝：与 a 共享内存
a2[0, 0] = 999
print(a) # [[999,2,3],[4,5,6]] —— a 被改动，证明共享内存
a[0, 0] = 1 # 还原
print(np.array(a) is a) # False：np.array 是深拷贝

print(np.linspace(0, 100, 11)) # 按"数量"：11 个点，含 100
print(np.arange(10, 50, 2)) # 按"步长"：10,12,...,48
print(np.logspace(0, 2, 3)) # 按"指数"：1, 10, 100
print(np.random.rand(3, 2)) # [0,1) 均匀分布，3x2
print(np.random.randint(1, 100, size=(4, 3)))# [1,100) 随机整数
print(np.random.uniform(-1, 5, size=(3, 4))) # [-1,5) 均匀分布
print(np.random.normal(0, 1, 100).mean) # 标准正态，均值≈0

# ================= 3. 索引与切片：先行后列 =================
m = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print(m[0, 1]) # 2 —— 第 1 行第 2 列（索引从 0 开始）
print(m[0:2, :]) # 前两行的所有列
print(m[:, 1:3]) # 第 2、3 列的所有行
print(m[0, 1:3]) # [2 3]
t = np.array([[[1, 2, 3], [4, 5, 6]], [[12, 3, 34], [5, 6, 7]]])
print(t[0, 0, 1]) # 2 —— 三维：先"层"，再行，再列

# ================= 4. 形状修改：reshape / resize / T =================
x = np.arange(9)
print(x.reshape(3, 3)); print(x) # reshape 返回视图，x 本身不变
y = np.arange(9); y.resize((3, 3), refcheck=False) # 原地修改，要求元素个数一致
print(y)
z = np.array([[1, 2, 3], [4, 5, 6]])
print(z.T) # [[1 4] [2 5] [3 6]] —— 行列互换

# ================= 5. 类型修改与去重 =================
f = np.array([1.1, 2.2, 3.3, 4.4, 5.5])
i32 = f.astype(np.int32) # 截断小数部分（不四舍五入）
print(f.dtype, i32.dtype, i32) # float64 int32 [1 2 3 4 5]
print(np.unique(np.array([[1, 2, 3, 4], [3, 4, 5, 6]]))) # [1 2 3 4 5 6]

# ================= 6. 逻辑运算、布尔索引与 np.where =================
score = np.random.randint(40, 100, (10, 5)) # 10 名同学 5 门课
test_score = score[6:, 0:5] # 最后 4 名同学
print(test_score > 60) # 布尔矩阵
test_score[test_score > 60] = 1 # 布尔索引赋值
print(test_score)
print(np.all(score[0:2, :] > 60)) # 前两名是否全及格
print(np.any(score[0:2, :] > 90)) # 前两名是否有 90 分以上

temp = score[:4, :4]
print(np.where(temp > 60, 1, 0)) # 三元运算
print(np.where(np.logical_and(temp > 60, temp < 90), 1, 0)) # 大于 60 且小于 90
print(np.where(np.logical_or(temp > 90, temp < 60), 1, 0)) # 大于 90 或小于 60

# ================= 7. 统计运算：axis 是核心 =================
temp = score[:4, 0:5]
print('各科最高分 :', np.max(temp, axis=0)) # 沿列：每列一个结果，长度=列数
print('各科最低分 :', np.min(temp, axis=0))
print('各科平均分 :', np.mean(temp, axis=0))
print('各科中位数 :', np.median(temp, axis=0))
print('各科标准差 :', np.std(temp, axis=0))
print('各科方差 :', np.var(temp, axis=0))
print('各科极差 :', np.ptp(temp, axis=0))
print('最高分是谁 :', np.argmax(temp, axis=0)) # 返回下标
print('每人总分 :', np.sum(temp, axis=1)) # 沿行：每人一个结果，长度=行数
print('全班总和 :', np.sum(temp)) # 不指定 axis，统计全部元素
print(np.cumsum(np.arange(12).reshape(3, 4))) # 展平后累加，返回一维

# ================= 8. 数组间运算与广播 =================
print(np.array([[1, 2, 3]]) + 1) # 标量运算：作用到每个元素
print(np.array([1, 2, 3]) * 3) # [3 6 9]

arr1 = np.array([[0], [1], [2], [3]]) # shape (4,1)
arr2 = np.array([1, 2, 3]) # shape (3,)
print(arr1 + arr2) # (4,3)：(4,1) 与 (1,3) 逐维兼容
# [[1 2 3] [2 3 4] [3 4 5] [4 5 6]]

try: # 不兼容：2x6 与 2x4，最后一维 6!=4 且都不为 1
 np.array([[1,2,3,2,1,4],[5,6,1,2,3,1]]) + np.array([[1,2,3,4],[3,4,5,6]])
except ValueError as e:
 print('广播失败:', e)

# ================= 9. 逐元素乘法 vs 矩阵乘法 =================
p = np.array([[1, 2, 3], [4, 5, 6]])
q = np.array([[1, 2, 3], [4, 5, 6]])
print(p * q, np.multiply(p, q)) # 逐元素相乘，要求形状相同
x2 = np.array([[1, 2, 3], [4, 5, 6]]) # 2x3
y2 = np.array([[6, 23], [-1, 7], [8, 9]]) # 3x2
print(x2.dot(y2), np.dot(x2, y2)) # 2x2：左列数 = 右行数

# ================= 10. 内置函数与排序 =================
r = np.random.randn(2, 3)
print(np.ceil(r), np.floor(r), np.rint(r)) # 向上取整 / 向下取整 / 四舍五入
print(np.isnan(r), np.abs(np.array([-1, 2, -3]))) # 判 NaN / 绝对值

s = np.array([1, 2, 34, 5])
print(np.sort(s)); print(s) # 返回副本，s 不变
s.sort(); print(s) # 原地排序 -> [1 2 5 34]
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-NumPy数值计算：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../02-data/02-NumPy与Pandas/05-NumPy数值计算.md)
