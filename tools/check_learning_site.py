"""Fail publishing if catalog, Markdown, bodies, links or search disagree."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

def assignment(path, prefix):
    text = path.read_text(encoding='utf-8')
    if not text.startswith(prefix) or not text.endswith(';'):
        raise ValueError('生成数据格式无效：' + str(path))
    return json.loads(text[len(prefix):-1])

def main():
    catalog = assignment(SITE / 'catalog.js', 'window.WKX_CATALOG=')
    by_id = {n['id']: n for n in catalog}
    assert len(by_id) == len(catalog), '页面编号重复'
    manifest = json.loads((ROOT / 'learning-map.json').read_text(encoding='utf-8'))
    expected = {p['id'] for p in manifest['pages'].values()}
    assert expected <= by_id.keys(), '存在已登记页面缺失'
    for note in catalog:
        assert (ROOT / 'docs' / note['src']).is_file(), '内容源缺失：' + note['src']
        assert (SITE / unquote(note['path']) / 'index.html').is_file(), '原始文章地址缺失：' + note['path']
        raw = (SITE / 'content' / (note['id'] + '.js')).read_text(encoding='utf-8')
        match = re.search(r'window\.WKX_ARTICLES\["[^"]+"\]=(.*);$', raw, re.S)
        assert match, '正文格式错误'
        body = json.loads(match.group(1))
        soup = BeautifulSoup(body, 'html.parser')
        for link in soup.select('a[href^="#note="]'):
            identifier = link['href'].split('=', 1)[1].split('&')[0]
            assert identifier in by_id, '正文指向缺失页面：' + identifier
        if note['kind'] == 'article':
            assert note.get('direction') and note.get('topic'), '知识点缺少学习方向或主题'
            assert note.get('sourceId') in by_id, '综合原文不存在'
    for domain in manifest['domains']:
        prefix = 'window.WKX_SEARCH_TEXT=Object.assign(window.WKX_SEARCH_TEXT||{},'
        raw = (SITE / 'search' / (domain['key'] + '.js')).read_text(encoding='utf-8')
        subset = json.loads(raw[len(prefix):-2])
        assert subset.keys() == {n['id'] for n in catalog if n['category'] == domain['key']}, '正文索引与目录不一致'
    soup = BeautifulSoup((SITE / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    for element in soup.select('script[src], link[href]'):
        uri = element.get('src') or element.get('href')
        assert (SITE / urlparse(uri).path).is_file(), '首页资源缺失：' + uri
    print(f'一致性检查通过：{len(catalog)} 个页面、{sum(n["kind"] == "article" for n in catalog)} 个知识点、全部正文与分领域索引。')

if __name__ == '__main__':
    main()
