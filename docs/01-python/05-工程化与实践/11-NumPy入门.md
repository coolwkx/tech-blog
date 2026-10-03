# 11 NumPy 入门
> **一句话总结**：NumPy 的核心是 `ndarray` —— 一块**同类型、连续内存**的多维数据块，配合向量化和广播把"循环"从 Python 层搬到 C 层；理解 `axis`、视图 vs 拷贝、广播三条规则，后面的 Pandas 就只是"带标签的 ndarray"。
> **前置知识**：列表与嵌套结构（01 篇）、列表推导式（07 篇）、函数与类（02、03 篇）。

> 1. 熟练创建 `ndarray` 并读懂 `shape / ndim / size / dtype / itemsize`；
> 2. 正确使用索引、切片、布尔索引、花式索引，并分清哪些操作返回**视图**、哪些返回**拷贝**；
> 3. 用广播机制完成"列向量 × 行向量"这类矩阵级运算，并用 `axis` 参数做行列方向的聚合统计。

## 1. 核心概念
### 1.1 NumPy 解决了什么问题
| 维度 | Python 原生 list | NumPy ndarray |
| --- | --- | --- |
| 元素类型 | 任意（每个元素是一个对象指针） | **必须相同** |
| 内存布局 | 分离式存储（存指针，再跳到对象） | **一体式存储**（连续内存块） |
| 运算语义 | `a * 3` 是"列表重复 3 次" | `a * 3` 是"每个元素乘 3"（向量化） |
| 循环位置 | Python 解释器逐元素循环 | 底层 C 循环 |
| GIL | 受 GIL 限制 | 计算过程释放 GIL，可用多核 |
| 内存开销 | 大（每元素一个 PyObject） | 小（紧凑的原始字节） |

**实测（200 万个整数求和）**：
```text
list sum: 11.71ms ndarray sum: 0.52ms 加速 22.5x
```
**为什么快？** 三个原因：① 内存连续 → CPU 可以预取、缓存命中率高；② 类型统一 → 不需要逐个做类型判断和动态派发；③ 底层用 C 实现且不持有 GIL → 可以真正并行/向量化。

> 这也是"数据量与内存块风格"那两张图的真正含义：**list 是"指针数组 + 散落的对象"，ndarray 是"一整块同类型的字节"**。

### 1.2 核心属性
| 属性 | 含义 | 示例（`arr = np.arange(15).reshape(3, 5)`） |
| --- | --- | --- |
| `ndim` | 维数（轴的数量） | `2` |
| `shape` | 各维度长度的**元组** | `(3, 5)` |
| `size` | 元素总个数 | `15` |
| `dtype` | 元素类型 | `int64` |
| `itemsize` | 单个元素占的字节数 | `8` |
| `nbytes` | 整个数组占的字节数 = `size × itemsize` | `120` |
| `T` | 转置 | `(5, 3)` |

**形状怎么读？** `(3, 5)` = 3 行 5 列；`(4,)` = 长度 4 的一维数组（注意那个逗号，它不是 `(4)` 即标量）；`(2, 2, 3)` = 2 层、每层 2 行、每行 3 个元素。

> 注意：`itemsize` 取决于平台。本机是 64 位，默认整数是 `int64`（8 字节），而示例里是 `int32`（4 字节）。要跨平台对齐字节数就显式写 `dtype=np.int32`。

### 1.3 常用 dtype
| 类型 | 描述 | 简写 |
| --- | --- | --- |
| `np.bool_` | 布尔 | `'?'` |
| `np.int8 / int16 / int32 / int64` | 有符号整数（1/2/4/8 字节） | `'i1' / 'i2' / 'i4' / 'i8'` |
| `np.uint8 / uint16 / uint32 / uint64` | 无符号整数 | `'u1' / 'u2' / 'u4' / 'u8'` |
| `np.float16 / float32 / float64` | 半/单/双精度浮点 | `'f2' / 'f4' / 'f8'` |
| `np.complex64 / complex128` | 复数 | `'c8' / 'c16'` |
| `np.str_`（原 `np.unicode_`） | Unicode 字符串 | `'U'` |
| `np.bytes_`（原 `np.string_`） | 字节串（只支持 ASCII） | `'S'` |
| `np.object_` | 任意 Python 对象 | `'O'` |

**默认规则**：整数不指定就是 `int64`，小数不指定就是 `float64`（Windows 上整数曾默认 `int32`）。

> ⚠️ 用 `np.string_` / `np.unicode_`：这两个别名在 NumPy 2.0 已**移除**，现在应写 `np.bytes_` / `np.str_`。

### 1.4 创建数组的方法
| 分类 | 函数 | 说明 |
| --- | --- | --- |
| 从序列 | `np.array(obj, dtype=)` | **拷贝**数据，得到新数组 |
| 从序列 | `np.asarray(obj, dtype=)` | 若已是 ndarray 且 dtype 一致 → **不拷贝，直接返回原对象** |
| 全 0 / 全 1 | `np.zeros(shape, dtype)` / `np.ones(shape, dtype)` | 默认 `float64` |
| 形状参照 | `np.zeros_like(a)` / `np.ones_like(a)` | 与 `a` 同形状同类型 |
| 未初始化 | `np.empty(shape)` | 速度快，内容是内存残留，**必须先赋值** |
| 等差（指定步长） | `np.arange(start, stop, step)` | **包左不包右**，类似 `range` |
| 等差（指定个数） | `np.linspace(start, stop, num, endpoint=True)` | **默认包左包右** |
| 等比 | `np.logspace(start, stop, num, base=10)` | 生成 `base^start ~ base^stop` |
| 单位矩阵 | `np.eye(n)` / `np.identity(n)` | 对角线为 1 |
| 随机 | `np.random.rand(...)` / `uniform` / `randint` / `randn` / `normal` | 见下表 |

**`arange` vs `linspace` 的关键区别**：
```python
np.arange(10, 50, 2) # 指定"步长" → [10 12 14 ... 48]
np.linspace(0, 100, 11) # 指定"个数" → [0. 10. 20. ... 100.]
np.linspace(1, 10, 10, endpoint=False) # [1. 1.9 2.8 ... 9.1]，不包含终点
```
**随机数函数**：

| 函数 | 分布 | 示例 |
| --- | --- | --- |
| `np.random.rand(d0, d1, ...)` | `[0,1)` 均匀，参数是**形状** | `rand(3, 4)` |
| `np.random.uniform(low, high, size)` | `[low, high)` 均匀，可指定范围 | `uniform(-1, 5, (3, 4))` |
| `np.random.randint(low, high, size)` | 整数均匀，**包左不包右** | `randint(1, 100, (4, 3))` |
| `np.random.randn(d0, d1, ...)` | 标准正态 `N(0,1)` | `randn(3, 4)` |
| `np.random.normal(loc, scale, size)` | 任意正态，`loc`=均值、`scale`=标准差 | `normal(0, 1, 100)` |
| `np.random.default_rng(seed)` | **新版推荐入口** | `rng.integers(1, 10, 5)` |

> 可复现性：固定种子才能复现实验。新版 API 推荐 `rng = np.random.default_rng(42)`，然后用 `rng.random` / `rng.integers` / `rng.normal`；老式全局 `np.random.seed(42)` 仍然可用，但会污染全局状态。

### 1.5 索引与切片的三种玩法
| 玩法 | 写法 | 返回 | 是否共享内存 |
| --- | --- | --- | --- |
| 基础索引/切片 | `a[1:3]`、`a[:, 0]`、`a[0, 1]` | **视图 view** | ✅ **共享**，改一个另一个也变 |
| 布尔索引 | `a[a > 5]` | **拷贝 copy** | ❌ |
| 花式索引 | `a[[0, 2]]`、`a[[0, 1], [1, 2]]` | **拷贝 copy** | ❌ |

**这是 NumPy 最大的坑，必须实测记住**：
```python
base = np.arange(10)
view = base[2:5]
view[:] = -1
print(base) # [ 0 1 -1 -1 -1 5 6 7 8 9] ← 原数组被改了！

base2 = np.arange(10)
fancy = base2[[1, 3, 5]]
fancy[:] = -1
print(base2) # [0 1 2 3 4 5 6 7 8 9] ← 原数组没变
```
**为什么切片返回视图？** 因为设计目标是"零拷贝"：视图只额外保存 `shape / strides / 起始偏移`，不复制数据，所以 `a[::2]` 这种操作是 `O(1)` 的。要真正拿到独立副本必须显式 `a[2:5].copy`。

### 1.6 形状操作
| 操作 | 方法 | 是否改原数组 | 是否共享内存 |
| --- | --- | --- | --- |
| 改形状（返回新视图） | `a.reshape(2, 3)` | ❌ | ✅ 视图（前提是内存连续） |
| 改形状（原地） | `a.resize(2, 3)` / `a.shape = (2, 3)` | ✅ | — |
| 拉平（拷贝） | `a.flatten` | ❌ | ❌ 拷贝 |
| 拉平（视图） | `a.ravel` | ❌ | ✅ 尽量返回视图 |
| 行列互换 | `a.T` / `a.transpose` | ❌ | ✅ 视图 |
| 交换轴 | `a.swapaxes(0, 1)` | ❌ | ✅ 视图 |
| 自动推断维度 | `a.reshape(-1)` / `a.reshape(2, -1)` | ❌ | ✅ 视图 |
| 拼接 | `np.vstack` / `np.hstack` / `np.concatenate` | ❌ | ❌ 新数组 |
| 切分 | `np.split()` / `np.hsplit` / `np.vsplit` | ❌ | ✅ 视图 |
```python
x = np.arange(6)
r = x.reshape(2, 3)
print(np.shares_memory(x, r)) # True → reshape 是视图
print(np.shares_memory(x, r.flatten)) # False → flatten 是拷贝
```
> **`-1` 的含义**：让 NumPy 自己算这个维度。`m.reshape(-1)` 等价于拉平，`a.reshape(2, -1)` 表示"2 行，列数自己算"。这是处理"不确定行数"场景的常用技巧。

### 1.7 广播机制（broadcasting）三条规则
当两个数组形状不同时，NumPy 会尝试把它们"扩展"到相同形状再做逐元素运算：

| 规则 | 内容 |
| --- | --- |
| 规则 1 | 维度数不同时，在**维度少**的数组**前面**补 1，直到维度数一致 |
| 规则 2 | 从**最后一个维度**往前逐维比较：长度相等，或其中一个长度为 **1** → 兼容 |
| 规则 3 | 任何一维上长度既不同、又都不为 1 → **无法广播，抛 `ValueError`** |
```python
col = np.array([[0], [1], [2], [3]]) # shape (4, 1)
row = np.array([1, 2, 3]) # shape (3,) → 补成 (1, 3)
print(col + row)
# [[1 2 3]
# [2 3 4]
# [3 4 5]
# [4 5 6]] 两个维度都从 1 扩展到目标长度
```
**常见可广播 / 不可广播的组合**：

| A 形状 | B 形状 | 结果 |
| --- | --- | --- |
| `(4, 1)` | `(3,)` | ✅ → `(4, 3)` |
| `(3, 1)` | `(1, 4)` | ✅ → `(3, 4)` |
| `(2, 6)` | `(2, 4)` | ❌ 最后一维 6 vs 4 且都不为 1 |
| `(2, 1)` | `(8, 4, 3)` | ✅ → `(8, 4, 3)`（前面补 1 成 `(1, 2, 1)`，第 2 维 2 vs 4 ❌）—— 实际**报错**，因为 2≠4 且都不为 1 |
| `(4, 3)` | `(3,)` | ✅ → `(4, 3)`（补成 `(1,3)`） |

实测报错信息：
```text
ValueError: operands could not be broadcast together with shapes (2,6) (2,4)
```
> 广播的价值：**不用显式复制数据**就能完成"列广播到每列、行广播到每行"的运算。这让"每个学生成绩减去各科平均分"这种操作变成一行代码。

### 1.8 `axis` 参数：一句话记住
`axis=0` 表示"**沿着第 0 轴（行方向）压缩**"，结果里第 0 轴消失，也就是**对每一列**做统计：
```python
m = np.arange(12).reshape(3, 4)
m.sum(axis=0) # shape (4,) → [12 15 18 21]，每列之和
m.sum(axis=1) # shape (3,) → [6 22 38]，每行之和
```
| 操作 | 记忆方式 |
| --- | --- |
| `axis=0` | 跨行操作（把行"压掉"）→ 每列的统计量 |
| `axis=1` | 跨列操作（把列"压掉"）→ 每行的统计量 |
| 不写 `axis` | 对整个数组做统计，返回标量 |

**判断技巧**：看结果的 `shape`。`(3,4).sum(axis=0)` 得到 `(4,)` —— 少了的是第 0 维，所以是对列做统计。

### 1.9 统计、逻辑与 `where`
| 分类 | 函数 |
| --- | --- |
| 聚合 | `min` `max` `mean` `median` `std` `var` `sum` `prod` |
| 下标 | `argmin` `argmax` `argsort` |
| 累计 | `cumsum` `cumprod` |
| 判空 | `isnan` `isinf` `isfinite` |
| 逻辑 | `logical_and` `logical_or` `logical_not` `all` `any` |
| 三元 | `np.where(cond, x, y)` |
| 去重/排序 | `np.unique` `np.sort()` `np.argsort` |
```python
np.unique(np.array([[1, 2, 1], [2, 3, 4]])) # [1 2 3 4]，展平后去重，返回一维新数组
np.sort(a) # 返回排序后的新数组，原数组不变
a.sort() # 原地排序，返回 None
```
**`nan` 的三个反直觉行为**：

| 行为 | 结果 | 原因 |
| --- | --- | --- |
| `np.nan == np.nan` | `False` | IEEE 754 规定 NaN 不等于任何值（包括自身） |
| `np.isnan(x)` | 判断是否 NaN 的**唯一可靠方式** | 不能用 `==` |
| `arr.sum` 含 NaN | 结果是 `nan` | NaN 会"传染" |

解决：用 `np.nansum` / `np.nanmean` / `np.nanstd`，或先 `arr[~np.isnan(arr)]` 过滤。

> `np.where` 支持嵌套实现多分支，配合 `logical_and` / `logical_or` 表达复合条件：
> ```python
> np.where(np.logical_and(tmp > 60, tmp < 90), 1, 0)
> ```

### 1.10 `*` 与 `@`：最容易被搞混的一组运算
| 表达式 | 含义 | 前提 |
| --- | --- | --- |
| `A * B` | **逐元素相乘**（element-wise / Hadamard 积） | 形状可广播 |
| `np.multiply(A, B)` | 同上，就是 `*` 的函数形式 | 形状可广播 |
| `A @ B` | **矩阵乘法** | `A` 的列数 = `B` 的行数 |
| `np.dot(A, B)` | 矩阵乘法（一维时是点积） | 同上 |
| `np.matmul(A, B)` | 矩阵乘法（不允许标量，语义最严格） | 同上 |
```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
A * B # [[ 5 12] [21 32]] 逐元素
A @ B # [[19 22] [43 50]] 矩阵乘法
```
> ⚠️ **纠错**：的 `03_numpy常用函数介绍.ipynb` 里把 `np.multiply(arr1, arr1)` 注释成"**矩阵乘法**"，这是错的 —— `np.multiply` 是**逐元素乘法**，本机实测 `np.array_equal(np.multiply(A, B), A * B)` 为 `True`。真正的矩阵乘法要用 `np.dot` / `@` / `np.matmul`。这个错误在教学材料里很常见，考试和面试都会考。

## 2. 最小可运行示例

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

## 3. 常见坑
| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| 切片改动污染原数组 | "我没改原数组，它怎么变了" | 基础切片返回**视图**，共享内存 | `a[1:3].copy`，或先复制再操作 |
| 以为 `np.array` 和 `np.asarray` 一样 | 改了原数组，`asarray` 结果跟着变 | `asarray` 对 ndarray 直接返回原对象 | 需要独立数据用 `np.array(a)` 或 `a.copy` |
| 混淆 `*` 和 `@` | 矩阵运算结果完全不对 | `*` 是逐元素乘，`@`/`dot` 才是矩阵乘 | 矩阵乘用 `A @ B` 或 `np.dot(A, B)` |
| 把 `np.multiply` 当矩阵乘法 | 结果与手算不符 | `multiply` 是逐元素乘（此处写错了） | 用 `np.dot` / `@` |
| 广播形状记错 | `ValueError: operands could not be broadcast together` | 从最后一维比较，长度必须相等或为 1 | 写代码前先 `print(a.shape, b.shape)` |
| 以为所有形状都能广播 | 静默产生意料之外的巨大数组 | 广播会"虚拟扩展"，如 `(1000,1)*(1,1000)` 得到 100 万元素 | 注意内存放大；必要时用 `np.newaxis` 显式控制 |
| `axis` 理解反了 | 想求每行却求了每列 | `axis=0` 是跨行（压掉行） | 看结果的 `shape` 确认 |
| 没写 `axis` | 得到标量而不是向量 | 默认对整个数组聚合 | 明确写 `axis=0` / `axis=1` |
| `dtype` 不一致导致计算错误 | 整数相除得到整数、溢出 | `np.array([1,2,3]) / 2` 是浮点，但 `//` 是整除；`int8` 会溢出 | 显式指定 `dtype=np.float64`，注意整型溢出 |
| 用 `==` 判断 `nan` | 永远为 `False` | NaN 不等于自身 | `np.isnan(x)`，聚合用 `np.nansum` 等 |
| 含 `nan` 直接 `mean` | 结果变成 `nan` | NaN 会传染 | `np.nanmean` / 先过滤 |
| 用 `np.empty` 后忘赋值 | 出现随机垃圾值 | `empty` 不初始化内存 | 用 `zeros` / `ones`，或立刻全部赋值 |
| `np.zeros(3, 4)` 报错 | `TypeError: 'int' object is not iterable` | 形状必须传**元组** | `np.zeros((3, 4))` |
| `reshape` 元素数不匹配 | `ValueError: cannot reshape array of size 6 into shape (4,3)` | 新旧形状元素总数必须相同 | 用 `-1` 让 NumPy 推断：`a.reshape(2, -1)` |
| `resize` 与 `reshape` 混用 | 原数组被改了 | `resize` 是原地操作 | 只读场景用 `reshape` |
| `np.sort(a)` 后 `a` 没变却以为变了 | 以为排序失败 | `np.sort()` 返回新数组 | 需要原地用 `a.sort()`（注意它返回 `None`） |
| 一维数组当列向量用 | 广播结果形状不对 | `(3,)` 与 `(3,1)` 语义不同 | 用 `a[:, None]` 或 `a.reshape(-1, 1)` 显式升维 |
| 用 `np.random.seed` 却在别处随机 | 结果不可复现 | 全局随机状态被其他调用消耗 | 用 `rng = np.random.default_rng(42)` 独立生成器 |
| NumPy 2.0 后旧别名报错 | `AttributeError: module 'numpy' has no attribute 'string_'` | `np.string_` / `np.unicode_` 已移除 | 改用 `np.bytes_` / `np.str_` |

## 4. 面试问答
<details><summary>参考答案</summary>

**Q1：ndarray 为什么比 Python list 快？**

三个层面：

1. **内存布局**：list 是"指针数组 + 散落的 PyObject"，遍历时要不断解引用、跳内存；ndarray 是**一整块连续内存**，元素类型统一、大小固定，CPU 能预取、缓存命中率高，还能用 SIMD 指令批量处理。
2. **运算在 C 层**：ndarray 的运算由编译好的 C 循环完成，省掉了 Python 逐元素的解释器开销（类型检查、字节码派发、动态查找）。本机实测 200 万整数求和：list 11.71ms vs ndarray 0.52ms，约 **22.5 倍**。
3. **释放 GIL**：NumPy 的很多运算在 C 层显式释放 GIL，因此可以真正利用多核（"支持并行化运算"）。

代价是：ndarray 类型必须统一（混合类型会退化成 `object_` 类型，性能优势全失），且尺寸固定（`append` 需要重新分配整块内存）。

</details>

<details><summary>参考答案</summary>

**Q2：NumPy 的广播机制是什么？规则是什么？**

广播是"**在不复制数据的前提下，把形状不同的数组虚拟扩展成相同形状再做逐元素运算**"的机制。三条规则：

1. 维度数不同时，在**维度少**的数组**左侧（前面）**补 1；
2. 从**最后一维**开始逐维比较：长度相等，或其中一个为 **1** → 该维兼容；
3. 任何一维上长度既不同又都不为 1 → 抛 `ValueError: operands could not be broadcast together`。

例子：`(4,1) + (3,)` → 后者补成 `(1,3)`，两个维度都从 1 扩展到目标长度，结果 `(4,3)`；`(3,1) * (1,4)` → `(3,4)`；而 `(2,6) + (2,4)` 最后一维 6 vs 4 且都不为 1，直接报错。

实践意义：广播让"每行减去均值""列向量乘行向量生成网格"这类操作变成一行代码，不需要手动 `tile`/`repeat` 复制数据。但要注意**广播是虚拟的**：`(100000, 1) * (1, 100000)` 会真的生成 10¹⁰ 个元素，内存会爆，这种场景要先想清楚算法再写。

</details>

<details><summary>参考答案</summary>

**Q3：NumPy 里"视图"和"拷贝"有什么区别？哪些操作返回视图？**

**视图（view）** 是一个新的数组对象，但与源数组**共享底层数据缓冲区**，只保存自己的 `shape / strides / 起始偏移`。改视图会影响源数组，反之亦然。**拷贝（copy）** 会分配新内存并复制数据，两者完全独立。

| 返回视图 ✅ | 返回拷贝 ❌ |
| --- | --- |
| 基础切片 `a[1:5]`、`a[:, 0]` | 花式索引 `a[[0, 2]]` |
| `reshape` / `ravel` / `T` / `swapaxes` | 布尔索引 `a[a > 0]` |
| `np.split()` 系列 | `flatten` / `np.array(a)` / `a.copy` |
| `a.view` | 算术运算结果 `a + 1`、`np.sort(a)` |

验证工具是 `np.shares_memory(a, b)`。实践中要注意两点：① 切片赋值 `view[:] = -1` 会**原地**改数据，这是最常见的隐蔽 bug；② 视图持有对源数据的引用，一个大数组的切片视图会让整块内存无法释放（内存泄漏的常见原因），需要长期保留时用 `.copy`。

</details>

## 5. 自测题
<details><summary>1. `np.arange(6).reshape(2,3)` 和 `np.arange(6).reshape(2,3).flatten`，哪个与原数组共享内存？</summary>

`reshape` 的结果**共享内存**（是视图），`flatten` 的结果**不共享**（是拷贝）。而 `ravel` 与 `reshape` 一样尽量返回视图。
```python
x = np.arange(6)
r = x.reshape(2, 3)
print(np.shares_memory(x, r)) # True
print(np.shares_memory(x, r.flatten)) # False
print(np.shares_memory(x, r.ravel)) # True
```
选择依据：只想换形状看数据 → `reshape`（零拷贝）；需要一个能自由修改且不影响原数组的独立数组 → `flatten` 或 `.copy`。

</details>

<details><summary>2. `a = np.arange(10)`；`b = a[2:5]`；`b[0] = 100`，此时 `a` 是什么？怎样避免？</summary>

`a` 变成 `[ 0 1 100 3 4 5 6 7 8 9]`。因为 `b = a[2:5]` 是**基础切片**，返回视图，`b[0]` 就是 `a[2]`，改它就是改原数组。

避免方式：`b = a[2:5].copy`（显式拷贝），或使用会返回拷贝的索引方式（布尔索引、花式索引）。如果确实想改原数组，那就利用这个特性（例如 `a[2:5] = 0` 批量置零），但必须是有意为之。

</details>

<details><summary>3. `m = np.arange(24).reshape(2, 3, 4)`，`m.sum(axis=1)` 的形状是什么？</summary>

结果是 `(2, 4)`。`axis=1` 表示"把第 1 轴压掉"，原形状 `(2, 3, 4)` 去掉中间那一维，剩下 `(2, 4)`。含义是：对每个"层"的 3 行做列方向求和，得到 2 层 × 4 列。

一般规律：`m.sum(axis=k)` 的结果形状 = 原形状删掉第 k 维。可以记成"**axis=k 就是让第 k 维消失**"，这样再也不会记混 `axis=0` / `axis=1`。验证：
```python
m = np.arange(24).reshape(2, 3, 4)
print(m.sum(axis=1).shape) # (2, 4)
print(m.sum(axis=0).shape) # (3, 4)
print(m.sum(axis=2).shape) # (2, 3)
```
</details>

<details><summary>4. 学生的成绩矩阵 `score` 形状为 `(10, 5)`（10 个学生 × 5 门课），如何用一行代码得到"每个学生成绩减去该生平均分"（中心化）？</summary>
```python
centered = score - score.mean(axis=1, keepdims=True)
```
要点：

- `score.mean(axis=1)` 得到每个学生的平均分，形状 `(10,)`；
- 直接用 `(10,5) - (10,)` 会触发广播，把 `(10,)` 补成 `(1,10)`，与 `(10,5)` 的最后一维 5 vs 10 冲突而报错；
- 加 `keepdims=True` 让结果保持二维形状 `(10,1)`，广播时沿列方向展开，正是我们要的"每个学生减去自己的均值"。

如果无法加 `keepdims`，也可以用 `score - score.mean(axis=1)[:, None]`，效果相同。

</details>

<details><summary>5. 为什么 `np.nan == np.nan` 是 `False`？含 NaN 的数组怎么正确统计？</summary>

因为 NumPy 遵循 IEEE 754 浮点标准：NaN（Not a Number）表示"未定义/缺失"的结果，任何与 NaN 的比较（包括与自身）都返回 `False`。这是标准要求，不是 NumPy 的 bug。

正确做法：

1. 判断是否 NaN 用 `np.isnan(arr)`（不要用 `==`）；
2. 过滤用 `arr[~np.isnan(arr)]`；
3. 统计用 NaN-safe 版本：`np.nansum` / `np.nanmean` / `np.nanstd` / `np.nanmax`；
4. 转为 Pandas 后，`isnull` / `dropna` / `fillna` 是更常见的处理方式（见 12 篇）。
```python
d = np.array([1.0, np.nan, 3.0])
print(d.sum) # nan
print(np.nansum(d)) # 4.0
print(np.nanmean(d)) # 2.0
```
</details>

## 6. 延伸阅读
- NumPy 官方 · 快速入门（中文）：<https://numpy.org/doc/stable/user/absolute_beginners.html>
- NumPy 官方 · 广播机制详解（含图示与规则）：<https://numpy.org/doc/stable/user/basics.broadcasting.html>
- NumPy 官方 · 索引（基础/花式/布尔索引与视图语义）：<https://numpy.org/doc/stable/user/basics.indexing.html>
- NumPy 官方 · 数据类型对象 dtype 全表：<https://numpy.org/doc/stable/reference/arrays.dtypes.html>
- NumPy 官方 · 随机数生成（推荐使用 `default_rng`）：<https://numpy.org/doc/stable/reference/random/index.html>
- NumPy 2.0 迁移指南（`np.string_` 等已移除的别名）：<https://numpy.org/doc/stable/numpy_2_0_migration_guide.html>

---

[⬅️ 返回 Python 目录](README.md)
