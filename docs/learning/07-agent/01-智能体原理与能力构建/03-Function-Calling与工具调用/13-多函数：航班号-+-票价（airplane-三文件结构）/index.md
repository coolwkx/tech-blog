---
article_id: kp-ec3b35237a325bfe
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-9a522c2cae70
learning_sourceId: 9a522c2cae70
learning_order: 12
learning_objective: 理解并验证：多函数：航班号 + 票价（airplane 三文件结构）
---

# 多函数：航班号 + 票价（airplane 三文件结构）

> **学习目标**：能够解释「多函数：航班号 + 票价（airplane 三文件结构）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 Action 环节、[../llm/05-大模型API与调用实践.md](../../../../../06-llm/06-提示工程/05-大模型API与调用实践.md) 的 `messages` 角色约定。
>
> **所属主题**：-Function-Calling与工具调用 · 可运行示例

## 本次只学这一点

这里把多函数示例拆成三个文件：`muti_utils.py`（函数与分发）、`airplane_function_tools.py`（tool schema）、`muti_function_zhipu.py`（主逻辑）。合并后的最小可运行版本：

**依赖**：标准库（模型调用部分见 3.1）。

```python
"""Function Calling 实现数据库查询。

依赖：pip install pymysql
安全提示：生产环境必须使用只读账号，并校验 query 只包含 SELECT。
"""

import json
import re

import pymysql

database_schema_string = """
CREATE TABLE `emp` (
`empno` int DEFAULT NULL, -- 员工编号
`ename` varchar(50) DEFAULT NULL, -- 员工姓名
`job` varchar(50) DEFAULT NULL, -- 员工工作
`mgr` int DEFAULT NULL, -- 员工领导
`hiredate` date DEFAULT NULL, -- 员工入职日期
`sal` int DEFAULT NULL, -- 员工的月薪
`comm` int DEFAULT NULL, -- 员工年终奖
`deptno` int DEFAULT NULL -- 员工部门编号
);
CREATE TABLE `DEPT` (
`DEPTNO` int NOT NULL, -- 部门编码
`DNAME` varchar(14) DEFAULT NULL, -- 部门名称
`LOC` varchar(13) DEFAULT NULL, -- 地点
PRIMARY KEY (`DEPTNO`)
);
"""

def ask_database(query):
    """连接数据库，进行查询"""
    if not re.match(r"^\s*select\b", query, flags=re.IGNORECASE):
        return json.dumps({"error": "仅允许 SELECT 查询"}, ensure_ascii=False)
    if ";" in query.rstrip().rstrip(";"):
        return json.dumps({"error": "禁止多语句执行"}, ensure_ascii=False)

    conn = pymysql.connect(
    host="localhost", port=3306, user="root", password="123456",
    database="it_heima", charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return json.dumps(result, ensure_ascii=False, default=str)
    finally:
        conn.close()

        tools = [
        {
        "type": "function",
        "function": {
        "name": "ask_database",
        "description": (
        "使用此函数回答业务问题，要求输出是一个SQL查询语句。"
        "SQL查询提取信息以回答用户的问题。"
        "查询应该以纯文本返回，而不是JSON。"
        "SQL应该使用以下数据库模式编写: %s" % database_schema_string
        ),
        "parameters": {
        "type": "object",
        "properties": {
        "query": {"type": "string", "description": "需要执行的 SQL 语句"}
        },
        "required": ["query"],
        },
        },
        }
        ]

        available_functions = {"ask_database": ask_database}

        def parse_response(response):
            """根据模型回复决定是否调用工具，返回工具执行结果"""
            message = response.choices[0].message
            if not message.tool_calls:
                return None
            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            return available_functions[tool_call.function.name](**args)

        if __name__ == "__main__":
            print(ask_database("SELECT ename, sal FROM emp ORDER BY sal DESC LIMIT 1"))
```

预期输出：

```text
第 1 轮结果: {"date": "2024-04-02", "number": "1123"}
第 2 轮结果: {"ticket_price": "668"}
```

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「多函数：航班号 + 票价（airplane 三文件结构）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md)
