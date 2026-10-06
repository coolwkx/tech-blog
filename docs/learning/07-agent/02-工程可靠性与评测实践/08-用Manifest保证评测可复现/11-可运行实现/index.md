---
article_id: kp-7f02d8d15785cd00
learning_kind: article
learning_category: 07-agent
learning_direction: practice
learning_topic: topic-cf848e0fe35f
learning_sourceId: cf848e0fe35f
learning_order: 10
learning_objective: 理解并验证：可运行实现
---

# 可运行实现

> **学习目标**：能够解释「可运行实现」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01 篇](../../../../../07-agent/06-评测实战/01-项目复盘-AgentEvalLab.md) 的六段流水线与四道一致性闸门、SHA-256 与规范化（canonicalization）的基本概念、JSON/JSONL 基础。
>
> **所属主题**：-用Manifest保证评测可复现 · 数据集哈希与提示词哈希的计算方式

## 本次只学这一点

```python
"""复现 agent-eval-lab 的两类哈希口径：提示词哈希与数据集哈希。

只依赖标准库。核心约定：先定义规范化规则，再哈希。
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any, Iterable


class HashError(ValueError):
    """哈希输入不满足规范化前置条件。"""


def sha256_text(text: str) -> str:
    """返回 `sha256:<64 位小写十六进制>`，与 Manifest 的格式约束一致。"""
    if not isinstance(text, str):
        raise HashError("sha256_text 只接受 str")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def canonical_json(value: Any) -> str:
    """稳定序列化：键排序、无多余空白、不转义非 ASCII。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ------------------------------------------------------------- 提示词哈希
def normalize_prompt(text: str) -> str:
    """提示词规范化：统一换行、NFC 归一、去行尾空白、单个结尾换行。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFC", text)
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def prompt_hash(text: str) -> str:
    """推荐口径：对规范化后的提示词取哈希（结尾换行不影响结果）。"""
    return sha256_text(normalize_prompt(text))


def prompt_hash_raw(text: str) -> str:
    """仓库公开示例采用的口径：直接对原始字符串取哈希。"""
    return sha256_text(text)


# ------------------------------------------------------------- 数据集哈希
def dataset_content_hash(records: Iterable[Any]) -> str:
    """内容哈希：记录规范化后排序再整体哈希，与行的物理顺序无关。"""
    normalized = sorted(canonical_json(record) for record in records)
    if not normalized:
        raise HashError("数据集为空，拒绝生成哈希")
    return sha256_text("\n".join(normalized) + "\n")


def dataset_content_hash_from_jsonl(path: str | Path) -> str:
    """从 JSONL 文件读内容哈希：跳过空行与 `#` 注释行，去 BOM，显式 UTF-8。"""
    text = Path(path).read_text(encoding="utf-8").lstrip("\ufeff")
    records = [json.loads(line) for line in text.split("\n")
               if line.strip() and not line.strip().startswith("#")]
    return dataset_content_hash(records)


def dataset_id_hash(identifier: str) -> str:
    """标识哈希：只哈希稳定数据集 ID。仓库公开示例用的是这一种。"""
    if not identifier.strip():
        raise HashError("数据集标识不能为空")
    return sha256_text(identifier)


if __name__ == "__main__":
    prompt = "Evaluate each synthetic trajectory using evidence-bound completion rules."
    identifier = "agent-eval-lab-public-synthetic-v1"
    assert prompt_hash_raw(prompt) == (
        "sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc")
    assert dataset_id_hash(identifier) == (
        "sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2")
    # 规范化后结尾换行、\r\n 不改变结果；内容哈希与行序、键序无关
    assert prompt_hash(prompt) == prompt_hash(prompt + "\n") == prompt_hash(prompt + "\r\n")
    assert dataset_content_hash([{"taskId": "t1", "seed": 1}, {"seed": 2, "taskId": "t2"}]) == \
        dataset_content_hash([{"seed": 2, "taskId": "t2"}, {"taskId": "t1", "seed": 1}])
    print("self-check OK")
    print("promptHash(raw)   =", prompt_hash_raw(prompt))
    print("promptHash(norm)  =", prompt_hash(prompt))
    print("dataset.hash(id)  =", dataset_id_hash(identifier))
    print("dataset.hash(body)=", dataset_content_hash([{"taskId": "t1", "seed": 1},
                                                       {"taskId": "t1", "seed": 2}]))
```

运行输出（两个哈希与仓库里的 Manifest **逐位相同**）：

```text
self-check OK
promptHash(raw)   = sha256:59385ca68f462dd301e9866b7e918dafd1cc466d5779d9a2d8d7acbe7091fedc
promptHash(norm)  = sha256:547a99eec715132850d9f1e2a8a16487333feaedb237270524efd881a2f72aa7
dataset.hash(id)  = sha256:af71072674c8e544ed7154cc99a7bf815c050c9dc693e2ca7ff38f783f24ddb2
dataset.hash(body)= sha256:1466fcf2593637352a821a05ed26b28cc1a81e6f16ab9466dc326ecbe5b2b5c6
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「可运行实现」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/06-评测实战/02-用Manifest保证评测可复现.md)
