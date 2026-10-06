---
article_id: kp-6cee8ff2609756e8
learning_kind: article
learning_category: 05-nlp
learning_direction: practice
learning_topic: topic-d7bbe1de9b00
learning_sourceId: d7bbe1de9b00
learning_order: 7
learning_objective: 理解并验证：GRU：更精简的版本
---

# GRU：更精简的版本

> **学习目标**：能够解释「GRU：更精简的版本」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：第 04 篇词向量与 `nn.Embedding`、第 05 篇文本分类流水线、PyTorch `nn.Module` 与 `Dataset/DataLoader`、链式法则与反向传播。
>
> **所属主题**：RNN 与 LSTM 文本建模 · 方法细节

## 本次只学这一点

GRU 把 LSTM 的三个门合并为两个，并把细胞状态与隐状态合并：

$$
\begin{aligned}
z_t &= \sigma\big(W_z \cdot [h_{t-1}, x_t]\big) &&\text{更新门}\\
r_t &= \sigma\big(W_r \cdot [h_{t-1}, x_t]\big) &&\text{重置门}\\
\tilde{h}_t &= \tanh\big(W \cdot [r_t \odot h_{t-1}, x_t]\big) &&\text{候选隐状态}\\
h_t &= (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t &&\text{输出}
\end{aligned}
$$

| 对比项 | LSTM | GRU |
|--------|------|-----|
| 门数 | 3（遗忘 / 输入 / 输出） | 2（更新 / 重置） |
| 状态 | 隐状态 $h$ + 细胞状态 $c$ | 只有隐状态 $h$ |
| 参数量 | 基准 | 约为 LSTM 的 **2/3** |
| 训练速度 | 较慢 | 较快 |
| 小数据表现 | 略好（表达力更强） | 略好（参数少、不易过拟合） |
| 大数据表现 | 通常略优 | 接近，常打平 |

人名分类案例给出的结论与经验一致：**RNN 快但精度低，LSTM 精度高但慢，GRU 居中且大多数情况下与 LSTM 打平**。实践中建议三个都跑一遍看验证集曲线，不要预设答案（见小结中「优缺点」部分：GRU 相比 LSTM 结构更简单，同样能缓解梯度消失；但 RNN 系列都无法并行，数据量大时效率低）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「GRU：更精简的版本」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../05-nlp/02-序列建模与Transformer/07-RNN与LSTM文本建模.md)
