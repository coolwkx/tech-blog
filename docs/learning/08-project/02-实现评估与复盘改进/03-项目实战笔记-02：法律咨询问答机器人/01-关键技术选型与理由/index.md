---
article_id: kp-4a721e18b06ae876
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-3e5bdcfe80e4
learning_sourceId: 3e5bdcfe80e4
learning_order: 4
learning_objective: 理解并验证：关键技术选型与理由
---

# 关键技术选型与理由

> **学习目标**：能够解释「关键技术选型与理由」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：Transformer Decoder 结构与自注意力、因果语言模型（CLM）的 shift 对齐损失、PyTorch 的 `Dataset / DataLoader / collate_fn`、HuggingFace `transformers` 的 `GPT2LMHeadModel` 与 `BertTokenizerFast`。
>
> **所属主题**：项目实战笔记 02：法律咨询问答机器人 · 关键技术选型与理由

## 本次只学这一点

| 方案 | 优点 | 代价 | 本项目为何选它 |
| --- | --- | --- | --- |
| GPT2（Decoder-only） | 天然适配自回归生成，`GPT2LMHeadModel` 开箱即用 | 没有 Encoder，无法做双向理解/分类 | 任务是"续写对话"，Decoder 就是唯一正确的形状 |
| `GPT2Config.from_json_file` 自建 + 不加载预训练权重 | 词表可自定义（法律领域 13317 词），模型小、训练快 | 失去通用语义先验，需要更多数据才能说人话 | 语料是法律垂直领域，且要求可复现地跑完训练全流程 |
| `BertTokenizerFast` + 自定义 vocab | 中文按字切分效果好，`vocab.txt` 轻量 | 引入了 `[CLS]/[SEP]/[PAD]` 三个 BERT 特殊符号到 GPT2 体系 | 把 `[SEP]` 直接当"话轮分隔符 + 生成终止符"用，一符两用，极简 |
| 用 pkl 缓存 tokenize 结果 | 训练时无需重复分词，epoch 迭代快 | 换词表就得重新生成 pkl | 3 万条语料分词只需几秒，相比训练耗时微不足道，但避免了每 epoch 重复 IO |
| `pad_sequence` + `padding_value=-100` | 变长序列无需人为截齐，-100 自动被 `CrossEntropyLoss` 忽略 | 需要自定义 `collate_fn` | 标准做法，`ignore_index=-100` 是 PyTorch 约定 |
| 梯度累积（steps=4） | 显存不够也能凑出大 batch 的等效效果 | 训练代码复杂度上升 | 单卡消费级 GPU 训 12 层 transformer 的必备手段 |
| AdamW + warmup + linear decay | 预热防早期梯度爆炸，衰减保证后期稳定收敛 | 需要正确计算 `t_total` | Transformer 训练的经典组合 |
| top-k 采样 + 重复惩罚 | 生成多样不死板，且不鬼打墙 | 温度/k 值需要调 | 对话生成场景比贪心解码自然得多 |
| Flask 服务化 | 几行代码就能提供 Web 交互 | 单线程阻塞、无并发能力 | 教学/演示场景够用，生产要换 FastAPI + 队列 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「关键技术选型与理由」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/02-项目-法律咨询问答机器人.md)
