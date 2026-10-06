---
article_id: kp-8c8777d73e347027
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-7f36aafe1891
learning_sourceId: 7f36aafe1891
learning_order: 9
learning_objective: 理解并验证：用假模型跑通全流程
---

# 用假模型跑通全流程

> **学习目标**：能够解释「用假模型跑通全流程」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Python 的 AST 与异常处理、JSON Schema 基本概念、LLM 的采样与上下文窗口、[ReAct / Plan-and-Execute / Reflexion 的术语定义](../../../../../07-agent/90-cheatsheet/glossary.md)
>
> **所属主题**：从零实现一个最小 Agent · 深入机制

## 本次只学这一点

没有 key 时，用一个靠关键词走脚本的假模型就能把循环跑通，用来验证解析器、工具层与终止判定：

```python
def mock_llm(prompt: str) -> str:
    """离线假模型：靠 prompt 里 Observation 的条数走固定脚本。"""
    rounds = prompt.count("Observation:")
    if rounds == 0:
        return 'Thought: 先算数。\nAction: calculator\nAction Input: {"expression": "(1250 + 430) * 3 / 4"}'
    if rounds == 1:
        return 'Thought: 再查概念。\nAction: search\nAction Input: {"query": "ReAct Reflexion", "top_k": 2}'
    return ('Thought: 材料齐了。\nFinal Answer: (1250 + 430) * 3 / 4 = 1260；'
'ReAct 交错推理与行动，Reflexion 失败后反思再重试。')
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用假模型跑通全流程」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-从零实现一个最小Agent.md)
