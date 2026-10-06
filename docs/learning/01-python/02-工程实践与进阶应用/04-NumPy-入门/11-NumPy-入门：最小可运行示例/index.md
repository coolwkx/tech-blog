---
article_id: kp-ac557be24d79f262
learning_kind: article
learning_category: 01-python
learning_direction: practice
learning_topic: topic-a5477d7405c8
learning_sourceId: a5477d7405c8
learning_order: 10
learning_objective: 理解并验证：NumPy 入门：最小可运行示例
---

# NumPy 入门：最小可运行示例

> **学习目标**：能够解释「NumPy 入门：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。
>
> **所属主题**：NumPy 入门 · 最小可运行示例

## 本次只学这一点

```python
import time
import numpy as np

# ---------- 1) 属性 ----------
arr = np.arange(15).reshape(3, 5)
print(arr.shape, arr.ndim, arr.size, arr.dtype, arr.itemsize, arr.nbytes)
# (3, 5) 2 15 int64 8 120

# ---------- 2) list vs ndarray 性能：向量化把循环搬到 C 层 ----------
n = 2_000_000
py_list = list(range(n))
np_arr = np.arange(n)

t = time.perf_counter; sum(py_list); t_py = time.perf_counter - t
t = time.perf_counter; np.sum(np_arr); t_np = time.perf_counter - t
print(f"list: {t_py*1000:.2f}ms ndarray: {t_np*1000:.2f}ms 加速 {t_py/t_np:.1f}x")
# list: 11.71ms ndarray: 0.52ms 加速 22.5x

# ---------- 3) array 是拷贝，asarray 能省则省 ----------
a = np.array([1, 2, 3])
b = np.array(a) # 拷贝
c = np.asarray(a) # 已是 ndarray 且类型一致 → 原样返回
a[0] = 99
print(b, c) # [1 2 3] [99 2 3]
print(b is a, c is a) # False True

# ---------- 4) 视图 vs 拷贝：NumPy 最大的坑 ----------
base = np.arange(10)
view = base[2:5]
view[:] = -1
print("切片是视图 →", base) # [ 0 1 -1 -1 -1 5 6 7 8 9]

base2 = np.arange(10)
fancy = base2[[1, 3, 5]] # 花式索引 → 拷贝
fancy[:] = -1
print("花式索引是拷贝 →", base2) # 原数组不变

base3 = np.arange(10)
safe = base3[2:5].copy # 想要独立副本必须显式 copy
safe[:] = -1
print("显式 copy →", base3) # 原数组不变

# ---------- 5) reshape / flatten / ravel / T 的视图语义 ----------
x = np.arange(6)
r = x.reshape(2, 3)
print(np.shares_memory(x, r)) # True（reshape 只改元信息）
print(np.shares_memory(x, r.flatten)) # False（拷贝）
print(np.shares_memory(x, r.ravel)) # True（视图）
print(r.T)
# [[0 3]
# [1 4]
# [2 5]]

# ---------- 6) 广播机制三条规则 ----------
print(np.array([[0], [1], [2], [3]]) + np.array([1, 2, 3])) # (4,1)+(3,) → (4,3)
print(np.array([[1], [2], [3]]) * np.array([[10, 20, 30, 40]])) # (3,1)*(1,4) → (3,4)
try:
 np.array([[1, 2, 3, 2, 1, 4], [5, 6, 1, 2, 3, 1]]) + np.array([[1, 2, 3, 4], [3, 4, 5, 6]])
except ValueError as e:
 print("不兼容:", e)
 # operands could not be broadcast together with shapes (2,6) (2,4)

# ---------- 7) axis 的含义：axis=k 就是让第 k 维消失 ----------
m = np.arange(12).reshape(3, 4)
print(m.sum(axis=0).shape, m.sum(axis=0)) # (4,) [12 15 18 21] 每列
print(m.sum(axis=1).shape, m.sum(axis=1)) # (3,) [ 6 22 38] 每行
print(m.cumsum(axis=1))
# [[ 0 1 3 6]
# [ 4 9 15 22]
# [ 8 17 27 38]]

# ---------- 8) 学生成绩统计 ----------
score = np.array([[80, 89, 86, 67, 79],
 [78, 97, 89, 67, 81],
 [90, 94, 78, 67, 74],
 [91, 91, 90, 67, 69]])
print("各科最高:", np.max(score, axis=0)) # [91 97 90 67 81]
print("最高分所在学生下标:", np.argmax(score, axis=0)) # [3 1 3 0 1]
print("各科平均:", np.mean(score, axis=0))
print("各科标准差:", np.round(np.std(score, axis=0), 2))

# ---------- 9) 布尔索引 + where + all/any ----------
t = score[:, :4].astype(float)
t[t > 85] = 85 # 布尔索引赋值（原地）
print(np.where(t >= 80, 1, 0)) # 三元运算
print(np.where(np.logical_and(t > 60, t < 85), 1, 0)) # 复合条件
print(np.all(score > 60), np.any(score > 95)) # True True

# ---------- 10) nan：不能用 == 判断 ----------
d = np.array([1.0, np.nan, 3.0])
print(np.nan == np.nan) # False
print(np.isnan(d)) # [False True False]
print(d.sum, np.nansum(d), np.nanmean(d)) # nan 4.0 2.0

# ---------- 11) 逐元素乘 vs 矩阵乘（最容易被搞混的一组） ----------
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print("逐元素 A*B:\n", A * B) # [[ 5 12] [21 32]]
print("矩阵乘 A@B:\n", A @ B) # [[19 22] [43 50]]
print(np.array_equal(np.multiply(A, B), A * B)) # True ← multiply 不是矩阵乘法！
print(np.array_equal(np.dot(A, B), A @ B)) # True

# ---------- 12) 常用创建函数与可复现随机 ----------
print(np.linspace(1, 10, 10, endpoint=False)) # [1. 1.9 2.8 ... 9.1]
print(np.logspace(1, 3, 5)) # [10. 31.62 100. 316.23 1000.]
print(np.unique(np.array([[1, 2, 1], [2, 3, 4]]))) # [1 2 3 4]

rng = np.random.default_rng(42) # 固定种子 → 结果可复现
print(rng.integers(1, 10, size=5)) # [1 7 6 4 4]
print(np.round(rng.normal(0, 1, 5), 3)) # [ 0.941 -1.951 -1.302 0.128 -0.316]
```

真实运行输出（节选，NumPy 2.3.5）：

```text
(3, 5) 2 15 int64 8 120
list: 11.71ms ndarray: 0.52ms 加速 22.5x
[1 2 3] [99 2 3]
False True
切片是视图 → [ 0 1 -1 -1 -1 5 6 7 8 9]
花式索引是拷贝 → [0 1 2 3 4 5 6 7 8 9]
显式 copy → [0 1 2 3 4 5 6 7 8 9]
True
False
True
不兼容: operands could not be broadcast together with shapes (2,6) (2,4)
(4,) [12 15 18 21]
(3,) [ 6 22 38]
nan != nan: False
nan 4.0 2.0
```

**关键点说明**

| 位置 | 关键点 |
| --- | --- |
| `arr.itemsize` 为 8 | 64 位平台默认整数是 `int64`；是 `int32`（4 字节），要一致需显式 `dtype=np.int32` |
| `np.array` vs `np.asarray` | 前者总拷贝，后者"能省则省"；用 `b is a` 可以直接验证 |
| `view[:] = -1` | **切片是视图**，改它会污染原数组 —— NumPy 最常见的 bug 来源 |
| `fancy[:] = -1` | 花式索引 / 布尔索引返回拷贝，改它安全 |
| `np.shares_memory` | 判断两个数组是否共享内存的官方工具，比猜可靠 |
| `reshape` 后共享内存为 `True` | reshape 只改 shape/strides 元信息，不搬数据 |
| `flatten` vs `ravel` | 前者一定拷贝，后者尽量返回视图；要独立数据用 `flatten` |
| `(4,1) + (3,)` → `(4,3)` | 广播规则 1（补 1）+ 规则 2（长度为 1 的维度可扩展） |
| `sum(axis=0)` 结果 `(4,)` | 少了第 0 维，说明"把行压掉、得到每列的和" |
| `t[t > 85] = 85` | 布尔索引赋值是**原地**修改，常用来做截断/置零 |
| `np.nan == np.nan` 为 `False` | 判 NaN 只能用 `np.isnan`；聚合用 `np.nansum` / `np.nanmean` |
| `np.multiply` 等于 `A * B` | **不是矩阵乘法**，注释有误，必须纠正 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「NumPy 入门：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../01-python/05-工程化与实践/11-NumPy入门.md)
