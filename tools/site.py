"""One entry point for the same build locally and in CI."""
import argparse
import functools
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('build', 'preview'))
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    python = [sys.executable] + (['-S'] if sys.flags.no_site else [])
    for command in (python + ['-m', 'mkdocs', 'build'],
                    python + ['tools/build_learning_site.py'],
                    python + ['tools/check_learning_site.py']):
        subprocess.run(command, cwd=ROOT, check=True)
    (ROOT / 'site' / '.nojekyll').touch()
    if args.action == 'preview':
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'site'))
        print(f'学习界面：http://127.0.0.1:{args.port}；修改源码后重新运行此命令。')
        with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass

if __name__ == '__main__':
    main()
