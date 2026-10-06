---
article_id: kp-402bec48a39cb239
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-c24a4924b596
learning_sourceId: c24a4924b596
learning_order: 9
learning_objective: 理解并验证：参数配置：一份集中管理的实验档案
---

# 参数配置：一份集中管理的实验档案

> **学习目标**：能够解释「参数配置：一份集中管理的实验档案」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：因果语言模型与 `GPT2LMHeadModel`、多轮对话的上下文拼接、采样解码（temperature / top-k / top-p / repetition penalty）、Flask 模板渲染。
>
> **所属主题**：项目实战笔记 03：企业客服聊天机器人 · 核心实现

## 本次只学这一点

```python
# parameter_config.py（节选）
class ParameterConfig:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available else 'cpu')
        self.vocab_path = '.../vocab/vocab.txt' # 词表路径
        self.train_path = '.../data/medical_train.pkl' # 训练数据
        self.valid_path = '.../data/medical_valid.pkl'
        self.config_json = '.../config/config.json' # 模型结构
        self.save_model_path = '.../save_model1'
        self.pretrained_model = '' # 留空 = 从零初始化，不加载官方 GPT2 权重
        self.ignore_index = -100 # 填充位不算 loss
        self.max_history_len = 3 # 历史保留轮数
        self.max_len = 300 # 单轮最大生成长度
        self.repetition_penalty = 10.0 # 重复惩罚
        self.topk = 4 # top-k 采样的 k
        self.batch_size = 4
        self.epochs = 4
        self.lr = 2.6e-5
        self.eps = 1.0e-09
        self.max_grad_norm = 4.0
        self.gradient_accumulation_steps = 4
        self.warmup_steps = 100
```

**为什么要单独搞一个类，而不是散落的常量**：训练超参、路径、解码参数都是"实验变量"。集中在一处，才能一眼看出"这次实验和上次差在哪"，也才好用命令行覆盖、写进实验记录。这是把个人脚本变成可复现实验的最小成本做法。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「参数配置：一份集中管理的实验档案」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/02-对话与生成系统/03-项目-企业客服聊天机器人.md)
