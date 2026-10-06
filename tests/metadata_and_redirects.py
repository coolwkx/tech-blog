"""Moving a Markdown page must retain its record ID and its published URL."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from mkdocs.config import load_config
from build_learning_site import load_entries, write_redirects

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    docs = root / 'docs'
    site = root / 'site'
    docs.mkdir()
    site.mkdir()
    original = docs / 'original.md'
    original.write_text('---\narticle_id: stable-old-id\nlearning_kind: reference\nlearning_category: 01-python\n---\n\n# Example\n', encoding='utf-8')
    config_path = root / 'mkdocs.yml'
    config_path.write_text('site_name: Test\nsite_url: https://example.com/blog/\n', encoding='utf-8')
    config = load_config(str(config_path))
    before = load_entries(config)[0]
    original.rename(docs / 'renamed.md')
    after = load_entries(config)[0]
    assert before['id'] == after['id'] == 'stable-old-id'
    assert before['path'] != after['path']
    write_redirects(site, config.site_url, [after], {before['id']: before['path']})
    redirect = (site / before['path'] / 'index.html').read_text(encoding='utf-8')
    assert 'https://example.com/blog/#note=stable-old-id' in redirect
    try:
        write_redirects(site, config.site_url, [after], {after['id']: '../outside/'})
        raise AssertionError('外部路径应被拒绝')
    except ValueError:
        pass
print('Stable article IDs, old URL redirects and path containment passed')
