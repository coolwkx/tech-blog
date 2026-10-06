---
article_id: kp-4cc65b320d61d8fa
learning_kind: article
learning_category: 04-dl
learning_direction: practice
learning_topic: topic-ae2a0b64784b
learning_sourceId: ae2a0b64784b
learning_order: 1
learning_objective: 理解并验证：动态图 vs 静态图：框架的分水岭
---

# 动态图 vs 静态图：框架的分水岭

> **学习目标**：能够解释「动态图 vs 静态图：框架的分水岭」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：会 Python（类、`with`、装饰器）；知道张量与矩阵乘法；了解前向传播、损失函数、梯度下降与链式法则（参见本目录 01 反向传播与计算图、02 优化与训练技巧）。
>
> **所属主题**：-深度学习框架实践 · 核心思想

## 本次只学这一点

《神经网络与深度学习》4.5.3 节讲得最清楚：计算图分**静态计算图**（编译时构建、运行时不可改变）与**动态计算图**（运行时动态构建）。静态图构建期可优化、并行强，但灵活性差；动态图不易优化、输入结构不一致时难并行，但**灵活性高**。书中点名：Theano 与 TensorFlow 1.x 用静态图，DyNet、Chainer、PyTorch 用动态图；TensorFlow 2.0 之后也支持动态图。

| 框架 | 计算图模式 | 调试体验 | 部署/生态 | 社区与适合人群 |
| --- | --- | --- | --- | --- |
| **PyTorch** | 动态图（eager），可用 `torch.compile`/`torch.export` 补静态优化 | 最好：就是普通 Python，`pdb`/`print` 直接可用 | TorchScript / torch.export + ONNX + ExecuTorch，研究转生产链路成熟 | 学术界与工业界主流，论文复现首选；初学者也最容易上手 |
| **TensorFlow 2.x** | 默认 eager，`@tf.function` 转静态图 | 尚可，但 `@tf.function` 内的 Python 副作用会失效 | TF Serving / TF Lite / TF.js，端侧与部署最完整 | 大厂生产部署、安卓端侧、需要 TFX 的团队 |
| **Keras** | 高层 API（3.x 起支持 TF/JAX/PyTorch 多后端） | 好，抽象层级最高 | 跟随所选后端 | 教学、快速原型；不适合需要精细控制梯度的研究 |
| **PaddlePaddle（飞桨）** | 同时支持动态图与静态图 | 好，中文文档齐全 | 自研推理引擎、Paddle Serving/Lite，国产化部署完整 | 国内产业落地、需要中文文档与国产硬件适配的团队 |

> 归纳：**动态图赢在开发效率，静态图赢在极致性能与部署**。PyTorch 用 eager 保证好用，再用 `torch.compile`/`torch.export` 捕获图补性能；今天选型基本是"默认 PyTorch，端侧与服务化再看 TensorFlow Lite 或 Paddle Lite"。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「动态图 vs 静态图：框架的分水岭」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/02-优化与训练/07-深度学习框架实践.md)
