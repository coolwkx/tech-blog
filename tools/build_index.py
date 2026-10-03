# -*- coding: utf-8 -*-
"""为合并后的 tech-blog 生成：分类索引、首页、mkdocs 配置。

章节列表从磁盘实际目录推导，因此新增笔记目录后重跑本脚本即可刷新导航。
"""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\王凯旋\OneDrive\文档\deepseek-harness\default-workspace")
DST = ROOT / "tech-blog"
DOCS = DST / "docs"
GH = "coolwkx"

GROUPS = {
    "01-python": "🐍 Python",
    "02-data": "📦 数据处理与统计",
    "03-ml": "📊 机器学习",
    "04-dl": "🧠 深度学习",
    "05-nlp": "📝 自然语言处理",
    "06-llm": "🤖 大语言模型",
    "07-agent": "🕹️ AI Agent",
    "08-project": "🚀 项目实战",
}

DESC = {
    "01-python": "语言机制、工程实践与性能优化：把「会写」变成「写对、写快」",
    "02-data": "Linux、SQL、NumPy/Pandas 到统计分析与实战案例",
    "03-ml": "从数学基础到工程落地：问题建模、特征工程、模型选择与评估",
    "04-dl": "梯度、优化、架构与训练工程：理解「为什么能训得起来」",
    "05-nlp": "文本表示、序列建模与预训练范式：串起 NLP 的演进主线",
    "06-llm": "从架构到对齐到推理落地：掌握大模型全生命周期的关键决策",
    "07-agent": "把 LLM 变成能行动的智能体：循环、工具、记忆、评估与工程化",
    "08-project": "把知识串成系统：项目架构、关键实现、踩坑与可复用经验",
}

# 中文标题：优先取章节 README 的 H1，取不到就用目录名
def section_title(sec_dir: Path) -> str:
    idx = sec_dir / "README.md"
    if idx.is_file():
        for line in idx.read_text(encoding="utf-8").split("\n"):
            if line.startswith("# "):
                t = line[2:].strip()
                t = re.sub(r"^\d+\s*[·.、]\s*", "", t)
                return t
    return sec_dir.name.split("-", 1)[1].replace("-", " ")


def sections(group: str) -> list[tuple[str, str]]:
    gdir = DOCS / group
    if not gdir.is_dir():
        return []
    out = []
    for d in sorted(p for p in gdir.iterdir() if p.is_dir()):
        out.append((d.name, section_title(d)))
    return out


def count_notes(d: Path) -> int:
    if not d.is_dir():
        return 0
    return len([p for p in d.rglob("*.md") if p.name != "README.md"])


def main() -> None:
    # ---------- 大区索引 ----------
    for group, title in GROUPS.items():
        gdir = DOCS / group
        gdir.mkdir(parents=True, exist_ok=True)
        rows, total = [], 0
        for folder, name in sections(group):
            if folder.startswith("90-"):
                continue
            n = count_notes(gdir / folder)
            total += n
            status = f"✅ {n} 篇" if n else "📝 待补充"
            idx = gdir / folder / "README.md"
            label = f"[{name}]({folder}/README.md)" if idx.is_file() else name
            rows.append(f"| {folder.split('-')[0]} | {label} | {status} |")
        if not rows:
            rows = ["| — | 待补充 | 📝 |"]

        cs = gdir / "90-cheatsheet"
        cs_row = ("| — | [速查表 / 术语表 / 面试题库](90-cheatsheet/README.md) | ✅ |"
                  if (cs / "README.md").is_file()
                  else "| — | 速查表 / 术语表 / 面试题库（待补充） | 📝 |")

        (gdir / "README.md").write_text(f"""# {title}

> {DESC[group]}

本区共 **{total}** 篇笔记。

## 章节目录

| # | 章节 | 状态 |
| --- | --- | --- |
{chr(10).join(rows)}
{cs_row}

状态说明：✅ 已有内容 ｜ 📝 待补充

## 学习建议

1. 先看每章 `README.md` 里的「本章要回答的问题」，定位自己的薄弱环节，不要从头顺读。
2. 每篇笔记按「核心概念 → 可运行示例 → 常见坑 → 面试问答 → 自测题」组织，重点看后三节。
3. 读完合上笔记做自测题，答不出来的回读对应小节。

---

[⬅️ 返回博客首页](../README.md)
""", encoding="utf-8")

    # ---------- 首页 ----------
    group_rows, total_all = [], 0
    for group, title in GROUPS.items():
        n = sum(count_notes(DOCS / group / f) for f, _ in sections(group))
        total_all += n
        group_rows.append(f"| [{title}]({group}/README.md) | {DESC[group]} | {n} |")

    (DOCS / "README.md").write_text(f"""# 📚 技术复习笔记博客

> 把 **Python → 数据处理 → 机器学习 → 深度学习 → NLP → 大语言模型 → AI Agent → 项目实战**
> 串成一条链的个人知识库。每个知识点按「核心概念 → 可运行示例 → 常见坑 → 面试问答 → 自测题」组织，
> 目标是**半小时内能重新捡起来**。

当前共 **{total_all}** 篇笔记。

## 🗂️ 八大分区

| 分区 | 内容 | 笔记数 |
| --- | --- | --- |
{chr(10).join(group_rows)}

## 🚀 怎么用

| 你的目的 | 去哪里 |
| --- | --- |
| 系统复习某个领域 | 点上面任一分区，按章节顺序读 |
| 面试冲刺 | 各分区 `90-cheatsheet/interview.md` + 各章「面试问答」节 |
| 快速查命令 / API | 各分区 `90-cheatsheet/cheatsheet.md` |
| 看项目怎么落地 | [项目实战](08-project/README.md) |
| 找回某个术语 | 各分区 `90-cheatsheet/glossary.md` |
| 从零建立体系 | [docs/roadmap.md](roadmap.md) |

## 🧭 建议的复习节奏

1. **定位**：读目标分区的 `README.md`，挑出自己讲不清楚的章节。
2. **读**：重点看「常见坑」与「面试问答」两节。
3. **跑**：把「可运行示例」在本地跑通，改参数看输出变化。
4. **测**：合上笔记做「自测题」，错题记成 issue。
5. **沉淀**：把新的理解补进对应笔记，或写进速查表。

## 🛠️ 本地预览

```bash
pip install mkdocs-material
mkdocs serve   # http://127.0.0.1:8000
```

## 📐 写作规范

- 中文为主，**英文术语保留原文**（`gradient checkpointing` 不硬译）。
- 每篇必须包含：一句话总结、前置知识、可运行示例、常见坑表、自测题。
- 引用外部结论必须给链接；数字要给量级与出处。
- 一篇只讲一个知识点，超过 400 行就拆。

## 📄 License

[MIT](../LICENSE) © 2026
""", encoding="utf-8")

    # ---------- mkdocs nav ----------
    nav = ["  - 🏠 首页: README.md"]
    for group, title in GROUPS.items():
        nav.append(f'  - "{title}":')
        nav.append(f"      - 本区目录: {group}/README.md")
        for folder, name in sections(group):
            if folder.startswith("90-"):
                continue
            idx = DOCS / group / folder / "README.md"
            if idx.is_file():
                nav.append(f"      - {name}: {group}/{folder}/README.md")
        if (DOCS / group / "90-cheatsheet" / "README.md").is_file():
            nav.append(f"      - 速查与面试: {group}/90-cheatsheet/README.md")

    mk = (DST / "mkdocs.yml").read_text(encoding="utf-8")
    mk = re.sub(r"nav:\n.*$", "nav:\n" + "\n".join(nav) + "\n", mk, flags=re.S)
    (DST / "mkdocs.yml").write_text(mk, encoding="utf-8")

    print(f"大区 {len(GROUPS)} 个，笔记总数 {total_all}，nav 条目 {len(nav)}")


if __name__ == "__main__":
    main()
