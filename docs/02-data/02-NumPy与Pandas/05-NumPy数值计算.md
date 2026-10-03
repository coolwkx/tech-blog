> **一句话总结**：NumPy 的核心是一个**同类型、内存连续**的 N 维数组 `ndarray`，它用"整块内存 + C 语言循环"换来了比 Python 列表快一个数量级的运算；掌握 `shape`/`axis` 两个概念和**广播机制**三条规则，就掌握了 NumPy 的 80%。
> **前置知识**：Python 基础（列表、元组、字典、lambda、`import`）；了解"矩阵"的基本概念即可，无需线性代数基础。
> **学完能做到**：1. 用 `np.array/zeros/ones/arange/linspace/random` 按需造出正确形状与 dtype 的数组；2. 熟练用切片、布尔索引、`np.where` 完成条件筛选与替换，并说清 `axis=0/1` 的统计方向；3. 判断两个数组能否运算（广播），并区分 `*` 逐元素乘法与 `dot` 矩阵乘法。

## 1. 核心概念

### 1.1 NumPy 是什么，为什么快

NumPy（Numerical Python）是开源科学计算库，**用于快速处理任意维度的数组**，核心对象是 `ndarray`（N-dimensional array），描述"**相同类型** items 的集合"。与原生 `list` 的效率对比（实测：1 亿个随机数求和）：

| 方式 | 耗时（Wall time） | 说明 |
| --- | --- | --- |
| Python `sum(list)` | **1.13 s** | 逐个取出 Python 对象、解引用、调用 `__add__` |
| `np.sum(ndarray)` | **134 ms** | 连续内存 + C 循环 + 向量化 |

| 快的原因 | 说明 |
| --- | --- |
| 内存块风格 | `ndarray` 所有元素类型相同，数据地址**连续**，批量操作无需寻址跳转；`list` 存的是**指针**，元素对象散落在堆上，是"分离式存储" |
| 向量化/并行运算 | 一次操作作用到整个数组，省掉显式循环；多核时自动并行 |
| 底层 C 实现、释放 GIL | 数组运算不受 Python 逐行执行与全局解释器锁的限制 |

代价：`ndarray` 要求元素**同构**，通用性不如 `list`，但在数值计算场景下这个约束正好换来性能。

### 1.2 ndarray 的属性

| 属性 | 含义 | 示例（`arr = np.arange(15).reshape(3,5)`） |
| --- | --- | --- |
| `ndarray.shape` | 维度的元组 | `(3, 5)` |
| `ndarray.ndim` | 维数（轴的个数） | `2` |
| `ndarray.size` | 元素总个数 | `15` |
| `ndarray.itemsize` | 单个元素占用的字节数 | `8`（int64） |
| `ndarray.dtype` | 元素类型 | `int64` |

属性也有等价函数写法：`np.shape(arr)`、`np.ndim(arr)`、`np.size(arr)`；类型本身是 `<class 'numpy.ndarray'>`。

### 1.3 dtype 常用类型

| 类型 | 描述 | 简写 |
| --- | --- | --- |
| `np.bool_` | 布尔，1 字节 | `'b'` |
| `np.int8` | −128 ~ 127 | `'i1'` |
| `np.int16` | −32768 ~ 32767 | `'i2'` |
| `np.int32` | −2³¹ ~ 2³¹−1 | `'i4'` |
| `np.int64` | −2⁶³ ~ 2⁶³−1（**整数默认**） | `'i8'` |
| `np.uint8` | 无符号，0 ~ 255 | `'u1'` |
| `np.float16` | 半精度：符号 1 + 指数 5 + 尾数 10 | `'f2'` |
| `np.float32` | 单精度：符号 1 + 指数 8 + 尾数 23 | `'f4'` |
| `np.float64` | 双精度：符号 1 + 指数 11 + 尾数 52（**小数默认**） | `'f8'` |
| `np.complex64/128` | 复数，两个 32/64 位浮点表示实部虚部 | `'c8'/'c16'` |
| `np.object_` | 任意 Python 对象 | `'O'` |
| `np.bytes_` / `np.str_` | 定长字节串 / Unicode 串 | `'S'` / `'U'` |

> 历史上还有 `np.string_` 与 `np.unicode_`，它们**已被弃用并在 NumPy 2.x 中移除**。新代码请直接写 `np.bytes_`、`np.str_`，或用 `dtype='S12'`、`dtype='U12'`。区别：`S`（bytes）只支持 ASCII，`U`（str）支持 Unicode。

### 1.4 创建数组的常用函数

| 函数 | 作用 | 关键点 |
| --- | --- | --- |
| `np.array(obj, dtype=)` | 从列表/元组等创建 | **深拷贝**，与原数据独立 |
| `np.asarray(obj, dtype=)` | 从已有数组创建 | **浅拷贝**，输入已是 ndarray 且 dtype 一致时直接返回原对象 |
| `np.ones(shape)` / `np.zeros(shape)` | 全 1 / 全 0 | 默认 dtype 为 float64 |
| `np.ones_like(a)` / `np.zeros_like(a)` | 形状与 `a` 相同的全 1 / 全 0 | 省去手写 shape |
| `np.empty(shape)` | 只分配内存、**不初始化** | 内容是内存残留值，不是"随机数" |
| `np.arange(start, stop, step)` | 等差，**按步长** | 类似 `range`，不含 stop |
| `np.linspace(start, stop, num, endpoint)` | 等差，**按数量** | 默认含 stop（`endpoint=True`） |
| `np.logspace(start, stop, num, base)` | 等比，默认底数 10 | 生成 10^x |
| `np.random.rand(d0,...)` | [0.0, 1.0) 均匀分布浮点 | 参数是各维长度，不是 shape 元组 |
| `np.random.randn(d0,...)` | 标准正态分布（μ=0, σ=1） | — |
| `np.random.normal(loc, scale, size)` | 指定均值与标准差的正态分布 | `loc` 决定图形左右位置、`scale` 决定瘦高或矮胖 |
| `np.random.uniform(low, high, size)` | 指定区间的均匀分布 | — |
| `np.random.randint(low, high, size)` | 指定区间的整数 | 左闭右开 |

## 2. 可运行示例

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

## 3. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| `np.asarray` 改了原数组 | 修改"副本"时原数组也变了 | `asarray` 对 ndarray 输入返回**同一块内存** | 需要独立副本用 `np.array(a)` 或 `a.copy` |
| 把 `np.empty` 当随机数组 | 内容每次都不同，像随机数 | `empty` 只分配内存、**不初始化** | 需要确定内容用 `zeros`/`ones`/`random.*` |
| 混淆 `reshape` 与 `resize` | 原数组被改 / 报元素数量错误 | `ndarray.reshape` 返回视图**不改原数组**；`np.resize` 会**循环填充**成新数组；`ndarray.resize` 原地改且元素数必须一致 | 只想换看法用 `reshape`；要改原数组且元素数相同用 `arr.resize(shape)` |
| 以为 `reshape` 会转置 | 结果和预期行列对不上 | `reshape` 只按内存顺序重划形状，**不交换行列** | 需要行列互换用 `.T` |
| `axis` 记反 | 想"每列统计"却得到每行结果 | `axis=0` 沿列（跨行）运算；`axis=1` 沿行（跨列）运算 | 记"**axis 是被塌缩掉的轴**"：`axis=0` 表示第 0 维消失 |
| `arr + arr2` 报错 | `operands could not be broadcast together` | 形状不满足广播规则 | 先 `print(a.shape, b.shape)`，用 `.reshape`/`np.newaxis` 对齐形状 |
| 用 `*` 做矩阵乘法 | 形状对但数值不对 | `*` 是**逐元素乘法**（Hadamard 积） | 矩阵乘法用 `a.dot(b)` 或 `a @ b` |
| `dot` 报维度不匹配 | `shapes not aligned` | 未满足"左矩阵列数 = 右矩阵行数" | 检查 `a.shape[1] == b.shape[0]`，必要时转置 |
| 整数除法丢弃精度 | `astype(int)` 后小数没了 | `astype` 是**截断**而非四舍五入 | 先 `np.rint` 再 `astype` |
| 统计时把 NaN 算进去 | `mean` 结果是 `nan` | `np.mean` 遇 NaN 会污染整个结果 | 用 `np.nanmean`/`np.nansum` 等 `nan*` 系列，或先清洗 |
| 用 `np.string_` | 报 `AttributeError` | 该别名已在 NumPy 2.x 移除 | 改用 `np.bytes_`/`np.str_` 或 `dtype='S12'`/`'U12'` |

## 4. 面试问答

### Q1：`ndarray` 为什么比 Python 原生 `list` 快这么多？

<details markdown="1"><summary markdown="1">参考答案</summary>

以 1 亿个数求和为例，`list` 约 1.13 s，`ndarray` 约 134 ms，快了近 10 倍。原因有三层：

1. **内存布局不同（最根本）**：`list` 是"分离式存储"——列表里存的是指向 Python 对象的**指针**，每个 `int`/`float` 对象独立分配在堆上，地址不连续；`ndarray` 是"一体式存储"——所有元素**类型相同**，因此可以紧密排布在一块连续内存里，CPU 缓存命中率高，批量操作无需逐个寻址。
2. **省掉了装箱与解释器开销**：对 `list` 求和每次都要取出 Python 对象、判断类型、调用 `__add__`，全程由解释器逐条执行字节码；`ndarray` 的运算由编译好的 C 循环完成，一次调用处理整块数据（向量化）。
3. **释放了 GIL，支持并行**：NumPy 底层是 C 实现，数组运算期间不持有全局解释器锁，多核机器上可以并行计算。

代价是 `ndarray` 要求元素**同构**，不能像 `list` 那样混装字符串和数字；而在数值计算场景里这个约束恰好换来性能，所以 Pandas 也构建在 NumPy 之上。

</details>

### Q2：广播机制（broadcasting）的规则是什么？举例说明何时能广播、何时不行。

<details markdown="1"><summary markdown="1">参考答案</summary>

广播是 NumPy 在形状不同的数组之间做运算时，**虚拟地**把较小数组扩展到相同形状的机制（不会真正复制内存）。三条规则：

1. **补齐维度**：维数不同时，在维数较少的数组**前面补 1**；
2. **逐维比较**：从**最后一维**往前比，若该维长度**相等**或**其中一个为 1**则兼容；
3. **判定失败**：任何一维上两者长度既不同又都不为 1，则无法广播，抛 `ValueError`。

能广播：

```python
arr1 = np.array([[0], [1], [2], [3]]) # (4,1)
arr2 = np.array([1, 2, 3]) # (3,) -> 补成 (1,3)
print((arr1 + arr2).shape) # (4,3)
# 最后一维 1 vs 3 兼容；倒数第二维 4 vs 1 兼容
```

不能广播：

```python
# 2x6 与 2x4：最后一维 6 vs 4，既不相等又都不为 1 -> 失败
np.array([[1,2,3,2,1,4],[5,6,1,2,3,1]]) + np.array([[1,2,3,4],[3,4,5,6]])
# ValueError: operands could not be broadcast together with shapes (2,6) (2,4)
```

实务技巧：不确定时先 `print(a.shape, b.shape)`，再按"从右往左逐维比较"心算；也可用 `a[:, np.newaxis]` 主动插入长度为 1 的维度构造可广播形状。

</details>

### Q3：`np.resize`、`ndarray.reshape`、`ndarray.resize` 有什么区别？`axis=0` 和 `axis=1` 怎么记？

<details markdown="1"><summary markdown="1">参考答案</summary>

| 函数 | 类型 | 是否改原数组 | 元素个数不匹配时 |
| --- | --- | --- | --- |
| `ndarray.reshape(shape)` | 方法 | **否**，返回视图 | 报错 |
| `np.resize(a, shape)` | 函数 | 否，返回**新数组** | **循环重复原数据填充**（9 个元素变 2×5 会回头再取第一个） |
| `ndarray.resize(shape)` | 方法 | **是**，原地修改 | 报错（元素不足时行为受限） |
| `ndarray.T` | 属性 | 否，返回视图 | 不适用（行列互换） |

最容易被混为一谈的是 `np.resize` 与 `ndarray.resize`：前者"不够就循环复制"，后者"原地改形状且要求元素数一致"。

**axis 的记忆法**：`axis` 指定的是**要被塌缩掉的那个轴**。`axis=0` → 第 0 维（行）消失 → 结果是"每列一个值"（跨行汇总），长度等于列数；`axis=1` → 第 1 维（列）消失 → "每行一个值"（跨列汇总），长度等于行数；不写 `axis` → 展平后统计全部元素，返回标量。

```python
temp = np.random.randint(40, 100, (4, 5)) # 4 名学生 x 5 门课
np.max(temp, axis=0).shape # (5,) 每门课的最高分
np.max(temp, axis=1).shape # (4,) 每名学生的最高分
np.max(temp) # 标量，全班最高分
```

口诀：**axis=0 跨行看每列，axis=1 跨列看每行。**

</details>

## 5. 自测题

### 1. 创建 3 行 4 列、元素为 0~1 均匀分布随机数的数组，并输出 `shape`/`ndim`/`size`/`itemsize`/`dtype`。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
import numpy as np
a = np.random.rand(3, 4)
print(a.shape, a.ndim, a.size, a.itemsize, a.dtype)
# (3, 4) 2 12 8 float64
```

注意 `np.random.rand(3, 4)` 的参数是**各维长度**，不是 shape 元组；写 `np.random.rand((3,4))` 会报错。`np.random.uniform(0, 1, size=(3,4))` 也能达到同样效果。

</details>

### 2. `arr = np.arange(12).reshape(3, 4)`，求 `np.sum(arr, axis=0)` 与 `axis=1` 的结果并解释含义。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
arr = np.arange(12).reshape(3, 4)
# [[ 0 1 2 3]
# [ 4 5 6 7]
# [ 8 9 10 11]]
np.sum(arr, axis=0) # [12 15 18 21] —— 每列求和（跨行），长度=列数=4
np.sum(arr, axis=1) # [ 6 22 38] —— 每行求和（跨列），长度=行数=3
np.sum(arr) # 66 —— 全部元素求和
```

记忆：`axis` 是**被塌缩掉的轴**。`axis=0` 让行维消失，留下"每列一个和"；`axis=1` 让列维消失，留下"每行一个和"。

</details>

### 3. `a = np.array([[0],[1],[2],[3]])`（4×1）、`b = np.array([1,2,3])`（3），`a + b` 能否执行？结果形状是什么？

<details markdown="1"><summary markdown="1">参考答案</summary>

可以执行，结果形状是 **(4, 3)**。按广播规则推演：① `b` 维数少，**前面补 1** 变成 `(1, 3)`；② 从最后一维往前比：`a` 是 1、`b` 是 3 → 其中一个为 1，**兼容**；倒数第二维 `a` 是 4、`b` 是 1 → **兼容**；③ 逐维取较大值得到 `(4, 3)`。

```python
# [[1 2 3]
# [2 3 4]
# [3 4 5]
# [4 5 6]]
```

理解方式：`a` 沿列方向"复制"成 4×3，`b` 沿行方向"复制"成 4×3，再做逐元素加法。这只是逻辑扩展，NumPy 不会真的复制内存，所以广播几乎不增加开销。

</details>

### 4. `s = np.array([55, 78, 92, 45, 88])`，把大于 60 的元素替换为 100、其余为 0，写出两种实现。

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
import numpy as np
s = np.array([55, 78, 92, 45, 88])

t = s.copy # 写法一：布尔索引 + 分步赋值
t[t > 60] = 100
t[t <= 60] = 0
print(t) # [ 0 100 100 0 100]

r = np.where(s > 60, 100, 0) # 写法二：np.where（更简洁，且不改原数组）
print(r) # [ 0 100 100 0 100]
```

要点：`np.where(condition, x, y)` 等价于三元表达式 `x if condition else y`；写法一必须先 `copy`，否则会改动原数组。多条件组合用 `np.logical_and`/`np.logical_or`，或写 `(s > 60) & (s < 90)`——**括号不能省**，因为 `&` 的优先级高于比较运算符。

</details>

### 5. 下面代码输出什么？为什么？

```python
import numpy as np
x = np.array([[1, 2, 3], [4, 5, 6]])
y = np.array([[1, 2, 3], [4, 5, 6]])
print(x * y)
print(x.dot(y))
```

<details markdown="1"><summary markdown="1">参考答案</summary>

```python
print(x * y)
# [[ 1 4 9]
# [16 25 36]] —— 逐元素相乘（Hadamard 积），等价 np.multiply(x, y)

print(x.dot(y))
# ValueError: shapes (2,3) and (2,3) not aligned: 3 (dim 1) != 2 (dim 0)
```

`*` 是**逐元素乘法**，要求形状相同（或可广播），对应位置相乘；`.dot`/`np.dot`/`@` 是**矩阵乘法**，要求"左矩阵列数 = 右矩阵行数"。这里 `x`、`y` 都是 2×3，`3 != 2`，所以报维度不匹配。

要能相乘，需把 `y` 转置成 3×2：

```python
print(x.dot(y.T))
# [[14 32]
# [32 77]]
```

口诀：**星号逐个乘，dot 要 (m,n)·(n,p)。**

</details>

## 6. 延伸阅读

- [NumPy 官方文档：Absolute Beginners Guide](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [NumPy 官方文档：Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
- [NumPy 官方文档：Array creation routines](https://numpy.org/doc/stable/reference/routines.array-creation.html)
- [NumPy 官方文档：Statistics（统计函数）](https://numpy.org/doc/stable/reference/routines.statistics.html)
- [NumPy 官方文档：Random sampling](https://numpy.org/doc/stable/reference/random/index.html)

---

[⬅️ 返回数据处理目录](README.md)
