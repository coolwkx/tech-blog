---
article_id: kp-8123bbb2e88889f9
learning_kind: article
learning_category: 06-llm
learning_direction: practice
learning_topic: topic-90fdb3fa96e7
learning_sourceId: 90fdb3fa96e7
learning_order: 8
learning_objective: 理解并验证：安装与环境配置（命令清单）
---

# 安装与环境配置（命令清单）

> **学习目标**：能够解释「安装与环境配置（命令清单）」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
>
> **所属主题**：-本地部署与Ollama · 可运行示例

## 本次只学这一点

```bash
# ---------- 安装 ----------
# Windows：下载 OllamaSetup.exe，双击 → Install
# 默认安装路径：C:\Users\%username%\AppData\Local\Programs\Ollama（不可自定义）
# macOS / Linux：官网 https://ollama.com/ 下载后直接安装

# 安装后先退出 Ollama（Windows 右下角图标 → Quit Ollama），否则环境变量不生效

# ---------- 模型存储路径迁移（Windows）----------
# 新建系统环境变量：
# 变量名：OLLAMA_MODELS
# 变量值：D:\Work\ollama\models
# 关闭开机自启动（可选）：删除下面的快捷方式
# %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Ollama.lnk

# ---------- 验证 ----------
ollama --version # 能输出版本号即安装成功
ollama list # 查看本地模型
ollama run qwen2:1.5b # 首次会自动下载，然后进入对话
```

> Linux 用 systemd 管理时，环境变量需写进服务配置（`systemctl edit ollama.service`
> 添加 `Environment="OLLAMA_MODELS=/data/ollama/models"`），否则只在当前 shell 生效。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「安装与环境配置（命令清单）」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../06-llm/05-推理与部署/06-本地部署与Ollama.md)
