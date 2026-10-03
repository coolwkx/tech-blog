# Python 数据模型与对象语义

> **一句话总结**：CPython 里一切皆对象，变量只是「名字到对象的绑定」；`len`、`for`、`in`、`[]`、`==` 都是「按类型查找 dunder 方法」的语法糖，理解这套协议就理解了 Python 行为的第一性原理。
>
> **前置知识**：基础语法（函数、类、列表/字典）；知道「引用」与「值」的区别会更顺。涉及 CPython 实现的地方都有标注，不需要 C 语言基础。
>

> 1. 用 `id` / `type` / 值三元组解释任意赋值、传参、拷贝、比较的实际行为；
> 2. 准确区分 `is` 与 `==`，说清小整数缓存与字符串 interning 的边界，并知道为什么不能依赖它们；
> 3. 自己实现 `__len__` / `__getitem__` / `__contains__` / `__eq__` / `__hash__`，并解释为什么调用 `len(x)` 而不是 `x.__len__`；
> 4. 一眼识别可变默认参数、`list * n`、浅拷贝、循环引用、可变对象做字典键这五类 bug。

---

## 1. 为什么需要它

初学 Python 时最反直觉的三个现象，来自同一个模型：

```python
a = [1, 2]
b = a
b += [3]
print(a) # [1, 2, 3] —— 改 b 为什么改了 a？

x = 257
y = 257
print(x is y) # True（写在这里），换个位置就可能是 False

class Bag:
 def __len__(self): return 3

print(len(Bag)) # 3 —— len 凭什么认识我的类？
```

把它们想成「变量是装值的盒子」无法解释；换成「变量是名字，名字指向对象，对象的类型决定它能做什么」，三条同时自然。这就是数据模型（data model）。

不掌握它的代价很具体：函数「偶尔」改坏调用者的列表；`def f(x, acc=[])` 让第二次调用带上第一次的数据；对象放进 `set` 后改了字段就再也查不到；面试被问 `is` 与 `==`，只能背「一个比地址一个比值」，追问到 `nan`、混合数值类型、`NotImplemented` 就答不上来。数据模型也是 Python 惯用法的地基：实现了正确的 dunder 协议，你的类就能无缝接入 `for`、`in`、`sorted`、`max`、解包等所有内建语法。

---

## 2. 核心思想

### 2.1 对象 = id + type + 值

| 要素 | 含义 | 获取方式 | 备注 |
| --- | --- | --- | --- |
| 身份 identity | 生命周期内唯一的标识 | `id(x)` | CPython 里是对象地址；对象回收后地址会被新对象复用，不能当长期唯一键 |
| 类型 type | 决定支持哪些操作、占用多少内存 | `type(x)` | 类型本身也是对象；运行时改类型需要 `__class__` 赋值等特殊手段 |
| 值 value | 对象承载的数据 | 各类型自有形式 | 可变对象的值可变、身份不变；不可变对象没有原地修改接口 |

关键推论：**`a = b` 不复制对象，只让两个名字指向同一个对象**。"不可变」指的是没有提供原地修改的接口，不是内存被锁住。

### 2.2 名字绑定，不是盒子

```text
x = [1, 2] x ──► ┌────────────────────┐
 │ list 对象 │ id=0x7f..., value=[1,2]
 └────────────────────┘
x += [3] x ──► 同一个 list 对象，id 不变，value=[1,2,3]（原地扩展）
```

所以 Python 只有一种传参方式：**传对象引用（call by object reference / call by sharing）**。函数参数是绑到同一对象上的新名字——在函数内**原地修改**（`lst.append()`）调用者看得见，**重新赋值**（`lst = [...]`）调用者看不见。

### 2.3 语法糖都是协议调用

`len`、`for`、`in`、`[]` 不检查「对象是不是 list」，而是在**类型**上查对应 dunder 再调用：

| 写法 | 实际走的协议 | 找不到时的回退 |
| --- | --- | --- |
| `len(x)` | `type(x).__len__(x)` | 无回退，抛 `TypeError`；返回值为负抛 `ValueError` |
| `x[k]` | `type(x).__getitem__(x, k)` | 无回退（赋值 `__setitem__`，删除 `__delitem__`） |
| `for i in x` | `iter(x)` → `type(x).__iter__(x)` | 旧式序列协议：反复 `__getitem__(0), __getitem__(1), ...` 直到 `IndexError` |
| `v in x` | `type(x).__contains__(x, v)` | 回退 `__iter__`，再回退 `__getitem__` |
| `x == y` | `type(x).__eq__(x, y)` | 返回 `NotImplemented` 则反射 `type(y).__eq__(y, x)`，最后回退 `is` |
| `x + y` | `type(x).__add__(x, y)` | 反射 `type(y).__radd__(y, x)` |
| `x += y` | `type(x).__iadd__(x, y)` | 退化为 `x = x + y`，即**重新绑定名字** |
| `hash(x)` | `type(x).__hash__(x)` | `object.__hash__` 由身份派生；类型里是 `None` 则抛 `TypeError` |
| `str(x)` | `__str__` | `__str__` 缺失时回退 `__repr__` |

**为什么用内置函数而不是直接调 dunder**：内置函数在**类型**上查找，并补上回退与校验；`x.__len__` 只是普通属性查找，会命中实例字典、拿不到旧协议能力。第 4.4 节有可运行证明。

---

## 3. 最小可运行示例

```python
import copy

# 1) 对象三元组：id / type / 值
a = [1, 2, 3]
b = [1, 2, 3]
print(type(a), a == b, a is b) # <class 'list'> True False

# 2) 名字绑定：alias 与 a 是同一个对象
alias = a
alias.append(4)
print(a) # [1, 2, 3, 4]

# 3) += 走 __iadd__（原地），+ 走 __add__（新建并重新绑定）
m = [1]
n = m
m += [2]
p = [1]
q = p
p = p + [2]
print(m, n, p, q) # [1, 2] [1, 2] [1, 2] [1]

# 4) 浅拷贝共享内层，深拷贝不共享
inner = [1]
shallow = copy.copy([inner])
deep = copy.deepcopy([inner])
inner.append(2)
print(shallow, deep) # [[1, 2]] [[1]]

# 5) 可变默认参数的正确写法：None 哨兵
def collect(value, acc=None):
 acc = [] if acc is None else acc
 acc.append(value)
 return acc

print(collect(1), collect(2)) # [1] [2]
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `a == b` / `a is b` | 值相等 / 身份相同 | `==` 对 list 逐元素比较，与是否同一对象无关 |
| `alias = a` | 新名字指向同一 list | 不是复制；`alias is a` 为 `True` |
| `alias.append(4)` | 原地修改 | 只有这一个对象，通过 `a` 也能看到变化 |
| `m += [2]` | `list.__iadd__` 原地扩展并返回 `self` | `n is m` 仍为 `True`，`n` 一起变成 `[1, 2]` |
| `p = p + [2]` | `list.__add__` 造新 list 再绑定给 `p` | `q` 仍指向旧对象 |
| `copy.copy([inner])` | 新外层 + 共享内层 | `inner` 变化会同时反映到 `shallow` |
| `copy.deepcopy([inner])` | 递归复制，内层也是新对象 | `inner` 变化不影响 `deep` |
| `acc=None` 哨兵 | `None` 是不可变单例，天然安全 | 写 `acc=[]` 会跨调用累积（见 4.5） |

---

## 4. 深入机制

### 4.1 `type` 与 `object` 的循环

```python
print(type(3) is int) # True
print(type(int) is type) # True
print(type(type) is type) # True
print(type(object) is type) # True
print(object.__bases__) # 
print(type.__bases__) # (<class 'object'>,)
print(isinstance(object, type)) # True
print(int.__mro__) # (<class 'int'>, <class 'object'>)
```

类也是对象，其类型是 `type`（自定义元类替换这个位置）；`object` 是所有类的基类且自身没有基类；`isinstance` 检查 `type(x)` 是否在目标类的 MRO 中，所以子类实例也算。判断类型优先用 `isinstance`，只有明确要排除子类时才写 `type(x) is C`。

### 4.2 名字绑定与 `dis` 字节码

```python
import dis

def total(seq):
    s = 0
    for item in seq:
        s += item
        return s

    dis.dis(total)
```

```text
 3 RESUME 0
 4 LOAD_CONST 1 (0)
 STORE_FAST 1 (s)
 5 LOAD_FAST 0 (seq)
 GET_ITER
 L1: FOR_ITER 7 (to L2)
 STORE_FAST 2 (item)
 6 LOAD_FAST_LOAD_FAST 18 (s, item)
 BINARY_OP 13 (+=)
 STORE_FAST 1 (s)
 JUMP_BACKWARD 9 (to L1)
 5 L2: END_FOR
 ... （后续为 POP_TOP / LOAD_FAST / RETURN_VALUE，略）
```

迭代对象来自 `GET_ITER`（即 `iter(seq)`），不是下标遍历。`s += item` 编译成 `BINARY_OP 13 (+=)`：运行时先试 `__iadd__`，不可用则退化为 `__add__`，然后**无条件 `STORE_FAST s`**——所以「`+=` 一定是原地修改」是错的，对不可变对象它等价于 `s = s + item`。含 `STORE` 的名字还会被编译器判定为局部变量，这正是下面这个高频错误的原因：

```text
counter = 0

def bump:
 counter += 1 # 含 STORE，counter 被判定为局部变量

try:
 bump
except UnboundLocalError as exc:
 print(type(exc).__name__, exc)
 # UnboundLocalError cannot access local variable 'counter' where it is not associated with a value
```

### 4.3 `==` 与 `is`：缓存与 interning 的真相

`is` 比较身份（CPython 比指针），不可重载；`==` 比较值，走 `__eq__`，失败则反射，最后回退到身份比较。**`is` 只用于单例**：`None`、`True`、`False`、`NotImplemented`、`Ellipsis`，以及自造哨兵（`_MISSING = object`）。

```python
import sys

print(1 == 1.0, 1 is 1.0) # True False
print({1: "a"}[1.0], {True: "x"}[1]) # a x —— 相等且哈希相同的键互相命中
nan = float("nan")
print(nan == nan, nan is nan) # False True（但 {nan: "v"}[nan] 能命中：字典先比身份）

print(int("256") is int("256")) # True —— 小整数缓存
print(int("257") is int("257")) # False
x = "hello"
y = "".join(["hel", "lo"])
print(x == y, x is y) # True False
print(sys.intern(y) is x) # True —— 显式驻留后是同一对象
```

| 对象 | 规则 | 能否依赖 |
| --- | --- | --- |
| 小整数 | CPython 预创建 `-5..256` 的 int 对象（`small_ints`），这些值在任何地方都是同一对象 | 不能，是实现细节 |
| 同一 code object 的常量 | `co_consts` 去重，所以同一段代码里 `"hi there" is "hi there"` 为 `True`，`10**3 is 1000` 也为 `True`（常量折叠） | 不能，位置一变就变 |
| 跨 code object 的字符串 | 只有「看起来像标识符」的常量在编译期被 intern（`hello`、`hello_world`、`x1` 是；`hello world`、`a-b`、`1.5` 不是，`sys.intern` 也不会自动生效） | 不能 |
| `sys.intern(s)` | 显式放入驻留表并返回表中的对象，适合大量重复键的解析器 | 可以，但要显式调用 |

实践结论：`if x is 5`、`if s is "abc"` 属于 bug 级写法（CPython 会给出 `SyntaxWarning`）。

### 4.4 特殊方法在类型上查找，不在实例上

```python
class Bag:
 def __init__(self, items): self._items = list(items)
 def __len__(self): return len(self._items)
 def __getitem__(self, index): return self._items[index]
 def __contains__(self, value): return value in self._items

bag = Bag([10, 20, 30])
print(len(bag), bag[1], 20 in bag) # 3 20 True
print(list(bag)) # [10, 20, 30] —— 没有 __iter__，靠 __getitem__ 旧协议

bag.__len__ = lambda: 999 # 挂到实例字典上
print(bag.__len__, len(bag)) # 999 3 —— 内置函数忽略实例属性
```

`len(bag)` 仍返回 `3`：`len` 走 C 层 `PyObject_Size` → `type(bag)` 的类型槽（`sq_length`），完全绕开实例 `__dict__`。由此得到三条实践规则：

- 特殊方法必须定义在**类**上，`self.__len__ = ...` 对内置函数无效；
- 内置函数提供回退：`iter(bag)` 在没有 `__iter__` 时退化为 `bag[0]`、`bag[1]`… 直到 `IndexError`，而 `bag.__iter__` 直接 `AttributeError`；
- 内置函数承担校验：`__len__` 返回负数抛 `ValueError: __len__ should return >= 0`，返回非整数抛 `TypeError`；没有长度语义的对象（如生成器）得到明确的 `TypeError: object of type 'generator' has no len`，而不是默默返回 `0`。

### 4.5 可变性、传参与默认参数

```python
def mutate(items): items.append("new") # 原地修改：调用者可见
def rebind(items): items = items + ["new"] # 重新绑定本地名：调用者不可见

data = [1]
mutate(data)
rebind(data)
print(data) # [1, 'new'] —— rebind 没生效

t = ([1], 2)
try: t[0] += [2] # 先 __iadd__ 成功，再 __setitem__ 失败
except TypeError as exc: print(type(exc).__name__, exc)
print(t) # ([1, 2], 2) —— 异常抛了，数据已经改了

def bad(value, acc=[]): # [] 在 def 执行时创建一次，存进 __defaults__
 acc.append(value); return acc

def good(value, acc=None):
 acc = [] if acc is None else acc
 acc.append(value); return acc

print(bad(1), bad(2), bad.__defaults__) # [1, 2] [1, 2] ([1, 2],) —— 共享同一个 list
print(good(1), good(2)) # [1] [2]
```

`t[0] += [2]` 是「半成功」的经典形态：展开为「取 `t[0]` → 原地 `extend` → 写回 `t[0]`」，第三步失败但第二步的副作用已发生。默认值是函数对象的属性（`__defaults__` / `__kwdefaults__`），随函数对象长生不死；只有不可变默认值（`None`、数字、字符串、元组、`frozenset`）才天然安全，`def f(x=time.time)` 同理只在定义时求值一次。

### 4.6 浅拷贝、深拷贝与 `list * n`

| 操作 | 外层 | 内层 | 循环引用 | 用途 |
| --- | --- | --- | --- | --- |
| `b = a` | 同一对象 | 共享 | 原样 | 起别名，不是拷贝 |
| `copy.copy(a)` / `list(a)` / `a[:]` | 新对象 | **共享** | 不修复 | 只需外层独立 |
| `copy.deepcopy(a)` | 新对象 | 递归新对象 | 靠 `memo` 修复成自洽的图 | 需要完全独立副本 |
| `[x] * n` | 新列表，n 个槽指向**同一个** `x` | 共享 | — | 只适合不可变元素 |

```python
import copy

inner = [1, 2]
data = {"k": inner}
shallow, deep = copy.copy(data), copy.deepcopy(data)
inner.append(3)
print(shallow, deep) # {'k': [1, 2, 3]} {'k': [1, 2]}

cyc = []
cyc.append(cyc) # 自引用
print(copy.copy(cyc)[0] is cyc) # True —— 浅拷贝不修复循环
dcyc = copy.deepcopy(cyc)
print(dcyc[0] is dcyc) # True —— deepcopy 让副本自洽

grid = [[0] * 2] * 2 # 两个槽指向同一个内层 list
grid[0][0] = 1
print(grid, grid[0] is grid[1]) # [[1, 0], [1, 0]] True
grid2 = [[0] * 2 for _ in range(2)] # 每次迭代新建内层 list
grid2[0][0] = 1
print(grid2) # [[1, 0], [0, 0]]
```

`deepcopy` 靠 `memo`（已复制对象表）保证循环引用不会无限递归，并保留副本内部的共享关系（同一个原对象在副本里仍只对应一个对象）。它按类型工作：自定义类默认可通过 `__reduce_ex__` 协议深拷贝，持有 socket、文件句柄、锁等不可拷贝资源时需要自己实现 `__deepcopy__`。`[0] * 2` 安全是因为 `0` 不可变；判断标准永远是「元素是否可变」。

### 4.7 可哈希性与字典键的契约

`dict` / `set` 的查找分两步：用 `hash(key)` 定位桶，再用 `==` 确认。由此得到两条硬约束：**相等必须同哈希**（`a == b` ⇒ `hash(a) == hash(b)`），**键的哈希在生命周期内必须稳定**。

```python
print(hash(1) == hash(1.0) == hash(True) == 1) # True —— 数值与布尔统一哈希
try: hash([1, 2])
except TypeError as exc: print(type(exc).__name__, exc) # unhashable type: 'list'

class CaseInsensitive: # 正确示范：__eq__ 与 __hash__ 一致
    def __init__(self, text): self.text = text
    def __eq__(self, other):
        return isinstance(other, CaseInsensitive) and self.text.lower() == other.text.lower()
    def __hash__(self): return hash(self.text.lower())

    print({CaseInsensitive("Key"): 1}[CaseInsensitive("kEy")]) # 1

    class Broken: # 只定义 __eq__，__hash__ 被隐式置为 None
        def __init__(self, text): self.text = text
        def __eq__(self, other):
            return isinstance(other, Broken) and self.text == other.text

        print(Broken.__hash__ is None) # True
        # hash(Broken("a")) -> TypeError: unhashable type: 'Broken'
```

`list` 不能做键不是语法限制而是语义不允许：它可以原地变化，哈希会失效，CPython 干脆不给它 `__hash__`。自定义类定义了 `__eq__` 却没有 `__hash__` 时，`__hash__` 被隐式设为 `None`——因为「值相等」一旦可自定义，默认的按身份哈希就不再自洽。

可哈希：`int`、`float`、`str`、`bytes`、`bool`、`None`、`frozenset`、元素全部可哈希的 `tuple`、未重载 `__eq__` 的普通类实例（按身份）。不可哈希：`list`、`dict`、`set`、任何 `__hash__` 为 `None` 的类。

### 4.8 `__slots__` 与 dataclass 对对象语义的影响

| 特性 | 普通类 | `__slots__` 类 | `@dataclass` | `frozen=True` |
| --- | --- | --- | --- | --- |
| 属性存储 | `__dict__`（约 296 字节） | 固定槽位 | 同普通类 | 同普通类 |
| 新增属性 | 可以 | 未声明则 `AttributeError` | 可以 | 不可以（`FrozenInstanceError`） |
| `__eq__` | 按身份 | 按身份 | 按字段生成 | 按字段生成 |
| `__hash__` | 按身份 | 按身份 | 因生成 `__eq__` 而变成 `None` | 按字段生成 |
| 弱引用 | 支持 | 需显式加入 `"__weakref__"` | 支持 | 支持 |

```python
import sys
from dataclasses import dataclass

class WithDict:
 def __init__(self, x): self.x = x

class WithSlots:
 __slots__ = ("x",)
 def __init__(self, x): self.x = x

a, b = WithDict(1), WithSlots(1)
print(hasattr(a, "__dict__"), hasattr(b, "__dict__")) # True False
print(sys.getsizeof(a), sys.getsizeof(b)) # 48 40（CPython 3.13，64 位）

@dataclass(frozen=True)
class Point:
 x: int
 y: int = 0

@dataclass
class Mutable: x: int

print(Point(1) == Point(1), hash(Point(1)) == hash(Point(1))) # True True
print(Mutable.__hash__ is None) # True —— 生成的 __eq__ 把 __hash__ 置为 None
# hash(Mutable(1)) -> TypeError: unhashable type: 'Mutable'
```

三点提醒：`__slots__` 只省内存、加约束，不改变「一切皆对象」，子类若未定义 `__slots__` 会重新获得 `__dict__` 使优化失效；`@dataclass(eq=True)`（默认）生成 `__eq__` 从而把 `__hash__` 置为 `None`，要进 `set` 就用 `frozen=True`、`eq=False` 或 `unsafe_hash=True`；`frozen=True` 只拦属性赋值，字段内部的可变对象照样能改。

---

## 5. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
| --- | --- | --- | --- |
| 用 `is` 比较值 | `a is 257` 时真时假 | 小整数缓存、常量去重、interning 都是实现细节 | 值比较一律 `==`，`is` 只留给单例 |
| 可变默认参数 | 第二次调用带着第一次的数据 | 默认值在 `def` 时创建一次，存于 `__defaults__` | 用 `None` 哨兵或不可变默认值 |
| 以为传参是拷贝 | 调用者的 list/dict 被意外改掉 | 传参是绑定，`append`/`update` 原地生效 | 显式 `copy`/`deepcopy`，并标注原地修改 |
| `[[0] * 2] * 2` | 改一行所有行都变 | `*` 复制的是引用 | `[[0] * 2 for _ in range(2)]` |
| 浅拷贝当深拷贝 | 改内层副本跟着变 | `copy` / `list(x)` / `d[:]` 只复制一层 | 嵌套结构用 `deepcopy` |
| `t[0] += [2]` | 抛 `TypeError` 但数据已改 | 先原地 `extend` 成功，再 `__setitem__` 失败 | tuple 里不放可变对象；取出改完再整体替换 |
| 改字段后 `in` 失效 | `set`/`dict` 查不到、出现重复键 | 哈希依赖的字段被原地修改 | 键保持不可变，或改完重建容器 |
| 自定义 `__eq__` 后进不了 `set` | `unhashable type` | 定义 `__eq__` 会把 `__hash__` 置为 `None` | 显式实现 `__hash__` 或 `frozen=True` |
| 直接调 `x.__len__` | `AttributeError` 或拿到假结果 | 特殊方法按类型查找，内置函数才有回退与校验 | 用 `len`、`iter`、`bool` |
| 函数内用 `+=` 改全局 | `UnboundLocalError` | `STORE` 使该名字被判定为局部变量 | 显式 `global`，或把状态放进可变对象 |

---

## 6. 面试问答

**Q1：为什么推荐 `len(x)` 而不是 `x.__len__`？**

<details><summary>参考答案</summary>

`len(x)` 走 C 层 `PyObject_Size`，按 `type(x)` 的类型槽（`sq_length` / `mp_length`）查找 `__len__`，**不查实例 `__dict__`**，并校验返回值：必须是 `int`（`bool` 可以，它是 `int` 子类）且 `>= 0`，否则抛 `TypeError` / `ValueError: __len__ should return >= 0`。

直接写 `x.__len__` 有三个问题：它是普通属性查找，会命中实例属性（`x.__len__ = lambda: 999` 之后与 `len(x)` 行为分叉）；丢掉回退逻辑（`iter(x)` 能靠 `__getitem__` 工作，`x.__iter__` 直接 `AttributeError`）；绕过 C 层快路径与参数校验。同理适用于 `iter`、`next`、`bool`、`hash`、`str`、`repr`：**协议用内置函数调用，别手写 dunder**。

</details>

**Q2：`==` 和 `is` 的本质区别？为什么不能用 `is` 比较数字和字符串？**

<details><summary>参考答案</summary>

`is` 比较身份（CPython 比指针，即 `id(a) == id(b)`），不可重载；`==` 比较值，走 `type(a).__eq__(a, b)`，返回 `NotImplemented` 时反射 `type(b).__eq__(b, a)`，两边都放弃才回退到身份比较（默认 `object.__eq__` 就是 `is`）。

不能用 `is` 比较值，因为与身份相关的优化都不是语言保证：`-5..256` 的小整数是预创建单例（`int("256") is int("256")` 为 `True`，`257` 为 `False`）；同一 code object 的常量会去重（一段代码内 `"hi there" is "hi there"` 为 `True`，换位置未必）；只有「看起来像标识符」的字符串常量在编译期被 intern；`id` 会被复用。

附带一个坑：`nan != nan` 恒为 `True`，但同一个 `nan` 对象放进 `dict` 后能用它自己取出来——字典查找**先比身份，再比相等**。

</details>

**Q3：`def f(x, acc=[])` 到底发生了什么？**

<details><summary>参考答案</summary>

默认参数表达式在 **`def` 语句执行时**求值一次，结果存进函数对象的 `__defaults__`（仅位置参数）/ `__kwdefaults__`（keyword-only）。之后每次省略该参数，函数体拿到的都是**同一个对象**。`[]` 可变，所以 `acc.append(...)` 的副作用被持久化到下一次调用——本质是「传参是绑定 + 原地修改可见」的叠加。

修法：`None` 哨兵（最通用，`acc = [] if acc is None else acc`）；不可变默认值（``、`0`、`""`、`frozenset`）；`None` 也是合法业务值时用 `_NOT_SET = object` 哨兵。排查手段是 `print(f.__defaults__)`，看到真实数据而不是 `None`，就说明默认值被当成了状态容器。同一坑还出现在 `def f(x=time.time)`、`def f(x={})`、`def f(x=SomeCache)` 上。

</details>

**Q4：为什么 `list` 不能做字典键？`__hash__` 与 `__eq__` 的契约是什么？**

<details><summary>参考答案</summary>

`dict` / `set` 是哈希表：先用 `hash(key)` 找桶，再用 `==` 确认。这要求键的哈希在生命周期内稳定，并且相等即同哈希。`list` 支持原地增删，哈希随时会变，会导致同一个键散落到不同桶、查不到或出现重复键，所以 CPython 不给它 `__hash__`（`TypeError: unhashable type: 'list'`）；`dict`、`set`、`bytearray` 同理。

契约两条：`a == b` 为真 ⇒ `hash(a) == hash(b)` 必须为真（反之不要求，哈希冲突是允许的）；参与 `__hash__` 的字段在对象作为键期间不能修改，`__hash__` 必须返回 `int`。配套规则：类中定义 `__eq__` 而未定义 `__hash__`，`__hash__` 被隐式置为 `None`。需要值的哈希就显式实现（如 `hash((self.a, self.b))`）或用 `@dataclass(frozen=True)`。

`frozenset` 可哈希而 `set` 不可；`tuple` 当且仅当所有元素可哈希时可哈希，所以 `hash((1, [2]))` 抛 `TypeError: unhashable type: 'list'`。

</details>

---

## 7. 自测题

1. `a = [1, 2]`、`b = a`、`b += [3]` 之后 `a` 是什么？第三行换成 `b = b + [3]` 呢？解释协议层面的差别。
2. 下面这段打印什么？为什么？

 ```python
 def f(x, acc=[]):
 acc.append(x); return acc

 print(f(1), f(2), f.__defaults__)
 ```

3. `t = ([1], 2)` 执行 `t[0] += [2]` 会发生什么？数据被修改了吗？
4. 为什么定义了 `__eq__` 的类默认不能放进 `set`？给出两种修法。
5. 一个类只实现了 `__getitem__`，没有 `__iter__` 和 `__contains__`：`for x in obj`、`5 in obj` 还能工作吗？`obj.__iter__` 呢？

<details><summary>参考答案</summary>

1. `a` 变成 `[1, 2, 3]`：`+=` 调用 `list.__iadd__`（原地 `extend` 并返回 `self`），`a`、`b` 始终是同一个对象。换成 `b = b + [3]` 后 `b` 指向新建 list，`a` 保持 `[1, 2]`：`+` 走 `__add__` 产生新对象，再 `STORE` 回 `b`。

2. 打印 `[1, 2] [1, 2] ([1, 2],)`。默认值 `[]` 在 `def` 执行时创建一次并存入 `f.__defaults__`，两次调用共享同一个 list。

3. 抛 `TypeError: 'tuple' object does not support item assignment`，但**数据已经被修改**，`t` 变成 `([1, 2], 2)`。顺序是：取 `t[0]` → `__iadd__` 原地扩展成功 → 写回 `t[0]` 时失败。

4. 定义了 `__eq__` 而没有 `__hash__`，Python 把 `__hash__` 隐式置为 `None`，实例不可哈希。修法：显式实现与 `__eq__` 一致的 `__hash__`（如 `hash((self.a, self.b))`）；用 `@dataclass(frozen=True)` 自动生成一致的 `__eq__`/`__hash__`；或 `@dataclass(eq=False)` 保留基于身份的哈希。

5. 都能工作：`iter` 在没有 `__iter__` 时回退到旧式序列协议，反复调用 `__getitem__(0), __getitem__(1), ...` 直到 `IndexError`；`in` 在没有 `__contains__` 时回退到 `__iter__`，再回退到 `__getitem__`。但 `obj.__iter__` 抛 `AttributeError`，因为该方法根本不存在——这正是「协议用内置函数调用」的理由。

</details>

---

## 8. 延伸阅读

- [The Python Data Model（官方 reference，本文主线）](https://docs.python.org/3/reference/datamodel.html)
- [`__hash__` 与 `__eq__` 的契约](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Comparisons：`is` 与 `==` 的求值顺序](https://docs.python.org/3/reference/expressions.html#comparisons)
- [`copy` 模块：浅拷贝与深拷贝](https://docs.python.org/3/library/copy.html)
- [`dataclasses` 的 `eq` / `frozen` / `unsafe_hash`](https://docs.python.org/3/library/dataclasses.html)
- [`sys.intern` 字符串驻留](https://docs.python.org/3/library/sys.html#sys.intern)
- [`dis` 字节码反汇编](https://docs.python.org/3/library/dis.html)
- [PEP 8：与单例比较应使用 `is`](https://peps.python.org/pep-0008/#programming-recommendations)
- 本仓库相关笔记：[02 · 数据模型与容器](../03-面向对象与数据模型/README.md)、[09 · CPython 内部机制](../06-CPython与算法/README.md)、[术语表](../90-cheatsheet/glossary.md)

---

[⬅️ 返回本章目录](README.md)
