---
article_id: kp-553f38da25193b84
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-272ce9acf0c8
learning_sourceId: 272ce9acf0c8
learning_order: 24
learning_objective: 理解并验证：常见坑表
---

# 常见坑表

> **学习目标**：能够解释「常见坑表」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：BERT/MLM 预训练目标、Tokenizer 与词表（vocab）、`[MASK]` token 与 MLM Head、交叉熵损失、基本的分类任务指标（acc / P / R / F1）。
>
> **所属主题**：-指令数据构造与清洗 · 数据清洗清单

## 本次只学这一点

| 坑 | 表现 | 定位方法 | 修复 |
|---|---|---|---|
| 模板与分词器不匹配 | 伪 token / `[MASK]` 被切成多 token；`mask_position` 数量异常 | 检查 `convert_tokens_to_ids(["MASK"])` 是否等于 `unk` | 用分词器已有词表 token；`[MASK]` 必须写成 `[MASK]` |
| Verbalizer 词表外 token | 某类别 loss 常年不降，预测永远落不到该类 | 检查 `encode_label` 的 id 是否含 `unk_token_id` | 标签词换成词表内常见词；必要时 `add_tokens` |
| 标签词长度超 `max_label_len` | 标签被静默截断，与 Verbalizer 字典对不上 | 打印所有标签词的 token 数 | 调大 `max_label_len`（= 最长标签词 token 数） |
| 样本泄漏到验证集 | 训练 loss 与验证指标同步飙高，线上大跌 | 文本指纹交集检查 + 分组键交集检查 | 按 item_id/user_id/时间做分组切分 |
| 模板字面量泄漏 | 验证集里出现 `这是一条[MASK]评论` | 见 5.7 的 `find_template_leak` | 模板只在运行时拼接，绝不写进原始数据文件 |
| `attention_mask` 未随手工拼接更新 | 训练能跑但 loss 不降（伪 token 被 mask 掉） | 打印 `attention_mask` 中伪 token 位置是否为 1 | 拼接后显式重算 mask（见 3.3） |
| 兜底映射过度命中 | `网球拍` 也被判成 `体育` | 统计兜底命中率 | 保留兜底开关；线上记录兜底比例，过高时补子标签 |
| 去重时丢了标签列 | 同一输入两个不同标签的样本被静默合并 | 按 (指纹, label) 去重而非仅按指纹 | 无标签去重，冲突样本单独进人工队列 |
| 长度截断切掉最后一轮 | 多轮对话样本的监督信号为空 | 校验 `validate_dialogue` 最后一条必须是 assistant | 按轮丢弃最老轮次，而非按 token 硬截 |
| 训练数据混入评测集同源数据 | 指标虚高 5~20 个百分点 | 与评测集做 n-gram 重合率统计 | 评测集必须来自独立采集批次 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「常见坑表」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/06-指令数据构造与清洗.md)
