---
article_id: kp-55169af6a4b388d7
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-0ae5654d8e63
learning_sourceId: 0ae5654d8e63
learning_order: 9
learning_objective: 理解并验证：可观测性
---

# 可观测性

> **学习目标**：能够解释「可观测性」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议与错误处理、[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的状态持久化、[08-大宗商品价格监控Agent项目复盘](../../../../../07-agent/07-前沿与面试/08-大宗商品价格监控Agent项目复盘.md)。
>
> **所属主题**：-Agent工程化与可靠性设计 · 关键机制

## 本次只学这一点

| 手段 | 的实例 | 作用 |
| --- | --- | --- |
| 分级日志 | `from base import logger, Config`，`logger.info/error` | 结构化输出，可按级别过滤 |
| 关键节点计时 | `processing_time = time.time() - start_time` | 发现慢查询与慢检索 |
| 完整轨迹打印 | LangChain `verbose=True`；CrewAI `verbose=2` | 定位「选错工具」「任务传递丢失」类问题 |
| 中间结果落盘 | GPT2 医疗机器人的 `samples.txt` 聊天记录 | 事后复盘生成质量 |
| 可视化看板 | `dashboard.py`（Chart.js + 120 秒自动刷新） | 让人一眼看到「当前状态是否正常」 |
| 依赖清单 | `requirements.txt` | 环境可复现 |

一个反例：大宗商品项目的日志全靠 `print`，且 `logs.txt` 是空文件——**打印到 stdout 在后台运行时等于没有日志**。生产环境应改为写入带时间戳的日志文件（或日志采集系统），并至少保留最近若干天。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可观测性」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md)
