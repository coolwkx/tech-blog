---
article_id: kp-f96f14a596c95c01
learning_kind: article
learning_category: 08-project
learning_direction: foundations
learning_topic: topic-8f6e59312d25
learning_sourceId: 8f6e59312d25
learning_order: 14
learning_objective: 理解并验证：量化：一行代码减重 257MB
---

# 量化：一行代码减重 257MB

> **学习目标**：能够解释「量化：一行代码减重 257MB」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：TF-IDF 与词袋模型、jieba 分词、`sklearn` 的 `TfidfVectorizer` / `RandomForestClassifier`、PyTorch 训练循环、BERT 的 `[CLS]` 与 attention mask。
>
> **所属主题**：项目实战笔记 08：新闻文本分类三方案对比（随机森林 / FastText / BERT） · 核心实现

## 本次只学这一点

```python
# 注意：动态量化必须在 CPU 上做，Config 里要改成 self.device = 'cpu'
model = x.Model(config)
model.load_state_dict(torch.load(config.save_path, map_location='cpu'))
quantized_model = torch.quantization.quantize_dynamic(
model, {torch.nn.Linear}, dtype=torch.qint8)
test(config, quantized_model, test_iter) # Test Acc: 91.92%
```

**`quantize_dynamic` 做了什么**：把 `nn.Linear` 换成 `DynamicQuantizedLinear`，权重 float32 → int8（4 字节 → 1 字节），推理时用整数矩阵乘法。

**为什么叫"动态"**：权重的量化范围在加载时确定（静态），**激活值的量化范围在每次推理时根据实际输入动态计算**。相比需要校准数据的"静态量化"，动态量化精度损失更小，但速度提升也少一些。**对 BERT 这种输入分布变化大的模型，动态量化更稳。**

| | FP32 | INT8 动态量化 |
| --- | --- | --- |
| Test Acc | 93.64% | 91.92% |
| 模型文件 | 基准 | **−256.6 MB** |
| 部署设备 | GPU | CPU |

**两个边界必须知道**：**动态量化只能在 CPU 上做**（所以它是面向 CPU 部署的优化）；**在 GPU 上量化有时反而更慢**——GPU 浮点算力本就充裕，int8 的拆包/缩放/反量化会成新瓶颈。**"量化 = 加速"不总成立，要看部署硬件。**

**算一笔总账**：量化掉的 1.72 个点，几乎等于 BERT 相比 FastText 挣来的全部优势（1.92 点）。若最终都要 CPU 部署，量化的 BERT（91.92%）与 FastText（91.72%）精度几乎相同，而后者快约 38 倍、小得多、还简单得多。**除非有"必须用 BERT 架构"的理由**（比如同一编码器还要做 NER、句向量、问答），否则这种场景下 FastText 是更优解。**把每个环节的收益和代价放在一起算总账，比孤立评价"BERT 比 FastText 好"更有价值。**

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「量化：一行代码减重 257MB」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../08-project/03-文本分类系统/08-项目-新闻文本分类三方案对比（随机森林FastTextBERT）.md)
