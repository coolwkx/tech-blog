---
article_id: kp-b1c6e2ac006da820
learning_kind: article
learning_category: 03-ml
learning_direction: practice
learning_topic: topic-fb8e5382c0c0
learning_sourceId: fb8e5382c0c0
learning_order: 16
learning_objective: 理解并验证：日志工具类（可直接拷贝）
---

# 日志工具类（可直接拷贝）

> **学习目标**：能够解释「日志工具类（可直接拷贝）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：pandas 时间序列操作（`str` 切片、`shift`、`to_timedelta`）、特征工程五大组成（见 [09-特征工程](../../../../../03-ml/01-基础与特征工程/09-特征工程.md)）、XGBoost 与网格搜索（见 [06-集成学习](../../../../../03-ml/04-集成与无监督/06-集成学习.md)、[08-模型评估与调优](../../../../../03-ml/03-评估与调优/08-模型评估与调优.md)）。
>
> **所属主题**：数据挖掘案例：电力负荷预测 · 可运行示例

## 本次只学这一点

```python
# -*- coding: utf-8 -*-
"""utils/log.py —— 日志工具类，非核心代码，建议直接拷贝到项目中"""
import logging
import os

class Logger(object):
 # 日志级别关系映射
 level_relations = {
 "debug": logging.DEBUG,
 "info": logging.INFO,
 "warning": logging.WARNING,
 "error": logging.ERROR,
 "crit": logging.CRITICAL,
 }

def __init__(self, root_path, log_name, level="info",
fmt="%(asctime)s - %(levelname)s: %(message)s"):
 self.root_path = root_path
 self.log_name = log_name
 self.fmt = fmt
 self.logger = logging.getLogger(log_name)
 self.logger.setLevel(self.level_relations.get(level))

def get_logger(self):
 path = os.path.join(self.root_path, "log")
 os.makedirs(path, exist_ok=True)
 file_name = os.path.join(path, self.log_name + ".log")
 rotate_handler = logging.FileHandler(file_name, encoding="utf-8", mode="a")
 rotate_handler.setFormatter(logging.Formatter(self.fmt))
 self.logger.addHandler(rotate_handler)
 return self.logger
```

> **一个实际使用中的坑**：`logging.getLogger(log_name)` 是**全局单例**，同一个 `log_name` 重复调用 `get_logger` 会**重复添加 Handler**，导致同一条日志被写多次。项目里通常靠"日志文件名带时间戳"（`"train_" + datetime.now.strftime('%Y%m%d%H%M%S')`）来避免 `log_name` 相同。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「日志工具类（可直接拷贝）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../03-ml/06-案例与面试/10-数据挖掘案例-电力负荷预测.md)
