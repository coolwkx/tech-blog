---
article_id: kp-20b7fb095cecf40e
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-8b0a9bea9dde
learning_sourceId: 8b0a9bea9dde
learning_order: 8
learning_objective: 理解并验证：延伸：模型压缩三件套
---

# 延伸：模型压缩三件套

> **学习目标**：能够解释「延伸：模型压缩三件套」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 03 篇 TF-IDF、第 05 篇文本分类流水线与评估指标、第 09 篇 BERT 微调、第 11 篇情感分析项目的工程范式。
>
> **所属主题**：NLP 项目实战：医疗文本分类 · 方法细节

## 本次只学这一点

如果业务要求「BERT 的精度 + FastText 的速度」，就需要压缩。参考项目本主题覆盖了三种手段：

| 手段 | 核心思想 | 关键 API / 公式 |
|------|----------|----------------|
| 知识蒸馏 | 让学生模型（TextCNN）学教师模型（BERT）的**软标签** | $\text{loss}=\alpha\cdot\text{hard}+\beta\cdot\text{soft}$，软标签用 KL 散度 + 温度 $T$ |
| 模型量化 | 把 FP32 权重压成 INT8 | 动态量化 `torch.quantization.quantize_dynamic` |
| 模型剪枝 | 把绝对值小的权重置 0 | `prune.l1_unstructured` / `prune.ln_structured` / `prune.remove` |

**知识蒸馏的直觉**（为什么软标签比硬标签有信息量）：

```
传统训练（只用硬标签）：真实标签 = 治疗方法(1)
 学生只学到「这是治疗方法」

蒸馏训练（用软标签）：教师输出 = 治疗方法(0.75), 病因(0.08), 临床表现(0.05)...
 学生额外学到：① 治疗方法与病因有一定相似性（可能在问「为什么用这个药」）
 ② 类别之间的关系结构
 → 泛化更好
```

蒸馏的收益量化举例：1 亿次分类请求下，纯 BERT（50ms/次）需要约 58 天，纯 TextCNN（5ms/次）只需约 5.8 天但准确率只有 90%；蒸馏后的 TextCNN 达到 92.5% 且保持 5ms——**同时兼顾性能与效率**。

剪枝的 API 要点：

```python
import torch.nn.utils.prune as prune

prune.l1_unstructured(module, name="weight", amount=0.3) # 去掉绝对值最小的 30%
prune.ln_structured(module, name="weight", amount=0.4, n=2, dim=0) # 结构化剪枝
prune.remove(module, "weight") # 永久化：把 weight_orig × weight_mask 写回 weight
```

项目源码还演示了两种更进一步的用法：

```python
# 全局剪枝：在所有层之间统一按重要性排名剪掉 20%（各层被剪比例不同）
parameters_to_prune = (
(model.conv1, 'weight'), (model.conv2, 'weight'),
(model.fc1, 'weight'), (model.fc2, 'weight'), (model.fc3, 'weight'),
)
prune.global_unstructured(parameters_to_prune,
pruning_method=prune.L1Unstructured, amount=0.2)
# 随后可逐层统计稀疏度并与全局比例核对

# 自定义剪枝规则：继承 prune.BasePruningMethod 并实现 compute_mask
class MyPruningMethod(prune.BasePruningMethod):
    PRUNING_TYPE = "unstructured"

    def compute_mask(self, t, default_mask):
        mask = default_mask.clone
        mask.view(-1)[::3] = 0 # 每 3 个参数遮掉 1 个
        return mask
```

剪枝后模块会新增 `weight_orig`（原始权重）与 `weight_mask`（0/1 掩码），实际使用的是两者相乘的结果。**不调用 `prune.remove` 就不会真正减小模型**——这是最常见的误解。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「延伸：模型压缩三件套」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/03-任务与信息抽取/12-NLP项目实战-医疗文本分类.md)
