# 折叠块 Markdown 渲染探针

本文件用于实测哪种 details 写法能让块内 Markdown 正常解析，验证后删除。

## 变体 A：裸 details + 空行（当前全站写法）

<details>
<summary>变体 A 的摘要</summary>

1. 第一项 `code_a` 和 **粗体**
2. 第二项 `code_b`
3. 第三项

- 无序甲
- 无序乙

</details>

## 变体 B：details 加 markdown="1"

<details markdown="1">
<summary>变体 B 的摘要</summary>

1. 第一项 `code_b1` 和 **粗体**
2. 第二项 `code_b2`
3. 第三项

- 无序甲
- 无序乙

</details>

## 变体 C：pymdownx.details 的 ??? 语法

??? note "变体 C 的摘要"

    1. 第一项 `code_c1` 和 **粗体**
    2. 第二项 `code_c2`
    3. 第三项

    - 无序甲
    - 无序乙

## 变体 D：summary 内用 strong，正文用无序列表

<details>
<summary><strong>变体 D 的摘要</strong></summary>

- 第一项 `code_d1` 和 **粗体**
- 第二项 `code_d2`
- 第三项

</details>
