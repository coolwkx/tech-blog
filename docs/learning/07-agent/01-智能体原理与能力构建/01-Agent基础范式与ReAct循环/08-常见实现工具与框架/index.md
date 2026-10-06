---
article_id: kp-1ec6910dd246325a
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-0b49eeb55140
learning_sourceId: 0b49eeb55140
learning_order: 7
learning_objective: 理解并验证：常见实现工具与框架
---

# 常见实现工具与框架

> **学习目标**：能够解释「常见实现工具与框架」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的消息角色与 API 调用、[../llm/04-提示词工程.md](../../../../../06-llm/06-提示工程/04-提示词工程.md) 的 system prompt 用法、本目录 [02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)。
>
> **所属主题**：-Agent基础范式与ReAct循环 · 核心概念

## 本次只学这一点

| 工具 / 框架 | 类型 | 特点 | 地址 |
| --- | --- | --- | --- |
| AutoGPT | 自主 Agent | 给定名称、描述和若干目标即可自主完成项目 | https://github.com/Significant-Gravitas/AutoGPT |
| 百度 AgentBuilder | 平台 | 提供构建、训练和部署 Agent 的全流程支持 | https://agents.baidu.com/center |
| 字节扣子（Coze） | 平台 | 快速搭建基于大模型的问答 Bot 并发布到社交平台 | https://www.coze.cn/home |
| 天工 SkyAgents | 企业平台 | 集成大模型、知识库等模块，支持定制化 Agent | https://model-platform-skyagents.tiangong.cn/home/agent |
| AgentGPT | 开源工具 | 基于 GPT-4 的自动化机器人，浏览器中配置部署 | https://agentgpt.reworkd.ai/zh |
| LangChain | 开发框架 | Agents 模块提供 Agent 管理、记忆模块、工具集成 | https://github.com/langchain-ai/langchain |
| AutoGen | 多 Agent 框架 | 多个可定制、可对话的代理协作解决任务，允许人类参与 | https://github.com/microsoft/autogen |
| ChatDev | 多 Agent 框架 | 通过自然语言交互和多智能体协作实现软件开发全流程自动化 | https://github.com/OpenBMB/ChatDev |
| CrewAI | 多 Agent 框架 | 建立在 LangChain 之上，支持构建多 Agent 协作系统 | https://github.com/joaomdmoura/crewAI |

选型的一般顺序（**说明**：本小节超出本主题范围，为通用知识补充）：先用平台（Coze / AgentBuilder）验证业务可行性，再用框架（LangChain / CrewAI）落地私有逻辑，最后才考虑自研编排层。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「常见实现工具与框架」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md)
