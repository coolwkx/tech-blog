---
article_id: kp-ee93bece85e09494
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 9
learning_objective: 理解并验证：Schema 层：把错误定位到 JSON 路径
---

# Schema 层：把错误定位到 JSON 路径

> **学习目标**：能够解释「Schema 层：把错误定位到 JSON 路径」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

`src/schema.ts` 不用通用校验库，而是手写一组 `requiredString / requiredEnum / parseSha256` 之类的原语，每个原语失败时抛 `SchemaValidationError` 并带上**调用点传入的路径**：

```ts
// 精简重写：路径逐层拼接，最终错误形如 "$.manifest.promptHash"
function requiredString(object: JsonObject, key: string, path: string): string {
  const value = object[key];
  if (typeof value !== "string" || value.trim().length === 0) {
    fail(`${path}.${key}`, "必须是非空字符串");   // fail() 抛 SchemaValidationError
  }
  return value;
}

function parseSha256(value: string, path: string): string {
  if (!/^sha256:[0-9a-f]{64}$/iu.test(value)) fail(path, "必须使用 sha256:<64位十六进制> 格式");
  return value;
}
```

几个值得抄的细节：

1. **`fail()` 的返回类型是 `never`**，所以 TypeScript 能正确做窄化，不需要在每个调用点写 `else throw`。
2. **JSONL 记录带显式 `recordType`**（`manifest | task | run | result`），并且**禁止混用 `run` 与 `result`**，也禁止 `result` 输入带 `task` 记录。这避免了"一半是轨迹一半是结果"的语义混乱。
3. **`parseInputText` 先尝试整份 `JSON.parse`，失败才降级到逐行解析**，所以同一套校验代码同时服务 `.json` 与 `.jsonl`；JSONL 支持空行与 `#` 注释，报错时带行号 `$line[17]`。
4. **Manifest 校验包含跨字段业务约束**：`repeatCount >= seeds.length`、`taskIds` 去重后不能为空、`seeds` 去重后不能为空、`classification === "public"` 时 `containsPrivateData` 必须为 false、`evaluatorVersion` 必须是语义化版本、`codeCommit` 必须是 7–40 位十六进制。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「Schema 层：把错误定位到 JSON 路径」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
