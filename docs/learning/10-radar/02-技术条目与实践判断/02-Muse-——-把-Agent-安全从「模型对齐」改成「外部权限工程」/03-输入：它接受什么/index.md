---
article_id: kp-e76d8ee7eb2ec107
learning_kind: article
learning_category: 10-radar
learning_direction: practice
learning_topic: topic-ce0fb9ab9b60
learning_sourceId: ce0fb9ab9b60
learning_order: 2
learning_objective: 理解并验证：输入：它接受什么
---

# 输入：它接受什么

> **学习目标**：能够解释「输入：它接受什么」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：先了解本主题的基本术语；示例环境与背景见综合原文。
>
> **所属主题**：Muse —— 把 Agent 安全从「模型对齐」改成「外部权限工程」 · 核心机制拆解

## 本次只学这一点

自然语言任务，支持多步与长时任务。用户不需要保持 App 在前台——任务在云端后台执行，完成后主动回报。它同时从 Meta 自有生态获取上下文（社交关系链、用户收藏的内容），并从连接器获取外部服务能力。

| 连接器类别 | 已接入服务（公开口径） |
| --- | --- |
| 支付 | Stripe、Shop Pay、PayPal、Lync |
| 零售 | Walmart、Best Buy、Gap、Sephora、Wayfair，以及 Shopify 全量商品目录 |
| 出行与生活 | Expedia、Instacart（当时标注即将上线） |
| 效率工具 | GitHub、Notion、Granola、Google Drive |

没有公开 API 的网站，靠浏览器模拟人类操作完成。官方强调**模型本身看不到密码和支付方式**，凭据存放在安全存储中仅用于认证。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../10-radar/02-条目/2026-09-Muse-个人Agent.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「输入：它接受什么」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../10-radar/02-条目/2026-09-Muse-个人Agent.md)
