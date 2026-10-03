# -*- coding: utf-8 -*-
"""笔记内容质检：内部链接 + Python 代码块语法 + 文章结构。CI 与本地通用，零第三方依赖。

输出 GitHub Actions 注解（::error file=...），有 error 时退出码 1。
用法：python tools/lint_notes.py
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 同一套笔记体系的兄弟仓库：README 里会互相引用（../ml-notes 等），
# 在单仓库检出环境里不存在，属于预期情况，跳过检查。
SIBLINGS = {
    "python-notes", "ml-notes", "dl-notes", "nlp-notes", "llm-notes", "agent-notes",
    "issues", "pulls",
}
SKIP_DIRS = {".git", "site", ".venv", "node_modules", "__pycache__", "templates"}
SKIP_LINK_PREFIX = ("http://", "https://", "mailto:", "#")

FENCE_RE = re.compile(r"^```(?:python|py)\s*$", re.M)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+?)(?:#[^)]*)?\)")
BLOCK_RE = re.compile(r"^```.*?^```", re.S | re.M)
INLINE_RE = re.compile(r"`[^`\n]*`")

REQUIRED_SECTIONS = ["一句话总结", "前置知识", "常见坑", "自测题", "延伸阅读"]


def md_files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.md"):
        if set(p.parts) & SKIP_DIRS:
            continue
        out.append(p)
    return sorted(out)


def check_links(files: list[Path]) -> list[str]:
    problems = []
    for md in files:
        text = BLOCK_RE.sub("", md.read_text(encoding="utf-8"))
        text = INLINE_RE.sub("", text)
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(SKIP_LINK_PREFIX) or target in SIBLINGS:
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = target.replace("%20", " ")
            # 指向父级目录的兄弟仓库引用
            if target.strip("/").split("/")[-1] in SIBLINGS:
                continue
            if not (md.parent / target).exists():
                rel = md.relative_to(ROOT).as_posix()
                # 指向尚未产出的笔记（.md）只告警：增量写作期间属正常状态，不阻断 CI
                level = "warning" if target.endswith(".md") else "error"
                problems.append(f"::{level} file={rel}::断链 -> {target}")
    return problems


def check_code(files: list[Path]) -> list[str]:
    problems = []
    for md in files:
        lines = md.read_text(encoding="utf-8").split("\n")
        i = 0
        while i < len(lines):
            if FENCE_RE.match(lines[i]):
                start, i = i, i + 1
                buf = []
                while i < len(lines) and not lines[i].startswith("```"):
                    buf.append(lines[i])
                    i += 1
                code = "\n".join(buf)
                if code.strip():
                    try:
                        ast.parse(code)
                    except SyntaxError as e:
                        rel = md.relative_to(ROOT).as_posix()
                        problems.append(
                            f"::error file={rel},line={start + 1}::python 代码块语法错误：{e.msg}"
                        )
            i += 1
    return problems


def check_structure(files: list[Path]) -> list[str]:
    problems = []
    for md in files:
        if "topics" not in md.parts or md.name == "README.md" or "97-cheatsheet" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        missing = [k for k in REQUIRED_SECTIONS if k not in text]
        if missing:
            rel = md.relative_to(ROOT).as_posix()
            problems.append(f"::warning file={rel}::缺少必需小节：{'、'.join(missing)}")
    return problems


def check_nav() -> list[str]:
    """mkdocs.yml 的 nav 是否都指向真实文件。"""
    problems = []
    cfg = ROOT / "mkdocs.yml"
    if not cfg.is_file():
        return problems
    text = cfg.read_text(encoding="utf-8")
    # nav 路径相对于 docs_dir
    m = re.search(r"^docs_dir:\s*(\S+)\s*$", text, re.M)
    base = ROOT / (m.group(1) if m else "docs")
    # 粗略抽取 nav 段落里的 .md 路径
    in_nav = False
    for line in text.split("\n"):
        if line.startswith("nav:"):
            in_nav = True
            continue
        if in_nav and line and not line.startswith((" ", "\t", "-")):
            in_nav = False
        if in_nav:
            for m in re.finditer(r":\s*(\S+\.md)\s*$", line):
                target = m.group(1)
                if not (base / target).is_file():
                    problems.append(f"::error file=mkdocs.yml::nav 指向不存在的文件 -> {target}")
    return problems


def main() -> int:
    files = md_files()
    print(f"扫描 {len(files)} 个 Markdown 文件（仓库根：{ROOT.name}）")
    problems = check_links(files) + check_code(files) + check_structure(files) + check_nav()
    errors = [p for p in problems if p.startswith("::error")]
    if problems:
        print(f"\n发现 {len(problems)} 个问题（error {len(errors)} 个）：")
        for p in problems:
            print("  " + p)
    else:
        print("全部通过：链接无断链、代码块语法正确、文章结构完整、mkdocs nav 有效。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
