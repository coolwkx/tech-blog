import hashlib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup, SoupStrainer
import yaml

import shutil
import gzip
from mkdocs.config import load_config
from mkdocs.structure.files import get_files

REPO = Path(__file__).resolve().parents[1]
def load_entries(CONFIG):
    ROOT = Path(CONFIG.site_dir)
    BASE = CONFIG.site_url
    UI = REPO / 'learning-ui'
    FILES = get_files(CONFIG)
    METADATA = {}
    entries = []
    for file in FILES.documentation_pages():
        if file.src_uri in ('README.md', 'index.md'):
            continue
        source = Path(CONFIG.docs_dir) / file.src_uri
        markdown = source.read_text(encoding='utf-8').lstrip('\ufeff')
        metadata = yaml.safe_load(re.split(r'^---[ \t]*$', markdown, maxsplit=2, flags=re.M)[1]) if markdown.startswith('---\n') else {}
        if not metadata.get('article_id'):
            raise ValueError('缺少稳定 article_id，请先运行 python tools/register_articles.py：' + file.src_uri)
        METADATA[file.src_uri] = metadata
        entries.append({'title': file.name, 'path': urllib.parse.quote(file.url, safe='/%'), 'built': file.dest_uri, 'src': file.src_uri})
    (ROOT / 'content').mkdir(exist_ok=True)
    for entry in entries:
        metadata = METADATA[entry['src']]
        entry['id'] = metadata['article_id']
        entry['category'] = metadata.get('learning_category', entry['src'].split('/')[0])
        entry['kind'] = metadata.get('learning_kind', 'article')
        if entry['kind'] == 'guide' and len(entry['path'].strip('/').split('/')) == 1:
            entry['kind'] = 'domain'
        for key in ('direction', 'topic', 'sourceId', 'order', 'objective'):
            if 'learning_' + key in metadata:
                entry[key] = metadata['learning_' + key]
        entry['parent'] = '/'.join(entry['path'].strip('/').split('/')[:-1]) + '/'
    ids = [entry['id'] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('article_id 重复：不能发布')
    return entries

def import_entry(entry, ROOT, BASE, by_url):
    cache = ROOT / entry.pop('built')
    soup = BeautifulSoup(cache.read_text(encoding='utf-8'), 'html.parser', parse_only=SoupStrainer('article'))
    article = soup.select_one('article.md-content__inner')
    if article is None:
        raise ValueError('Missing body: ' + entry['path'])
    for element in article.select('script, iframe, object, embed, .headerlink, .md-annotation'):
        element.decompose()
    for element in article.find_all(True):
        for attr in list(element.attrs):
            if attr.startswith('on'):
                del element[attr]
    h1 = article.find('h1')
    title = h1.get_text(' ', strip=True) if h1 else entry['title']
    if h1:
        h1.decompose()
    for a in article.select('a[href]'):
        href = a['href']
        if href.startswith(('javascript:', 'data:')):
            a.unwrap()
            continue
        if href.startswith('#'):
            continue
        target, fragment = urldefrag(urljoin(BASE + entry['path'], href))
        if urllib.parse.unquote(target) in by_url:
            a['href'] = '#note=' + by_url[urllib.parse.unquote(target)] + ('&section=' + urllib.parse.quote(fragment) if fragment else '')
        elif target == BASE:
            a['href'] = '#home'
        else:
            a['href'] = target + ('#' + fragment if fragment else '')
            a['target'] = '_blank'
            a['rel'] = 'noopener noreferrer'
    for img in article.select('img[src]'):
        url = urljoin(BASE + entry['path'], img['src'])
        img['src'] = urllib.parse.unquote(url[len(BASE):]) if url.startswith(BASE) else url
        img['loading'] = 'lazy'
        img.attrs.pop('srcset', None)
    # Strip line anchors, preserving highlighted code and exact line breaks.
    for a in article.select('pre a'):
        a.decompose()
    for table in list(article.select('table')):
        wrapper = soup.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0', 'role': 'region', 'aria-label': '横向滚动表格'})
        table.wrap(wrapper)
    for node in article.select('h2, h3, h4'):
        if not node.get('id'):
            node['id'] = 'heading-' + hashlib.sha1(node.get_text().encode()).hexdigest()[:10]
    headings = [{'id': n['id'], 'text': n.get_text(' ', strip=True), 'level': int(n.name[1])} for n in article.select('h2, h3')]
    text = article.get_text(' ', strip=True)
    entry.update(title=title, headings=headings, text=text, excerpt=text[:150], minutes=max(1, round(len(text) / 450)), hasMath=bool(re.search(r'\\\(|\\\[|\$\$', str(article))), hasMermaid=bool(article.select('.mermaid')))
    body = ''.join(str(n) for n in article.contents)
    (ROOT / 'content' / (entry['id'] + '.js')).write_text('window.WKX_ARTICLES=window.WKX_ARTICLES||{};window.WKX_ARTICLES[' + json.dumps(entry['id']) + ']=' + json.dumps(body, ensure_ascii=False) + ';', encoding='utf-8')
    return entry

def compress_resources(ROOT):
    resources = [ROOT / name for name in ('index.html', 'catalog.js', 'app.js', 'style.css', 'records.js', 'learning-directions.js')] + list((ROOT / 'content').glob('*.js')) + list((ROOT / 'search').glob('*.js')) + list((ROOT / 'assets').glob('*.js'))
    for file in resources:
        if file.is_file() and file.suffix in ('.html', '.js', '.css', '.svg', '.json'):
            data = file.read_bytes()
            if len(data) > 1000:
                packed = gzip.compress(data, compresslevel=9, mtime=0)
                if len(packed) < len(data) * 0.9:
                    Path(str(file) + '.gz').write_bytes(packed)

def write_redirects(ROOT, BASE, catalog, published_paths):
    # Keep registered old URLs valid if Markdown moves without changing article_id.
    current_paths = {entry['path']: entry['id'] for entry in catalog}
    for identifier, old_path in published_paths.items():
        entry = next((entry for entry in catalog if entry['id'] == identifier), None)
        if entry is None or entry['path'] == old_path:
            continue
        if old_path in current_paths:
            raise ValueError('旧地址被另一篇文章占用：' + old_path)
        target = ROOT / urllib.parse.unquote(old_path) / 'index.html'
        target.resolve().relative_to(ROOT.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        redirect = BASE + '#note=' + identifier
        target.write_text('<!doctype html><meta charset="utf-8"><title>文章已移动</title><p>文章已移动。</p><script>location.replace(' + json.dumps(redirect) + ')</script>', encoding='utf-8')


def main():
    CONFIG = load_config(str(REPO / 'mkdocs.yml'))
    ROOT = Path(CONFIG.site_dir)
    BASE = CONFIG.site_url
    UI = REPO / 'learning-ui'
    MANIFEST = json.loads((REPO / 'learning-map.json').read_text(encoding='utf-8'))
    entries = load_entries(CONFIG)
    by_url = {urllib.parse.unquote(BASE + e['path']): e['id'] for e in entries}
    catalog = [import_entry(entry, ROOT, BASE, by_url) for entry in entries]
    order = {src: i for i, src in enumerate(MANIFEST['pages'])}
    catalog.sort(key=lambda entry: order.get(entry['src'], len(order)))

    write_redirects(ROOT, BASE, catalog, MANIFEST.get('published_paths', {}))

    # Keep original article URLs available and add the learning reader at the root.
    for name in ('index.html', 'app.js', 'style.css', 'records.js', 'manifest.webmanifest', 'icon.svg'):
        shutil.copy2(UI / name, ROOT / name)
    shutil.copytree(UI / 'assets', ROOT / 'assets', dirs_exist_ok=True)
    texts = {entry['id']: entry['text'] for entry in catalog}
    for entry in catalog:
        entry['text'] = entry['excerpt']
    (ROOT / 'catalog.js').write_text('window.WKX_CATALOG=' + json.dumps(catalog, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
    search_dir = ROOT / 'search'
    search_dir.mkdir(exist_ok=True)
    for domain in MANIFEST['domains']:
        subset = {entry['id']: texts[entry['id']] for entry in catalog if entry['category'] == domain['key']}
        (search_dir / (domain['key'] + '.js')).write_text('window.WKX_SEARCH_TEXT=Object.assign(window.WKX_SEARCH_TEXT||{},' + json.dumps(subset, ensure_ascii=False, separators=(',', ':')) + ');', encoding='utf-8')
    (ROOT / 'learning-directions.js').write_text('window.WKX_DIRECTIONS=' + json.dumps(MANIFEST['domains'], ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
    version = hashlib.sha256((ROOT / 'catalog.js').read_bytes() + (ROOT / 'app.js').read_bytes() + (ROOT / 'style.css').read_bytes()).hexdigest()[:12]
    index = ROOT / 'index.html'
    (ROOT / 'sw.js').write_text((UI / 'sw.js').read_text(encoding='utf-8').replace('__BUILD_VERSION__', version), encoding='utf-8')
    html = index.read_text(encoding='utf-8').replace('?v=2', '?v=' + version)
    index.write_text(html, encoding='utf-8')
    compress_resources(ROOT)
    print(json.dumps({'pages': len(catalog), 'articles': sum(e['kind'] == 'article' for e in catalog)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
