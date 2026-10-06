---
article_id: kp-eb350d1bd0d7ce55
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-757657a4bcd5
learning_sourceId: 757657a4bcd5
learning_order: 9
learning_objective: 理解并验证：示例二：忠实度近似与多轮对话整轨判分
---

# 示例二：忠实度近似与多轮对话整轨判分

> **学习目标**：能够解释「示例二：忠实度近似与多轮对话整轨判分」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[06-RAG作为Agent的知识获取手段](../../../../../07-agent/03-记忆与多智能体/06-RAG作为Agent的知识获取手段.md) 的检索链路、[02-评测指标设计](../../../../../07-agent/05-评测/02-评测指标设计.md) 的指标口径、[03-评测方法-单元测试与LLM即裁判](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md) 的 Judge 校准。
>
> **所属主题**：-RAG与多轮对话评测 · 可运行示例

## 本次只学这一点

```python
"""忠实度近似 + 多轮对话评测（指代消解 / 整轨完成度 / 轮次效率）。

依赖：仅标准库。

注意：faithfulness 这里用「词重叠近似（token-overlap proxy）」实现，它只是一个
可复现的演示。它无法区分「同义改写」与「无依据编造」，也不能处理否定与条件句。
生产环境应换成 NLI 模型或 LLM 蕴含判断，并像 03 篇那样先校准 Judge。
"""

import re
from typing import Dict, List, Sequence

STOPWORDS = frozenset(
    "的 了 是 在 和 与 也 都 就 而 及 或 对 为 上 下 中 这个 那个 我们 你 我 "
    "a an the is are was were of in on at to and or for with it this that".split()
)


def _tokens(text: str) -> set:
    """粗粒度分词：英文按词、中文按字，去掉停用词。"""
    words = re.findall(r"[a-zA-Z0-9]+|[\u4e00-\u9fff]", text)
    return {w.lower() for w in words if w.lower() not in STOPWORDS}


def split_claims(answer: str) -> List[str]:
    """按中英文句末标点切分原子声明。"""
    parts = re.split(r"[。！？；;!?\n]+", answer)
    return [p.strip() for p in parts if p.strip()]


def faithfulness(answer: str, context: str,
                 threshold: float = 0.6) -> Dict[str, object]:
    """演示用的忠实度：claim 与其来源上下文词集的重叠率是否达标。"""
    ctx = _tokens(context)
    claims = split_claims(answer)
    supported = []
    for claim in claims:
        toks = _tokens(claim)
        overlap = len(toks & ctx) / len(toks) if toks else 0.0
        supported.append(overlap >= threshold)
    n = len(claims)
    return {
        "faithfulness": round(sum(supported) / n, 4) if n else 0.0,
        "n_claims": n,
        "unsupported": [claims[i] for i, ok in enumerate(supported) if not ok],
    }


def coreference_accuracy(turns: Sequence[Dict]) -> Dict[str, object]:
    """指代消解准确率：只看带期望实体的轮次。"""
    checked = [t for t in turns if t.get("expected_entity")]
    if not checked:
        return {"accuracy": 1.0, "n": 0, "errors": []}
    errors = [t["turn"] for t in checked
              if t.get("resolved_entity") != t["expected_entity"]]
    return {"accuracy": round(1 - len(errors) / len(checked), 4),
            "n": len(checked), "errors": errors}


def dialogue_completion(dialogue: Sequence[Dict], goal_state: Dict[str, str],
                        final_state: Dict[str, str],
                        min_turns: int) -> Dict[str, object]:
    """整轨判分：任务完成度 + 轮次效率。"""
    keys = list(goal_state)
    matched = sum(1 for k in keys if final_state.get(k) == goal_state[k])
    used = len(dialogue)
    mismatched = {k: (goal_state[k], final_state.get(k))
                  for k in keys if final_state.get(k) != goal_state[k]}
    return {
        "completed": matched == len(keys),
        "completion": round(matched / len(keys), 4) if keys else 1.0,
        "mismatched": mismatched,
        "turns_used": used,
        "min_turns": min_turns,
        "turn_efficiency": round(min_turns / used, 4) if used else 0.0,
    }


CONTEXT = (
    "H-102 酒店位于北京市朝阳区，共有 180 间客房，入住时间为 14:00，"
    "退房时间为 12:00，配有健身房和室内泳池。"
    "H-103 酒店位于北京市海淀区，共有 90 间客房，不提供健身房。"
)
ANSWER = (
    "H-102 酒店位于北京市朝阳区，配有健身房。"
    "H-102 酒店距离首都机场 12 公里。"
    "H-102 酒店共有 240 间客房。"
)

DIALOGUE: List[Dict] = [
    {"turn": 1, "user": "帮我订北京 6 月 1 日的酒店"},
    {"turn": 2, "user": "住 2 晚，两个人"},
    {"turn": 3, "user": "有什么推荐的"},
    {"turn": 4, "user": "那就订 H-102 吧"},
    {"turn": 5, "user": "改成三个人"},
    {"turn": 6, "user": "那个酒店有健身房吗",
     "expected_entity": "H-102", "resolved_entity": "H-103"},
]

GOAL_STATE = {"hotel": "H-102", "checkin": "2024-06-01",
              "nights": "2", "guests": "3"}
FINAL_STATE = {"hotel": "H-102", "checkin": "2024-06-01",
               "nights": "2", "guests": "2"}      # 第 5 轮的约束被遗忘


def main() -> None:
    print("\n=== 1) 忠实度（词重叠近似，生产应换 NLI / LLM 蕴含判断）===")
    f = faithfulness(ANSWER, CONTEXT)
    print("  faithfulness = %.4f（%d 条 claim，%d 条无依据）"
          % (f["faithfulness"], f["n_claims"], len(f["unsupported"])))
    for claim in f["unsupported"]:
        print("    未支撑：%s" % claim)
    print("  说明：『距离首都机场 12 公里』在上下文中不存在 → 被正确识别为编造。")

    print("\n  ▼ 词重叠近似的失效点（为什么生产必须换 NLI / LLM）")
    wrong = "H-102 酒店共有 240 间客房"
    toks, ctx = _tokens(wrong), _tokens(CONTEXT)
    print("    claim: %s" % wrong)
    print("    与上下文的重叠率 = %.2f → 被判为「有支撑」"
          % (len(toks & ctx) / len(toks)))
    print("    但上下文写的是 180 间 —— 这是数值矛盾，不是「无依据」。")
    print("    词重叠无法识别否定与数值冲突，所以这个指标只是演示用的近似。")

    print("\n=== 2) 多轮对话：指代消解 ===")
    coref = coreference_accuracy(DIALOGUE)
    print("  检查轮次 n=%d，指代消解准确率 = %.4f，出错轮次 = %s"
          % (coref["n"], coref["accuracy"], coref["errors"] or "无"))

    print("\n=== 3) 多轮对话：整轨判分 ===")
    d = dialogue_completion(DIALOGUE, GOAL_STATE, FINAL_STATE, min_turns=4)
    print("  是否完成目标：%s   完成度 = %.4f" % (d["completed"], d["completion"]))
    print("  不一致的约束：%s" % d["mismatched"])
    print("  轮次效率：用了 %d 轮 / 最少 %d 轮 = %.3f"
          % (d["turns_used"], d["min_turns"], d["turn_efficiency"]))
    print("\n  失败归因：第 5 轮用户把人数从 2 改成 3，Agent 口头确认了，")
    print("  但最终提交的订单仍是 guests=2 —— 这是典型的『遗忘型失败』。")
    print("  逐轮判分会判它为通过（每轮回复都合理），只有整轨判分能抓到。")


if __name__ == "__main__":
    main()
```

预期结果：`faithfulness = 0.6667`——3 条 claim 中 1 条被判为无依据；指代消解准确率为 **0.0**（第 6 轮把「那个酒店」解析成了 H-103）；整轨判分 **未完成**（`guests` 目标 3、实际 2）。三个指标分别指向三类不同的问题——**编造、指代错误、约束遗忘**——这正是分维度评测的意义。

同时注意那个「失效点」输出：`H-102 酒店共有 240 间客房` 与上下文的重叠率很高，被词重叠近似判为「有支撑」，但上下文写的是 180 间——**这是数值矛盾，不是无依据**。词重叠无法识别否定与数值冲突，所以生产环境必须换成 NLI 模型或 LLM 蕴含判断（并像 [03](../../../../../07-agent/05-评测/03-评测方法-单元测试与LLM即裁判.md) 那样先校准 Judge）。这个反例本身说明：**任何自动指标都要先明确它能捕捉哪一类错误、漏掉哪一类错误**，再决定要不要用它做门禁。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/05-评测/05-RAG与多轮对话评测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「示例二：忠实度近似与多轮对话整轨判分」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/05-评测/05-RAG与多轮对话评测.md)
