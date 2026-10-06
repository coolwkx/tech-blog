---
article_id: kp-761ae4bcb6717ca5
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-215b0af0476d
learning_sourceId: 215b0af0476d
learning_order: 11
learning_objective: 理解并验证：统计层：McNemar 与聚类 Bootstrap
---

# 统计层：McNemar 与聚类 Bootstrap

> **学习目标**：能够解释「统计层：McNemar 与聚类 Bootstrap」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-为什么Agent评测比LLM评测难](../../../../../07-agent/05-评测/01-为什么Agent评测比LLM评测难.md) 的结果层/过程层/系统层框架与四象限判定、[07-Agent工程化与可靠性设计](../../../../../07-agent/04-评估与工程化/07-Agent工程化与可靠性设计.md) 的轨迹落盘与结构化日志、基础统计学中的二项分布与 Bootstrap 重采样。
>
> **所属主题**：-项目复盘-AgentEvalLab · 核心实现剖析

## 本次只学这一点

`comparePaired` 做三件事：严格配对、数 2×2 配对表、算两个检验。

```ts
// 配对：两侧 key 集合必须完全相同，否则抛错并列出缺失项
const baselineKeys = [...baselineByPair.keys()].sort();
const optimizedKeys = [...optimizedByPair.keys()].sort();
if (baselineKeys.join("\n") !== optimizedKeys.join("\n")) {
  throw new Error(`Unpaired results: missing optimized [...] ; missing baseline [...]`);
}
```

McNemar exact 的实现用了一条**按样本量分叉**的路径：

```ts
const discordant = failToPass + passToFail;
if (discordant === 0) return 1;                       // 完全一致 → p = 1
const lower = Math.min(failToPass, passToFail);

if (discordant <= 1_024) {                            // 常规路径：精确组合数
  let cumulative = 0;
  for (let k = 0; k <= lower; k += 1) {
    cumulative += binomialCoefficient(discordant, k) * 0.5 ** discordant;
  }
  return Math.min(1, 2 * cumulative);
}

// 大样本路径：组合数会溢出 double，改在对数空间算最大项，再按相对比值回加
let logLargestTerm = -discordant * Math.LN2;
for (let k = 1; k <= lower; k += 1) {
  logLargestTerm += Math.log(discordant - k + 1) - Math.log(k);
}
let scaledCumulative = 1, relativeTerm = 1;
for (let k = lower; k >= 1; k -= 1) {
  relativeTerm *= k / (discordant - k + 1);           // term(k-1) / term(k)
  scaledCumulative += relativeTerm;
  if (relativeTerm === 0) break;
}
return Math.min(1, 2 * Math.exp(logLargestTerm + Math.log(scaledCumulative)));
```

聚类 Bootstrap 的实现只有三十行但每一步都有理由：

```ts
// 1) 先把配对按 taskId 折叠成"任务簇"，簇内保留全部重复
const clusters = new Map<string, { baselinePassed; optimizedPassed; runs }>();
// 2) 有放回抽取任务（抽够 taskIds.length 个），簇内全部配对一起进出
for (let draw = 0; draw < taskIds.length; draw += 1) {
  const cluster = clusters.get(taskIds[Math.floor(random() * taskIds.length)]!);
  baselinePassed += cluster.baselinePassed;
  optimizedPassed += cluster.optimizedPassed;
  runs += cluster.runs;
}
// 3) 每次重采样内先池化再作差——注意是"重采样后算比率"，不是"算比率后重采样"
samples.push(optimizedPassed / runs - baselinePassed / runs);
// 4) 百分位区间
lower: percentile(samples, alpha), upper: percentile(samples, 1 - alpha)
```

第 3 步是最容易写错的地方：**分母必须跟着重采样一起变**。如果先算好每个任务的比率再重采样平均，等于默认每个任务权重相同；而池化口径下重复次数多的任务权重更大。两种口径在"各任务重复次数不一致"时会给出不同答案。

`seededRandom` 用了一个 32 位 LCG（乘 1664525、加 1013904223），默认 seed 是 `20260819`（项目创建日期）。选 LCG 而不是密码学随机数，是因为测试里要能断言 `deepEqual(first, second)`。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「统计层：McNemar 与聚类 Bootstrap」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md)
