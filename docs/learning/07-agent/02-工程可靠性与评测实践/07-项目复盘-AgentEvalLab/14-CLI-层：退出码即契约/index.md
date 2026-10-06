---
article_id: kp-f5a2510ebc58968c
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 13
learning_objective: 理解并验证：CLI 层：退出码即契约
---

# CLI 层：退出码即契约

> **学习目标**：能够解释「CLI 层：退出码即契约」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

```ts
main().catch((error: unknown) => {
  if (error instanceof SchemaValidationError) {
    console.error(`输入 Schema 校验失败：\n${error.message}`);
    process.exitCode = 2;      // 输入问题：可以修数据
    return;
  }
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;        // 其它问题：先查代码与环境
});
```

`exit 2` 与 `exit 1` 的区分让 CI 能分流：2 表示"数据不符合 Schema，去看那行 JSON 路径"；1 表示"工具自身或环境出问题"。若两者合并成一个非零码，CI 日志里会长期混着"数据脏"和"工具坏"两类完全不同的故障。

用法上 CLI 支持 `--input`/`--output` 的空格与 `=` 两种写法：

```bash
agent-eval-lab evaluate --input ./my-runs.jsonl --output ./reports/my-report.json
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「CLI 层：退出码即契约」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
