import concurrent.futures
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup

import shutil
import gzip
from mkdocs.config import load_config
from mkdocs.structure.files import get_files

REPO = Path(__file__).resolve().parents[1]
CONFIG = load_config(str(REPO / 'mkdocs.yml'))
ROOT = Path(CONFIG.site_dir)
BASE = CONFIG.site_url
UI = REPO / 'learning-ui'
FILES = get_files(CONFIG)
entries = []
for file in FILES.documentation_pages():
    if file.src_uri in ('README.md', 'index.md'):
        continue
    entries.append({'title': file.name, 'path': urllib.parse.quote(file.url, safe='/%'), 'built': file.dest_uri})
(ROOT / 'content').mkdir(exist_ok=True)
for entry in entries:
    entry['id'] = hashlib.sha1(entry['path'].encode()).hexdigest()[:12]
    entry['category'] = entry['path'].split('/')[0]
    parts = entry['path'].strip('/').split('/')
    entry['kind'] = 'domain' if len(parts) == 1 else ('series' if len(parts) == 2 else 'article')
    entry['parent'] = '/'.join(parts[:-1]) + '/' if len(parts) > 1 else ''
by_url = {BASE + e['path']: e['id'] for e in entries}

def import_entry(entry):
    cache = ROOT / entry.pop('built')
    soup = BeautifulSoup(cache.read_bytes(), 'html.parser')
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
        if target in by_url:
            a['href'] = '#note=' + by_url[target] + ('&section=' + urllib.parse.quote(fragment) if fragment else '')
        elif target == BASE:
            a['href'] = '#home'
        else:
            a['href'] = target + ('#' + fragment if fragment else '')
            a['target'] = '_blank'
            a['rel'] = 'noopener noreferrer'
    for img in article.select('img[src]'):
        url = urljoin(BASE + entry['path'], img['src'])
        ext = Path(urlparse(url).path).suffix or '.png'
        name = hashlib.sha1(url.encode()).hexdigest()[:16] + ext
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

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    catalog = list(pool.map(import_entry, entries))

# Keep original article URLs available and add the learning reader at the root.
for name in ('index.html', 'app.js', 'style.css'):
    shutil.copy2(UI / name, ROOT / name)
shutil.copytree(UI / 'assets', ROOT / 'assets', dirs_exist_ok=True)
texts = {entry['id']: entry['text'] for entry in catalog}
for entry in catalog:
    entry['text'] = entry['excerpt']
(ROOT / 'catalog.js').write_text('window.WKX_CATALOG=' + json.dumps(catalog, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
(ROOT / 'search-index.js').write_text('window.WKX_SEARCH_TEXT=' + json.dumps(texts, ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
for file in ROOT.rglob('*'):
    if file.is_file() and file.suffix in ('.html', '.js', '.css', '.svg', '.json'):
        data = file.read_bytes()
        if len(data) > 1000:
            packed = gzip.compress(data, compresslevel=9, mtime=0)
            if len(packed) < len(data) * 0.9:
                Path(str(file) + '.gz').write_bytes(packed)
print(json.dumps({'pages': len(catalog), 'articles': sum(e['kind'] == 'article' for e in catalog)}, ensure_ascii=False))
