# 贡献与写作规范

这个仓库首先是**个人复习笔记库**，但任何纠错与改进都欢迎。

## 提 Issue

- 笔记里的**事实性错误**（请附正确说法的出处，优先论文 / 官方文档）
- 代码跑不通（请附 Python 版本、依赖版本与完整报错）
- 希望补充的知识点

## 提 PR

1. Fork 并新建分支：`git checkout -b fix/attention-typo`
2. 修改后自查：
 - [ ] Markdown 在 GitHub 上渲染正常（表格与代码块闭合）
 - [ ] 代码示例**亲自跑过**
 - [ ] 术语与 `docs/<分区>/90-cheatsheet/glossary.md` 一致
 - [ ] 更新了本章 `README.md` 的状态表
 - [ ] `python tools/lint_notes.py` 通过
3. 提交信息格式 `类型: 简述`，类型取 `feat|fix|docs|refactor|ci`。
4. 发起 PR 并说明「改了哪一节、为什么」。

## 折叠答案的写法（重要）

面试问答与自测题的答案放在折叠块里。**题目必须写进 summary，并用 HTML 标签而不是 Markdown 加粗**：

```html
<details>
<summary><strong>Q1：为什么 x += 1 不是原子的？</strong></summary>

（这里是答案，可以正常使用 Markdown）

</details>
```

**为什么必须用 `<strong>` 而不是 Markdown 的加粗语法**：summary 属于 HTML 块，GitHub 不会在 HTML 块内解析 Markdown 强调语法。用 Markdown 加粗会把两个星号原样显示在页面上，看起来像题目丢失。`<strong>` 是 HTML 标签，在任何渲染器下都生效。

**为什么题目要放进 summary**：题目直接显示在折叠条上，不用点开就知道问的是什么；点开才看答案。

**结构要求**：`<details>`、`<summary>`、`</details>` 各自单独占一行，并在 `</summary>` 之后与 `</details>` 之前保留空行。

## 写作规范

- 语言：中文为主，**英文术语保留原文**。
- 每篇笔记结构（缺一不可）：

```markdown
> **一句话总结**：…
> **前置知识**：…
> **学完能做到**：1. … 2. … 3. …

## 1. 核心概念 （至少一个表格）
## 2. 可运行示例 （代码必须真实可跑）
## 3. 常见坑 （表格：坑 / 现象 / 原因 / 正确做法）
## 4. 面试问答 （<details> 折叠答案）
## 5. 自测题 （<details> 折叠答案）
## 6. 延伸阅读 （真实链接）

---
[⬅️ 返回本章目录](README.md)
```

- 引用外部结论必须给链接；数字要给量级和出处。
- 一篇对应一个完整主题，具体概念通过文内目录定位，不按行数机械拆分。
- 不要提交模型权重、数据集、压缩包、图片等二进制大文件（见 `.gitignore`）。

## 笔记模板

见 [`templates/`](templates/)。


## 主题笔记维护约定

分类止于「领域 → 学习方向 → 主题」，每个主题对应一篇完整笔记，不继续拆分成细小知识点页面。新增主题登记到学习目录，并通过 learning_sourceId 关联完整原文；具体概念使用文内标题定位。保留前置知识、验证方法和上下文依赖。旧细分页面仅用于历史链接和学习记录兼容。

`article_id` 是学习记录的永久键，移动文件时保留它。新增页面使用 `tools/register_articles.py` 分配编号，并更新导航和目录登记。导入已有内容时避免重新生成编号。

构建与预览统一使用 `python tools/site.py build` 和 `python tools/site.py preview`。生成的 `site/` 不提交。修改学习记录逻辑后运行 `node tests/records.test.cjs`。
