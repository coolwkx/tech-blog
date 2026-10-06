---
article_id: kp-451a7c1d006eee9f
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-d130ec37c55d
learning_sourceId: d130ec37c55d
learning_order: 9
learning_objective: 理解并验证：查询意图识别：不是所有问题都该检索
---

# 查询意图识别：不是所有问题都该检索

> **学习目标**：能够解释「查询意图识别：不是所有问题都该检索」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[05-Agent的记忆与知识管理](../../../../../07-agent/03-记忆与多智能体/05-Agent的记忆与知识管理.md) 的外部知识记忆、[04-Agent的规划与任务分解](../../../../../07-agent/02-工具与规划/04-Agent的规划与任务分解.md) 的查询改写策略、[../llm/07-向量数据库与Milvus.md](../../../../../06-llm/07-检索增强RAG/07-向量数据库与Milvus.md)。
>
> **所属主题**：-RAG作为Agent的知识获取手段 · 关键机制

## 本次只学这一点

`QueryClassifier` 用 BERT 做二分类，把查询分成「通用知识」与「专业咨询」：

| 项 | 值 |
| --- | --- |
| 底座模型 | `bert-base-chinese` |
| 任务 | `BertForSequenceClassification`，`num_labels=2` |
| 标签映射 | `{"通用知识": 0, "专业咨询": 1}` |
| 训练数据 | `training_dataset_hybrid_5000.json`，80% 训练 / 20% 验证 |
| 关键超参 | `num_train_epochs=3`、`per_device_train_batch_size=8`、`max_length=128`、`fp16=False`、`metric_for_best_model="eval_loss"`、`save_total_limit=1` |
| 效果 | 准确率 93% 左右（分类报告 precision/recall/f1 均约 0.93，混淆矩阵 `[[460, 40], [30, 470]]`） |

**路由逻辑**：

```text
if query_category == "通用知识":
 prompt_input = rag_prompt.format(context="", question=query, phone=...)
 answer = llm(prompt_input) # 不检索
else:
 strategy = strategy_selector.select_strategy(query)
 context_docs = retrieve_and_merge(query, source_filter, strategy)
 answer = llm(rag_prompt.format(context=context, ...))
```

还记录了一个真实修复：早期 `evaluate_model` 对数字标签重复映射回 `label_map`，触发 `KeyError: 1`；修法是**直接使用传入的数字标签**，只对 `texts` 做分词。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「查询意图识别：不是所有问题都该检索」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md)
