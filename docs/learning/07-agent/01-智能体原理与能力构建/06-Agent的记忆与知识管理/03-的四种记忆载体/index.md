---
article_id: kp-4ef81bee4718c114
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3dbf2b7f4206
learning_sourceId: 3dbf2b7f4206
learning_order: 2
learning_objective: 理解并验证：的四种记忆载体
---

# 的四种记忆载体

> **学习目标**：能够解释「的四种记忆载体」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[03-LangChain与工具编排](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md) 的 Memory 组件、[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的向量检索、[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的 messages 角色约定。
>
> **所属主题**：-Agent的记忆与知识管理 · 核心概念

## 本次只学这一点

| 载体 | 出现位置 | 存什么 | 读的方式 | 写的方式 |
| --- | --- | --- | --- | --- |
| `ChatMessageHistory` | LangChain Memory 组件 | `HumanMessage` / `AIMessage` 对象列表 | `history.messages` | `add_user_message` / `add_ai_message` |
| 消息字典 | `messages_to_dict` / `messages_from_dict` | 可 JSON 序列化的 dict 列表 | `messages_from_dict(dicts)` | `messages_to_dict(history.messages)` |
| token id 历史 | GPT2 医疗问诊机器人 | 每轮 utterance 的 token id 列表 | 拼进 `input_ids` 送模型 | `history.append(text_ids)` |
| JSON 状态 / 历史文件 | 大宗商品价格监控项目 | 上一次价格、状态、提醒时间；历史价格序列 | `load_state()` / `load_history()` | `save_state()` / `json.dump` |
| 向量库（外部知识） | RAG 系统 | 文档块向量 + 父块内容 | 混合检索 + 重排 | `upsert` 写入 |

注意第四行其实包含两类不同的东西：**状态**（key-value，只关心最新值）与**历史**（时间序列，关心趋势）——大宗商品项目把它们分成了 `gold_state.json` 与 `gold_history.json` 两个文件，这个划分值得学习。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「的四种记忆载体」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md)
