# 折叠块渲染探针（第二轮：复杂场景）

## 变体 E：summary 内含反引号

<details markdown="1">
<summary><strong>变体 E：`f.__defaults__` 与 `__hash__` 的关系</strong></summary>

说明 `__hash__` 被置为 `None` 的情形。

</details>

## 变体 F：块内含围栏代码块

<details markdown="1">
<summary><strong>变体 F：含代码块</strong></summary>

```python
def f(a, b=[]):
    return a, b
```

1. 第一项
2. 第二项

</details>

## 变体 G：块内含表格

<details markdown="1">
<summary><strong>变体 G：含表格</strong></summary>

| 现象 | 原因 |
| --- | --- |
| `f.close` 未执行 | 异常跳过了关闭语句 |

</details>

## 变体 H：块内含嵌套 details

<details markdown="1">
<summary><strong>变体 H：嵌套折叠</strong></summary>

外层说明。

<details markdown="1">
<summary>内层摘要</summary>

1. 内层列表项一
2. 内层列表项二

</details>

</details>

## 变体 I：块内不含 summary

<details markdown="1">
<summary><strong>变体 I：正常结构</strong></summary>

1. 列表项 `code_i1`
2. 列表项 `code_i2`

</details>
