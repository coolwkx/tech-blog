---
article_id: kp-1deef3d9f405c2a2
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 8
learning_objective: 理解并验证：凭证、权限与最小暴露
---

# 凭证、权限与最小暴露

> **学习目标**：能够解释「凭证、权限与最小暴露」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

| 风险 | /项目中的表现 | 正确做法 |
| --- | --- | --- |
| API Key 硬编码 | CrewAI 项目里 `to_addr` / `from_pwd` / `from_addr` 写在源码（部分打码） | 环境变量（`os.environ["OPENAI_API_KEY"]`）或密钥管理服务 |
| 配置中的推送 Key 明文入库 | `config.json` 里 `sc_key` 明文 | 加入 `.gitignore`，仓库只放 `config.example.json` |
| 让 LLM 生成的 SQL 直接执行 | `ask_database(query)` 直接 `cursor.execute(query)` | 只读账号 + `SELECT` 白名单 + 禁止多语句 + 超时 + 行数上限 |
| 用 `eval` 解析外部响应 | 天气示例的 `eval(response.text)` | 改用 `json.loads` 或 `ast.literal_eval` |
| 日志打印完整上下文 | debug 打印可能含用户隐私 | 日志分级；入盘前脱敏 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「凭证、权限与最小暴露」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
