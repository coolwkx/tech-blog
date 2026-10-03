> **一句话总结**：Ollama 是把「下载模型 → 加载权重 → 起一个 HTTP 服务」三件事封装成一条命令的本地大模型运行工具；它让本地推理的门槛从「配环境 + 写加载代码」降到 `ollama run <模型名>`，并通过 11434 端口暴露 OpenAI 兼容接口，从而能无缝接入 LangChain 等上层框架。
> **前置知识**：命令行基础、环境变量概念、HTTP/REST 基础、Python 与虚拟环境。
> **学完能做到**：1. 在 Windows/Linux/macOS 上正确安装并配置 Ollama（含模型存储路径迁移）；2. 用 CLI、`ollama` Python 库、`requests` 调 REST API、LangChain 四种方式调用同一个本地模型；3. 根据显存选择模型规模与量化版本，并写出可复用的 Modelfile。

## 1. 核心概念

### 1.1 为什么需要 Ollama

LLM 的运行通常需要**大量计算资源和复杂的部署流程**（下载权重、装 CUDA/PyTorch、写加载与推理代码、
管理显存与并发）。Ollama 是一个**开源的大型语言模型服务工具**，帮助用户快速在本地运行大模型：
通过简单的安装指令，用户可以**执行一条命令就在本地运行开源大型语言模型**（如 Llama 2），
极大简化了 LLM 的部署与管理过程。

| 对比项 | 裸用 transformers | Ollama |
|---|---|---|
| 环境准备 | 装 PyTorch/CUDA、处理版本冲突 | 装一个安装包 |
| 模型下载 | 手动找权重、处理分片 | `ollama pull <模型名>` |
| 服务化 | 自己写 FastAPI/Flask 封装 | 自带 HTTP 服务（11434） |
| 量化 | 自己转 GGUF、选量化等级 | 模型库提供现成量化 tag |
| 多模型切换 | 改代码、重载权重 | 换模型名即可（服务端按需加载/卸载） |
| 适用场景 | 需要改模型结构、做训练/微调 | 推理、RAG 后端、Agent 工具 |

### 1.2 四种调用方式一览

| 方式 | 依赖 | 适用场景 | 关键点 |
|---|---|---|---|
| CLI（`ollama run`） | 无 | 快速验证、手动对话 | 交互式 REPL，`Ctrl+D` 退出 |
| `ollama` Python 库 | `pip install ollama` | Python 项目内调用 | 官方 SDK，最简洁；支持 `Client(host=...)` 远程调用 |
| `requests` 直连 REST | `pip install requests` | 跨语言、精细控制请求体 | `POST /api/chat`、`/api/generate`，可完全控制 `options` |
| LangChain 集成 | `langchain`、`langchain_community` | 构建 RAG/Agent 链路 | `Ollama(base_url=..., model=..., temperature=0)` |

同一个问题「为什么天空是蓝色的？」在四种方式下的写法见第 3 节。

### 1.3 硬件门槛（给出的经验值）

| 模型规模 | 最低显存要求 |
|---|---|
| 7B | ≥ 8 GB |
| 13B | ≥ 16 GB |
| 无 GPU | 默认加载 CPU（可运行但很慢） |
| 有 GPU | 默认加载 GPU |

规则：**如果没有 GPU 默认加载 CPU；如果有则默认加载 GPU**。这也是「本地能跑」与「本地能用」的分界线——
CPU 推理 7B 模型通常只有每秒几个 token。

## 2. 关键机制

### 2.1 Ollama 与 llama.cpp / GGUF 的关系

Ollama 底层基于 **llama.cpp** 推理引擎，模型以 **GGUF** 格式分发：

| 层次 | 说明 |
|---|---|
| 模型文件格式 | GGUF：把权重、量化参数、词表、对话模板打包在一个文件里 |
| 推理引擎 | llama.cpp：CPU/GPU 混合推理，支持多种量化 |
| Ollama 的角色 | 模型管理（拉取/缓存/切换）+ 会话管理 + HTTP 服务 + Modelfile 定制 |

**这解释了三个常见现象**：① 为什么 Ollama 能只靠 CPU 跑（llama.cpp 的 CPU 后端）；
② 为什么模型文件是 `.gguf`、存放在 `~/.ollama/models/blobs`（内容寻址的 blob 存储）；
③ 为什么「换模型」很快——服务端只是卸载旧权重、加载新权重。

### 2.2 为什么必须改模型存储路径

| 项 | 说明 |
|---|---|
| 默认路径 | Windows：`C:\Users\%username%\.ollama\models`；Linux/macOS：`~/.ollama/models` |
| 环境变量 | `OLLAMA_MODELS`（**必须配置**，明确要求） |
| 示例值 | `D:\Work\ollama\models` |
| 为什么 | 7B 模型量化后也是数 GB，13B/70B 更大；装在系统盘会持续挤占空间并影响电脑运行速度 |

**关键操作顺序**：先**退出 Ollama**（右下角图标 → Quit Ollama）再改环境变量，
否则配置无法生效；改完后从「开始」菜单重新启动 Ollama。

### 2.3 REST API 的两个核心端点

| 端点 | 用途 | 关键字段 |
|---|---|---|
| `POST /api/generate` | 单轮文本补全 | `model`、`prompt`、`stream`、`options` |
| `POST /api/chat` | 多轮对话（推荐） | `model`、`messages`、`stream`、`options` |
| `GET /api/tags` | 列出本地模型 | — |
| `POST /api/pull` | 拉取模型 | `name` |
| `POST /api/embed` | 生成 embedding（用于 RAG） | `model`、`input` |
| `GET /api/version` | 服务版本（可用于健康检查） | — |

**`options` 里放的是采样参数**：`temperature`、`top_p`、`num_ctx`（上下文长度）、`num_predict`（最大生成 token）等。
的注释很直白：`temperature`「为 0 表示不让模型自由发挥，输出结果相对较固定，>0 的话，输出的结果会比较放飞自我」。

### 2.4 Modelfile：把 Prompt 与参数固化成一个新模型

`ollama create` 的核心是 Modelfile（类似 Dockerfile 的思路）。

| 指令 | 作用 | 示例 |
|---|---|---|
| `FROM` | 指定基座模型或 GGUF 文件（**必需**） | `FROM qwen2:7b` |
| `SYSTEM` | 固定系统提示词 | `SYSTEM 你是一名严谨的金融分析师。` |
| `TEMPLATE` | 对话模板（不同模型格式不同） | `TEMPLATE """{{ .System }}\n{{ .Prompt }}"""` |
| `PARAMETER` | 默认推理参数 | `PARAMETER temperature 0.2`、`PARAMETER num_ctx 8192` |
| `ADAPTER` | 加载 LoRA adapter（把微调结果接上） | `ADAPTER ./lora-adapter` |
| `LICENSE` / `MESSAGE` | 许可信息 / 预置对话示例 | `MESSAGE user 你好` |

```text
# 文件名：Modelfile.finance
FROM qwen2:7b
PARAMETER temperature 0.2
PARAMETER num_ctx 8192
PARAMETER top_p 0.9
SYSTEM """你是一名严谨的金融文本分析助手。
只依据用户提供的原文作答，原文未提及的信息一律回答「原文中未提及」。
输出使用简体中文，不使用营销化措辞。"""
```

```bash
ollama create finance-qwen -f Modelfile.finance
ollama run finance-qwen
```

**为什么要这样做**：把「系统提示 + 参数」从应用代码里挪到模型定义里，
可以让同一个应用通过**切换模型名**就获得不同的角色与参数，避免 prompt 在代码中四处散落、难以版本管理。

### 2.5 量化为什么能省显存

GGUF 的量化把每个权重从 FP16（2 字节）压到更低位宽：

| 量化 | 每权重约 | 7B 模型权重体积（约） | 效果 |
|---|---|---|---|
| FP16 | 2 字节 | 约 14 GB | 最佳，最占显存 |
| Q8_0 | 1 字节 | 约 7 GB | 几乎无损 |
| Q5_K_M | 约 0.7 字节 | 约 5 GB | 轻微损失 |
| Q4_K_M | 约 0.55 字节 | 约 4 GB | **常用甜点**，明显省显存 |
| Q3/Q2 | ≤ 0.4 字节 | ≤ 3 GB | 体积最小，质量下降明显 |

**除了权重还有 KV cache**：显存 ≈ 权重 + KV cache + 运行开销。
KV cache 随上下文长度线性增长，因此 `num_ctx` 设得越大，显存占用越高。
显存吃紧时的优先级：**降量化等级 → 降 `num_ctx` → 换更小参数模型**。

## 3. 可运行示例

### 3.1 安装与环境配置（命令清单）

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

### 3.2 四种调用方式（同一个问题）

```python
# ========== 方式 1：官方 ollama 库（最简）==========
# 依赖：pip install ollama
import ollama

response = ollama.chat(
 model="qwen2:1.5b",
 messages=[{"role": "user", "content": "为什么天空是蓝色的？"}],
)
print(response["message"]["content"])

# 生成式（非对话）接口：
# response = ollama.generate(model="qwen2:1.5b", prompt="为什么天空是蓝色的？")

# ========== 方式 2：Client 指定主机（可远程调用）==========
from ollama import Client

client = Client(host="http://127.0.0.1:11434") # 远程示例：http://192.168.1.100:11434
resp = client.chat(model="qwen2:1.5b", messages=[
 {"role": "user", "content": "为什么天空是蓝色的？"},
])
print(resp["message"]["content"])

# ========== 方式 3：流式输出（生成器）==========
stream = ollama.chat(
 model="qwen2:1.5b",
 messages=[{"role": "user", "content": "为什么天空是蓝色的？"}],
 stream=True,
)
for chunk in stream:
 print(chunk["message"]["content"], end="", flush=True)
print
```

```python
# ========== 方式 4：requests 直连 REST ==========
# 依赖：pip install requests
import requests

host, port = "127.0.0.1", "11434"
url = f"http://{host}:{port}/api/chat"
data = {
"model": "qwen2:1.5b", # 模型选择
"options": {
"temperature": 0.0, # 0 表示不让模型自由发挥，输出相对固定
"num_ctx": 4096,
},
"stream": False, # 流式输出开关
"messages": [ # 对话列表
{"role": "system", "content": "你是一个简洁的科普助手。"},
{"role": "user", "content": "为什么天空是蓝色的？"},
],
}
response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=60)
response.raise_for_status
print(response.json["message"]["content"])
```

```python
# ========== 方式 5：LangChain 集成 ==========
# 依赖：pip install langchain langchain_community
# 注意：新版 LangChain 推荐 from langchain_ollama import OllamaLLM
from langchain_community.llms import Ollama

host, port = "127.0.0.1", "11434" # 默认端口 11434
# 如果本地系统已有 ollama 服务，可以省略 base_url
llm = Ollama(base_url=f"http://{host}:{port}", model="qwen2:1.5b", temperature=0)
print(llm.invoke("你是谁"))
```

## 4. 常见坑

| 坑 | 现象 | 原因 | 正确做法 |
|---|---|---|---|
| 先改环境变量后退出 Ollama | `OLLAMA_MODELS` 不生效，模型仍装在 C 盘 | 进程已加载旧环境 | 先 Quit Ollama（或结束进程），再改变量，最后重启 |
| 模型全下在 C 盘 | C 盘爆满、系统变卡 | 默认路径在用户目录 | 设置 `OLLAMA_MODELS` 到其它盘，并清理原目录 |
| Linux 只在 shell 里 export | 重启服务后配置丢失 | systemd 不继承交互 shell 的环境 | 写进 `systemctl edit ollama.service` 的 `Environment=` |
| 不写 tag 直接 pull | 拉到的规模/量化不符合预期 | 默认 tag 未必是你想要的版本 | 显式写全 `<模型>:<规模>-<量化>`，如 `qwen2:7b-instruct-q4_K_M` |
| 显存不够仍要跑大模型 | 加载失败、或退化到 CPU 极慢 | 权重 + KV cache 超出显存 | 换 Q4_K_M 量化、降 `num_ctx`、换更小模型；确认是否真的用上了 GPU |
| 上下文设得过大 | 显存溢出或速度骤降 | KV cache 随 `num_ctx` 线性增长 | 按实际需求设 `num_ctx`，不要无脑拉满 |
| 分类任务 temperature 过高 | 同一输入结果漂移 | 采样随机性 | 结构化任务 `temperature=0` |
| 把 Ollama 当生产级高并发服务 | 请求排队、超时 | 单机推理并发能力有限 | 加请求队列/限流，或评估更高吞吐的推理框架 |
| 远程调用没开监听 | 连不上 | 服务默认只监听本机 | 需要时配置 `OLLAMA_HOST=0.0.0.0`，并做好网络隔离与鉴权 |
| `requests` 不设 timeout | 程序长时间挂住 | 模型冷启动/长生成耗时不可控 | 显式设置 `timeout`，并对长文本启用 `stream=True` |
| 误以为 LangChain 集成必须联网 | 担心数据外传 | 不熟悉本地模型链路 | `Ollama` 走的是本地 11434，数据不出机器 |

## 5. 面试问答

**Q1：Ollama 相比直接用 transformers 加载模型，工程上解决了什么问题？**

<details><summary>参考答案</summary>

主要解决四件事：

1. **环境与依赖**：不用手工处理 PyTorch/CUDA 版本与编译问题，装一个安装包即可；
2. **模型分发**：模型以 GGUF 格式统一分发，`ollama pull` 一步获取，省去权重分片、词表、对话模板的拼装；
3. **服务化**：自带 HTTP 服务（默认 11434），提供 `/api/chat`、`/api/generate`、`/api/embed` 等端点，
 上层应用（LangChain、业务后端）通过 HTTP 调用，不需要自己写 Flask/FastAPI 封装；
4. **运维体验**：多模型共存、按需加载/卸载，`ollama list/ps/show/rm` 管理，Modelfile 可把系统提示与参数固化成新模型。

代价是**定制能力弱于 transformers**：不能改模型结构、不能直接做训练，
量化与推理参数的可调范围也受 llama.cpp 支持范围限制。所以「推理与部署」用 Ollama，
「训练与微调」仍要用 transformers + PEFT 这类工具链。
</details>

**Q2：为什么要在安装后立刻配置 `OLLAMA_MODELS`？不配会怎样？**

<details><summary>参考答案</summary>

Ollama 默认把模型存在用户目录下（Windows 为 `C:\Users\%username%\.ollama\models`，
Linux/macOS 为 `~/.ollama/models`）。一个大模型动辄数 GB 到数十 GB，若不迁移：
① 迅速占满系统盘，进而影响操作系统与其它软件运行（明确指出「会影响电脑运行速度」）；
② 后续换盘/迁移很麻烦（要重新下载或手工搬 blob）。

正确做法是：新建**系统**环境变量 `OLLAMA_MODELS` 指向数据盘（如 `D:\Work\ollama\models`），
并且**先退出 Ollama 进程再改、改完重启**，否则运行中的进程仍用旧配置。
Linux 下若用 systemd 管理服务，必须写进 service 的 `Environment=` 才持久有效。
</details>

**Q3：Ollama 的 `/api/generate` 和 `/api/chat` 有什么区别？RAG 应用该用哪个？**

<details><summary>参考答案</summary>

`/api/generate` 是**单轮文本补全**接口，入参是 `prompt` 字符串，适合「给一段文本让它续写/改写」；
`/api/chat` 是**多轮对话**接口，入参是 `messages` 列表（含 `role`/`content`），
服务端会按模型自带的对话模板拼接成正确的 prompt。

RAG 应用应优先用 `/api/chat`：① 检索到的上下文与用户问题需要按角色分隔
（通常把参考放进 `system` 或单独一段 `user` 内容），`messages` 结构天然表达这种分层；
② 多轮追问（Query 改写、指代消解）需要历史消息；③ 服务端套用对话模板能避免手工拼接出错。

另外 RAG 还需要 `/api/embed` 生成向量——**生成模型与 embedding 模型要分开选**
（如生成用 `qwen2:7b`、向量用 `nomic-embed-text`），不要用一个模型硬兼两职。
</details>

## 6. 自测题

**1. Ollama 默认监听哪个端口？用 Python 远程调用另一台机器上的 Ollama，代码怎么写？**

<details><summary>参考答案</summary>

默认端口 **11434**。远程调用：

```python
from ollama import Client
client = Client(host="http://192.168.1.100:11434")
resp = client.chat(model="qwen2:1.5b", messages=[{"role": "user", "content": "你好"}])
print(resp["message"]["content"])
```

需注意：服务端默认只监听本机，远程访问要在服务端配置 `OLLAMA_HOST=0.0.0.0`，
并做好网络隔离与访问控制，避免把模型服务暴露到公网。
</details>

**2. 运行 13B 模型大约需要多少显存？显存不足时按什么顺序降级？**

<details><summary>参考答案</summary>

给出的经验值：**13B 至少需要 16GB 显存**（7B 至少 8GB）。若没有 GPU 会默认加载 CPU，
可运行但速度很慢。

显存不足时的降级顺序：① 换更低量化等级（如 Q4_K_M，7B 权重从约 14GB 降到约 4GB）；
② 降低 `num_ctx`（KV cache 随上下文线性增长）；③ 换更小参数规模的模型；
④ 减少并发/批量。显存 ≈ 权重 + KV cache + 运行开销，三项都要考虑。
</details>

**3. 写一个 Modelfile，把 `qwen2:7b` 定制成「只依据原文作答、温度 0.2、上下文 8K」的金融助手。**

<details><summary>参考答案</summary>

```text
FROM qwen2:7b
PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
SYSTEM """你是一名严谨的金融文本分析助手。
只依据用户提供的原文作答，原文未提及的信息一律回答「原文中未提及」。
输出使用简体中文，不使用营销化措辞。"""
```

创建并使用：

```bash
ollama create finance-qwen -f Modelfile.finance
ollama run finance-qwen
```
</details>

**4. 为什么 Ollama 能在没有 GPU 的机器上运行？代价是什么？**

<details><summary>参考答案</summary>

因为 Ollama 底层使用 **llama.cpp**，它支持 CPU 后端（并支持 AVX/NEON 等指令集加速）与 CPU/GPU 混合推理，
模型以 GGUF 量化格式存储，量化本身也大幅降低了计算与内存需求。
因此即使没有 GPU，也能加载并运行模型。

代价是**推理速度显著下降**（通常每秒几个 token，长回答等待明显），
且并发能力很弱；另外提醒「如果没有 GPU 默认加载 CPU；如果有默认加载 GPU」，
说明这是自动降级而非等价替代。
</details>

**5. 用 Ollama 搭一个最小 RAG 后端，需要用到哪些端点？各自负责什么？**

<details><summary>参考答案</summary>

- `POST /api/embed`：把知识库切分后的文本块和用户问题编码为向量，用于建库与检索；
- `POST /api/chat`：把检索到的 Top-K 文本块与用户问题按角色拼进 `messages`，生成最终回答；
- `GET /api/tags`：启动时校验所需模型是否已下载；
- `GET /api/version`：健康检查。

流程：文档切分 → `/api/embed` 入库（向量库如 Milvus）→ 用户提问 → `/api/embed` 编码问题 →
向量检索 Top-K → 拼 prompt → `/api/chat` 生成 → 返回答案与引用来源。
注意生成模型与 embedding 模型要分别选择，并控制 `num_ctx` 能容纳拼接后的上下文。
</details>

## 7. 延伸阅读

- [Ollama 官方文档](https://docs.ollama.com/)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [LangChain 官方文档](https://python.langchain.com/docs/introduction/)
- [Milvus 官方文档](https://milvus.io/docs)

---

[⬅️ 返回本目录索引](README.md)
