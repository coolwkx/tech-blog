---
article_id: kp-465687da68c7a111
learning_kind: article
learning_category: 07-agent
learning_direction: foundations
learning_topic: topic-3d8f081f5ed3
learning_sourceId: 3d8f081f5ed3
learning_order: 13
learning_objective: 理解并验证：用 CrewAI 编排三 Agent 流水线（Chapter 10 项目）
---

# 用 CrewAI 编排三 Agent 流水线（Chapter 10 项目）

> **学习目标**：能够解释「用 CrewAI 编排三 Agent 流水线（Chapter 10 项目）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：[02-Function-Calling与工具调用](../../../../../07-agent/02-工具与规划/02-Function-Calling与工具调用.md) 的工具协议、[01-Agent基础范式与ReAct循环](../../../../../07-agent/01-基础范式/01-Agent基础范式与ReAct循环.md) 的 ReAct 结构、[../llm/08-LangChain基础.md](../../../../../06-llm/07-检索增强RAG/08-LangChain基础.md)。
>
> **所属主题**：-LangChain与工具编排 · 可运行示例

## 本次只学这一点

**依赖**：`pip install crewai langchain langchain-community openai python-dotenv`；环境变量 `OPENAI_API_KEY`（或通过 `base_url` 指向兼容端点）。

```python
"""CrewAI 多 Agent 编排：作家 → 编辑 → 寄信人。

依赖：pip install crewai langchain-community python-dotenv
环境变量：OPENAI_API_KEY
"""

import os

from crewai import Agent, Crew, Process, Task
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import tool

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

@tool("将文本写入文档中")
def store_poesy_to_txt(content: str) -> str:
    """将编辑后的书信文本内容自动保存到 txt 文档中，返回保存状态。"""
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poie.txt")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
        return "File written to %s." % filename

    @tool("发送文本到邮件")
    def send_message() -> str:
        """读取本地书信文件，并以邮件的形式发送到指定的邮箱地址。

        为保证示例可运行，这里只打印动作而不真正发信；
        生产实现可参考 custom_tools.py 的 smtplib.SMTP_SSL 版本。
        """
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poie.txt")
        if not os.path.exists(filename):
            return "错误：本地书信文件不存在，请先保存内容。"
        return "邮件已发送（示例模式）。"

    poet = Agent(
    role="作家",
    goal="根据用户需求，创作出情感丰富的文章（最长字数不超过300个词）。",
    backstory="你作为一名著名的作家，拥有千万级别的粉丝，最擅长写情感类型的文章。",
    llm=llm,
    allow_delegation=False,
    verbose=True,
    )

    letter_writer = Agent(
    role="内容编辑",
    goal="对作家撰写的文章内容进行精心编辑。",
    backstory=(
    "作为一名经验丰富的编辑，你在编辑书信方面有多年的专业经验，"
    "你需要将作家写的文章内容整理编排成书信的样式，并将书信内容存储在本地磁盘上。"
    ),
    tools=[store_poesy_to_txt],
    llm=llm,
    allow_delegation=False,
    verbose=True,
    )

    sender = Agent(
    role="寄信人",
    goal="将编辑好的书信以邮件的形式发送给心仪的人",
    backstory="你是一名勤恳的信使，专注于将书信传递给每个人。",
    tools=[send_message],
    llm=llm,
    allow_delegation=True,
    verbose=True,
    )

    def build_crew(content):
        task1 = Task(
        description="用户需求:%s。你最后给出的答案必须是一份富含爱情表示的情书。" % content,
        agent=poet,
        )
        task2 = Task(
        description=(
        "查找任何语法错误，进行编辑和格式化（如果需要），并要求将内容保存在本地磁盘中。"
        "将内容保存到本地非常重要，你最后的答案必须是信息是否已被存储在本地磁盘中。"
        ),
        agent=letter_writer,
        )
        task3 = Task(
        description=(
        "根据本次磁盘保存的书信内容，你将整理并发送邮件给心仪的人，这个很重要。"
        "你最后的答案一定要成功发送该邮件。"
        ),
        agent=sender,
        )
        return Crew(
    agents=[poet, letter_writer, sender],
    tasks=[task1, task2, task3],
    process=Process.sequential, # 上一任务结果作为附加内容传给下一个任务
    verbose=2,
    )

    if __name__ == "__main__":
        crew = build_crew("帮我写一份情书")
        result = crew.kickoff()
        print(result)
```

三点工程说明：

1. **工具失败要变成可读的返回文本**，而不是抛异常——`send_message` 里对文件不存在的处理就是范例；Agent 会把这段文本当作 Observation 继续推理。
2. **Task 的 description 承担输出契约**：三个 Task 都以「你最后的答案必须是……」结尾，这不是修辞，是在约束 AgentFinish 的内容。
3. 真实发信请使用 `custom_tools.py` 的 `smtplib.SMTP_SSL(smtp_srv.encode(), 465)` 写法，并且**凭证从环境变量读取**，不要写进源码。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「用 CrewAI 编排三 Agent 流水线（Chapter 10 项目）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../07-agent/03-记忆与多智能体/03-LangChain与工具编排.md)
