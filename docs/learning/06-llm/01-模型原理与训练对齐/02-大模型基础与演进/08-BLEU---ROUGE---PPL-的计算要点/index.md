---
article_id: kp-a3ea02267ea2417c
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-6495f5dc2b1b
learning_sourceId: 6495f5dc2b1b
learning_order: 7
learning_objective: 理解并验证：BLEU / ROUGE / PPL 的计算要点
---

# BLEU / ROUGE / PPL 的计算要点

> **学习目标**：能够解释「BLEU / ROUGE / PPL 的计算要点」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：概率论中的链式法则与条件概率、softmax、交叉熵、Python 基础（列表/字典/循环）。
>
> **所属主题**：-大模型基础与演进 · 关键机制

## 本次只学这一点

**BLEU**：分别统计 candidate 与 reference 的 n-gram（实践中 $N=1\sim4$），计算「匹配的 n-gram 个数 / candidate 中 n-gram 个数」，再对各阶 n-gram 做加权平均（几何平均 + 简短惩罚）。

以 `candidate: it is a nice day today`、`reference: today is a nice day` 为例：

| n-gram | 匹配情况 | 匹配度 |
|---|---|---|
| 1-gram | {today, is, a, nice, day} 匹配 | 5/6 |
| 2-gram | {is a, a nice, nice day} 匹配 | 3/5 |
| 3-gram | {is a nice, a nice day} 匹配 | 2/4 |
| 4-gram | {is a nice day} 匹配 | 1/3 |

**BLEU 的致命缺陷与修正**：极端例子 `candidate: the the the the`、`reference: the cat is standing on the ground`，若按 1-gram 朴素匹配匹配度为 1，显然不合理。修正办法是**截断（clip）**：先取该词在参考句中出现的最大次数 $s_k$，再与候选句中的出现次数 $c_k$ 取较小值。

**ROUGE**：与 BLEU 非常类似，**区别在于 ROUGE 基于召回率，BLEU 更看重准确率**。ROUGE-N 把生成结果与标准结果按 n-gram 拆分后计算召回率；同一例子中 ROUGE-1 匹配度为 5/5=1（生成内容覆盖了参考文本所有单词）。ROUGE 家族包括 ROUGE-N、ROUGE-L、ROUGE-W、ROUGE-S。

**PPL（困惑度）**：用来度量概率分布/概率模型预测样本的好坏程度，**句子概率越大，语言模型越好，困惑度越小**。

$$\mathrm{PPL} = \exp\left(-\frac{1}{N}\sum_{i=1}^{N}\ln p(w_i)\right)$$

直觉理解：PPL 可以近似看成「模型在每个位置上平均要在多少个候选词里犹豫」。等价地，PPL = $2^{H}$（$H$ 为以 2 为底的交叉熵），所以**降低 PPL 本质上就是降低交叉熵**。

> 请注意一个常见混淆：BLEU/ROUGE 衡量的是「生成结果 vs 参考文本」的相似度（需要参考答案），PPL 衡量的是「模型对文本的预测能力」（**不需要**参考答案），三者用途不同，不能互相替代。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「BLEU / ROUGE / PPL 的计算要点」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/01-架构与预训练/01-大模型基础与演进.md)
