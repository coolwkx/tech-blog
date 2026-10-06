---
article_id: kp-8f6879c4b0d9a084
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 2
learning_objective: 理解并验证：从零实现一个最小 Agent：最小可运行示例
---

# 从零实现一个最小 Agent：最小可运行示例

> **学习目标**：能够解释「从零实现一个最小 Agent：最小可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 最小可运行示例

## 本次只学这一点

先看一个 16 行版本，把循环骨架剥到只剩骨头（没有超时、没有重试、没有重复检测，只为看清形状）：

```python
import json, re

def mini_loop(question, llm, tools, max_steps=5):
    scratchpad = ""
    for _ in range(max_steps):
        raw = llm(question, scratchpad) # 1. 问模型
        if m := re.search(r"Final Answer[:：]\s*(.+)", raw):
            return m.group(1) # 2. 终止判定
        name = re.search(r"Action[:：]\s*(\w+)", raw).group(1)
        args = json.loads(re.search(r"Action Input[:：]\s*(.+)", raw).group(1))
        try:
            obs = tools[name](**args) # 3. 执行工具
        except Exception as exc:
            obs = f"ERROR: {type(exc).__name__}: {exc}" # 4. 失败不抛出，只回灌
            scratchpad += f"{raw}\nObservation: {obs}\n" # 5. 结果喂回去
            return "达到步数上限，仍未得到答案"
```

**逐行说明**：

| 代码 | 作用 | 容易误解的点 |
| --- | --- | --- |
| `for _ in range(max_steps)` | 步数上限，唯一的硬终止条件 | 它数的是「执行了几个动作」，不是「调用了几次模型」；解析失败的那一轮也算一步 |
| `llm(question, scratchpad)` | 把问题与历史一起交给模型 | 无状态 API 里不存在「对话」，每次都得把完整 scratchpad 重新发一遍，这是 token 成本的主要来源 |
| `re.search(r"Final Answer...")` | 模型主动宣布结束 | 判定必须先于动作解析，否则模型把答案写进 `Action Input` 时会被当成工具参数 |
| `tools[name](**args)` | 查表执行，名字即接口 | 工具名来自模型，必须先查表；直接 `getattr(module, name)` 等于把模块里所有函数暴露给模型 |
| `except Exception` | 把异常降级成 observation | 这是整个循环最反直觉的一条：**工具报错不是程序错误，而是模型下一步的输入** |
| `scratchpad += ...` | 唯一的记忆载体 | 拼接顺序决定模型看到什么；漏掉 Observation，模型就失去对自己上一步结果的感知 |

这段代码能跑，但一上真实模型就会暴露五个问题：参数可能不是合法 JSON、工具可能卡死不返回、模型可能重复同一个动作、scratchpad 会无限膨胀、模型可能根本不按格式输出。下面逐条补上。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「从零实现一个最小 Agent：最小可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
