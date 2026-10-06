---
article_id: kp-87e9e6bbfdcea805
learning_kind: article
learning_category: 06-llm
learning_direction: foundations
learning_topic: topic-e0e1aefc5818
learning_sourceId: e0e1aefc5818
learning_order: 10
learning_objective: 理解并验证：评估脚本骨架
---

# 评估脚本骨架

> **学习目标**：能够解释「评估脚本骨架」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：监督微调（SFT）的基本流程、LoRA 等参数高效微调方法、分类与生成的常用指标（acc / P / R / F1 / ROUGE / 通过率）、训练集-验证集切分与交叉验证。
>
> **所属主题**：-微调效果评估与灾难性遗忘 · 怎么设计微调对比实验

## 本次只学这一点

下面这份脚本骨架覆盖：任务指标、格式合规率、通用能力保持（遗忘度量）、过拟合检查四件事。

```python
# -*- coding: utf-8 -*-
"""微调评估脚本骨架：任务指标 + 格式合规率 + 遗忘度量 + 过拟合检查。

依赖：标准库；可选 scikit-learn（分类指标）、torch/transformers（真实推理）。
本脚本用可注入的 predict_fn 解耦模型，便于在无 GPU 环境下做逻辑自测。
"""
import json
import math
import re
from collections import Counter
from typing import Callable, Dict, List, Optional

# ---------------------------------------------------------------- 指标工具


def accuracy(preds: List[str], golds: List[str]) -> float:
    assert len(preds) == len(golds) and preds, "预测与标签长度必须一致且非空"
    return sum(p == g for p, g in zip(preds, golds)) / len(golds)


def macro_f1(preds: List[str], golds: List[str]) -> float:
    """不依赖 sklearn 的宏平均 F1，便于在最小环境里跑。"""
    labels = sorted(set(golds) | set(preds))
    f1s = []
    for lb in labels:
        tp = sum(p == lb and g == lb for p, g in zip(preds, golds))
        fp = sum(p == lb and g != lb for p, g in zip(preds, golds))
        fn = sum(p != lb and g == lb for p, g in zip(preds, golds))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(0.0 if precision + recall == 0
                   else 2 * precision * recall / (precision + recall))
    return sum(f1s) / len(f1s) if f1s else 0.0


def bleu_like(pred: str, gold: str, n: int = 2) -> float:
    """简化的 n-gram 精确率，用于生成任务的快速对比（不要当作 BLEU 汇报）。"""
    def grams(s, k):
        t = re.sub(r"\s+", "", s)
        return Counter(t[i:i + k] for i in range(max(len(t) - k + 1, 0)))
    pred_g, gold_g = grams(pred, n), grams(gold, n)
    if not pred_g or not gold_g:
        return 0.0
    overlap = sum((pred_g & gold_g).values())
    return overlap / max(sum(pred_g.values()), 1)


# ---------------------------------------------------------------- 格式合规


def json_compliance(outputs: List[str], required_keys: Optional[List[str]] = None) -> Dict:
    """统计 JSON 可解析率与必填字段齐全率，并返回失败样本下标。"""
    required_keys = required_keys or []
    ok, bad = 0, []
    for i, o in enumerate(outputs):
        try:
            obj = json.loads(o)
        except (json.JSONDecodeError, TypeError):
            bad.append(i)
            continue
        if required_keys and not all(k in obj for k in required_keys):
            bad.append(i)
            continue
        ok += 1
    return {
        "json_parse_rate": ok / len(outputs) if outputs else 0.0,
        "failed_indices": bad,
        "n_failed": len(bad),
    }


# ---------------------------------------------------------------- 遗忘度量


def forgetting_report(before: Dict[str, float], after: Dict[str, float]) -> Dict:
    """通用基准回测：给出每个基准的相对下降率与总体遗忘度量。

    before / after: {"mmlu": 0.612, "gsm8k": 0.341, ...}
    """
    assert before.keys() == after.keys(), "两次评测必须使用同一组基准"
    per_bench, drops = {}, []
    for name, b in before.items():
        a = after[name]
        if b == 0:
            per_bench[name] = {"before": b, "after": a, "relative_drop": None}
            continue
        rel = (b - a) / b
        per_bench[name] = {"before": b, "after": a, "relative_drop": round(rel, 4)}
        drops.append(rel)
    return {
        "per_benchmark": per_bench,
        "mean_relative_drop": round(sum(drops) / len(drops), 4) if drops else None,
        "max_relative_drop": round(max(drops), 4) if drops else None,
    }


def retention_score(before: Dict[str, float], after: Dict[str, float]) -> float:
    """综合保持率：几何平均，避免某一项崩掉被平均数掩盖。"""
    ratios = [max(a, 1e-6) / max(b, 1e-6) for b, a in zip(before.values(), after.values())]
    return math.exp(sum(math.log(r) for r in ratios) / len(ratios))


# ---------------------------------------------------------------- 过拟合检查


def overfit_signals(train_loss: List[float], eval_loss: List[float],
                    eval_metric: List[float]) -> Dict:
    """从训练曲线里提取过拟合信号（按 epoch 或固定步长采样）。"""
    assert len(train_loss) == len(eval_loss) == len(eval_metric), "三条曲线长度必须一致"
    best_epoch = max(range(len(eval_metric)), key=lambda i: eval_metric[i])
    gap = [e - t for t, e in zip(train_loss, eval_loss)]
    return {
        "best_epoch": best_epoch,
        "epochs_after_best": len(eval_metric) - 1 - best_epoch,
        "final_gap": round(gap[-1], 4),
        "min_gap": round(min(gap), 4),
        "eval_degraded": eval_metric[-1] < eval_metric[best_epoch],
        "verdict": ("疑似过拟合：验证指标在达到峰值后回落（下降 %.4f）"
                    % (eval_metric[best_epoch] - eval_metric[-1]))
        if eval_metric[-1] < eval_metric[best_epoch] * 0.995 else "未见明显过拟合",
    }


def verbatim_rate(outputs: List[str], train_texts: List[str], n: int = 13) -> float:
    """复述率：输出中是否存在与任一训练样本共享长度 n 的 n-gram。"""
    train_grams = set()
    for t in train_texts:
        t = re.sub(r"\s+", "", t)
        train_grams.update(t[i:i + n] for i in range(max(len(t) - n + 1, 0)))
    if not train_grams:
        return 0.0
    hit = 0
    for o in outputs:
        o = re.sub(r"\s+", "", o)
        if any(o[i:i + n] in train_grams for i in range(max(len(o) - n + 1, 0))):
            hit += 1
    return hit / len(outputs) if outputs else 0.0


# ---------------------------------------------------------------- 统一入口

def evaluate_all(predict_fn: Callable[[List[str]], List[str]],
                 task: Dict,
                 general_before: Optional[Dict[str, float]] = None,
                 general_after: Optional[Dict[str, float]] = None,
                 train_texts: Optional[List[str]] = None,
                 required_keys: Optional[List[str]] = None) -> Dict:
    """task: {"inputs": [...], "golds": [...], "kind": "classification" | "generation"}"""
    outputs = predict_fn(task["inputs"])
    report = {"n_samples": len(outputs)}

    if task["kind"] == "classification":
        report["task"] = {"accuracy": round(accuracy(outputs, task["golds"]), 4),
                          "macro_f1": round(macro_f1(outputs, task["golds"]), 4)}
    else:
        scores = [bleu_like(o, g) for o, g in zip(outputs, task["golds"])]
        report["task"] = {"overlap": round(sum(scores) / len(scores), 4)}

    report["format"] = json_compliance(outputs, required_keys)

    if general_before and general_after:
        report["forgetting"] = forgetting_report(general_before, general_after)
        report["retention"] = round(retention_score(general_before, general_after), 4)

    if train_texts:
        report["verbatim_rate"] = round(verbatim_rate(outputs, train_texts), 4)

    return report


if __name__ == "__main__":
    demo_task = {"inputs": ["a", "b", "c"],
                 "golds": ["x", "y", "x"],
                 "kind": "classification"}
    user_reply = {"a": '{"label": "x"}', "b": "y", "c": "不是 JSON"}

    def fake_predict_fn(inputs):
        return [user_reply[i] for i in inputs]

    print(json.dumps(evaluate_all(fake_predict_fn, demo_task,
                                  required_keys=["label"]),
                     ensure_ascii=False, indent=2))
```

> **说明**：`retention_score` 用几何平均是为了避免「某一项崩溃被其他项的提升掩盖」；`verbatim_rate` 用长度 13 的 n-gram 是为了降低偶然重合率（长文本可放宽到 20）。以上实现基于通用工程实践整理，未在本机实测运行（本机无 GPU / `transformers`）。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/02-微调与对齐/07-微调效果评估与灾难性遗忘.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「评估脚本骨架」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/02-微调与对齐/07-微调效果评估与灾难性遗忘.md)
