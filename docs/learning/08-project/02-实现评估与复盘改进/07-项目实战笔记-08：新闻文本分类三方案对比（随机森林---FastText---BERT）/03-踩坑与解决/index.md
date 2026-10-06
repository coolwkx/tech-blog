---
article_id: kp-ac57e3786cf272cd
learning_kind: article
learning_category: 08-project
learning_direction: practice
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 16
learning_objective: 理解并验证：踩坑与解决
---

# 踩坑与解决

> **学习目标**：能够解释「踩坑与解决」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 踩坑与解决

## 本次只学这一点

| 现象 | 根因 | 解决 | 如何预防 |
| --- | --- | --- | --- |
| BERT 精度低于预期但训练正常 | 用 jieba 分词后再喂给 BERT，与预训练 WordPiece 分布不一致 | 直接调 `config.tokenizer.tokenize(content)` | **每个模型的 tokenizer 就是它的"语言"，绝不混用** |
| 服务能跑但准确率下降，且不报错 | 训练按字切分、推理按词切分（`app.py` 用 `jieba.lcut`，`train_fast.txt` 是按字生成） | 训练与推理共用**同一个**预处理函数 | 把预处理抽成独立函数；这是"训练/推理不一致"的通用解法 |
| mask 与 token_ids 长度不一致导致形状错误 | `mask` 用 `len(token_ids)`、`token_ids` 补零用 `len(token)`，依赖两者相等的隐含假设 | 用同一长度变量推导所有数组 | 多数组 pad 到同一长度时**必须基于同一变量推导** |
| 训练极慢、显存不够 | `pad_size` 用了 BERT 默认的 512，而数据平均只有 19 字 | 按分布设 `pad_size=32`（mean + 2σ） | **先跑数据分析脚本**用 mean/std 决定序列长度；注意力 O(L²) |
| 微调后效果比预训练还差 | 学习率用成从头训练的 1e-3 量级，把预训练表示"冲毁"了 | 用 5e-5 量级小学习率 | 微调学习率要比从头训练**小一到两个数量级** |
| `model.eval` 后忘切回 `train`，后续训练失效 | 评估函数内部调了 `model.eval`，训练循环没复位 | 评估后立刻 `model.train` | **凡改变模型模式的调用都要配对复位**；最好让 `evaluate` 自己负责复位 |
| LayerNorm 和 bias 也被 weight decay，训练不稳 | 优化器未分层设置参数组 | `no_decay = ["bias","LayerNorm.bias","LayerNorm.weight"]` 这组 `wd=0` | Transformer 微调标准配置；要能解释"为什么" |
| 验证准确率长时间不涨但模型实际在改善 | accuracy 离散（10000 样本最小变化 0.01%），信号太粗 | 用连续 `dev_loss` 作保存判据 | 选模型指标要**对模型改善敏感**；同时记录 acc 与 loss |
| 结果无法复现，"提升"只是随机波动 | 未固定随机种子 | `np/torch/cuda/cudnn` 四个种子全设 + `cudnn.deterministic=True` | **方案对比前必须先固定种子**，否则结论不可信 |
| 100 秒自动调参只提升 0.07 点 | FastText 对超参敏感度低 | 精力转向数据层面（切分口径、清洗） | 调参前先确认"参数是否值得调"；**先动数据，再动超参** |
| 换成分词反而降 0.79 点 | jieba 分词错误不可逆传播；按字+bigram 能学字组合 | 优先尝试"按字 + n-gram" | 短文本分类上**分词未必优于按字**，两者都要实测 |
| GPU 上量化反而变慢 | GPU 浮点算力充裕，int8 的拆包/换算成新瓶颈 | 量化只在 CPU 部署时使用 | **量化不是必然加速**，按部署硬件评估 |
| Flask 开发服务器上了生产 | `app.run` 是单进程阻塞的开发服务器 | 生产用 gunicorn / uvicorn + 多 worker | 看到 `Do not use it in a production deployment` 提示就要当真 |
| 接口返回 `__label__education` 而非 `education` | 直接返回 `res[0][0]`，没剥前缀 | `predict_name.replace('__label__', '')` | 模型输出格式与接口契约解耦，加一层转换 |

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「踩坑与解决」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
