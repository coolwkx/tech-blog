"""Assign IDs once, then retain them when Markdown files move."""
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    count = 0
    for path in (ROOT / 'docs').rglob('*.md'):
        if path.relative_to(ROOT / 'docs').as_posix() in ('README.md', 'index.md'):
            continue
        text = path.read_text(encoding='utf-8').lstrip('\ufeff')
        if text.startswith('---\n') and 'article_id:' in re.split(r'^---[ \t]*$', text, maxsplit=2, flags=re.M)[1]:
            continue
        identifier = 'note-' + uuid.uuid4().hex[:16]
        if text.startswith('---\n'):
            text = text.replace('---\n', f'---\narticle_id: {identifier}\n', 1)
        else:
            category = path.relative_to(ROOT / 'docs').parts[0]
            kind = 'guide' if path.name == 'README.md' else 'reference'
            text = f'---\narticle_id: {identifier}\nlearning_category: {category}\nlearning_kind: {kind}\n---\n\n' + text
        path.write_text(text, encoding='utf-8')
        count += 1
    print(f'已为 {count} 个新页面分配稳定编号；现有编号保持不变。')

if __name__ == '__main__':
    main()
