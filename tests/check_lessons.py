"""Guard a large content split against broken code or lost source context."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
manifest = json.loads((ROOT / 'learning-map.json').read_text(encoding='utf-8'))
sources = {meta['id']: DOCS / src for src, meta in manifest['pages'].items() if meta['kind'] == 'reference'}
count = 0
for src, meta in manifest['pages'].items():
    if meta['kind'] != 'article':
        continue
    text = (DOCS / src).read_text(encoding='utf-8')
    source = sources[meta['sourceId']].read_text(encoding='utf-8')
    for match in re.finditer(r'^```[^\n]*\n(.*?)^```', text, re.M | re.S):
        assert match[1].strip() in source, f'知识点代码偏离综合原文：{src}'
    assert '综合原文' in text and '前置知识' in text and '学习目标' in text, f'上下文缺失：{src}'
    count += 1
for domain in manifest['domains']:
    assert len(domain['directions']) == 2
    for direction in domain['directions']:
        assert any(n['category'] == domain['key'] and n.get('direction') == direction['key'] and n['kind'] == 'article' for n in manifest['pages'].values())
print(f'{count} 个知识点的代码来源、上下文和领域方向检查通过。')
