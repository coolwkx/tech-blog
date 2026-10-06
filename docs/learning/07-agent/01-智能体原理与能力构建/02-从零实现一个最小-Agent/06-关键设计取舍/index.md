---
article_id: kp-75ee675cde82eb74
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 5
learning_objective: 理解并验证：关键设计取舍
---

# 关键设计取舍

> **学习目标**：能够解释「关键设计取舍」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 深入机制

## 本次只学这一点

**计算器为什么绝不能用 `eval`。** `eval("__import__('os').system('rm -rf /')")` 是一行合法表达式。即使加了 `{"__builtins__": {}}`，也挡不住 `.__class__.__base__.__subclasses__` 这类从对象模型里爬回内置函数的路径。上面用的是「先 `ast.parse`，再自己递归求值」：白名单里只有数字常量、一元正负号和七种二元运算符，其余节点一律抛异常。另外还卡了指数上限——`2**999999` 会把进程算到内存耗尽，这是一条不看代码就想不到的拒绝服务路径。

**`read_file` 为什么不用字符串前缀判断。** `str(target).startswith(str(root))` 会被 `/data/root_evil.txt` 骗过（前缀命中了 `/data/root`）。上面先 `resolve` 成真实路径再检查 `root in target.parents`，`../` 和软链接都会被解开后落到比较里。更严格的话，Windows 上还要叠一层 `os.path.normcase`（路径大小写不敏感），并且注意 `resolve` 不防 TOCTOU——检查与打开之间路径可能被换掉。

**解析器为什么要写两套。** 真实模型经常把 JSON 包在 Markdown 代码围栏里、在 `Action` 前多说一句解释、或者把 `Action Input` 写成裸字符串。`parse_response` 先去围栏、再试 JSON、最后退回正则，并允许「只有 `Action` 没有 `Thought`」。**任何解析失败都不抛到循环外**，而是变成一条 `ERROR: 无法解析...` 的 observation 让模型自己重试——这是 Agent 鲁棒性的第一道闸门。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键设计取舍」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
