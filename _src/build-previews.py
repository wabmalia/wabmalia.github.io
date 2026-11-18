#!/usr/bin/env python3
"""Rebuild the link-preview images (1200x630, for Discord, Slack, etc.) from the arcade tiles.

    python3 _src/build-previews.py

Reads every `<a class="tile">` in index.html (its artwork, name and description) and writes
previews/<slug>.png for each game plus previews/arcade.png for the arcade itself, by rendering
an HTML card with headless Chrome. The games point their og:image at
https://arcade.wabmalia.eu/previews/<slug>.png. After changing an image, bump ?v= in the
og:image/twitter:image tags that use it, so Discord and friends fetch it again.
"""
import html
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

STYLE = """
html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; }
body { background: #12152a; color: #eef0fa; font-family: system-ui, -apple-system, sans-serif;
       display: flex; align-items: center; gap: 64px; padding: 0 80px; box-sizing: border-box; }
.art { flex: none; border-radius: 24px; overflow: hidden; box-shadow: 0 0 0 4px #272c52; }
.art svg { display: block; }
h1 { margin: 0; font-size: 80px; font-weight: 900; letter-spacing: 1px; line-height: 1.05; }
h1 sup { font-size: 0.55em; }
p { margin: 24px 0 0; font-size: 36px; line-height: 1.3; color: #b8bdd8; }
.url { margin-top: 40px; font-size: 30px; color: #f2b134; }
.grid { display: grid; grid-template-columns: repeat(2, 260px); gap: 18px; flex: none; }
.grid svg { display: block; width: 260px; height: 143px; border-radius: 12px; box-shadow: 0 0 0 3px #272c52; }
"""


def tiles(src):
    for m in re.finditer(r'<a class="tile" href="/([^/"]+)/"[^>]*>(.*?)</a>', src, re.S):
        slug, body = m.group(1), m.group(2)
        art = re.search(r'<svg class="art".*?</svg>', body, re.S).group(0)
        art = re.sub(r'\s*<!--.*?-->', '', art, flags=re.S).replace(' class="art"', '')
        name = re.search(r'<span class="tile-name">(.*?)</span>', body, re.S).group(1)
        desc = re.search(r'<span class="tile-desc">(.*?)</span>', body, re.S).group(1)
        yield slug, art, name, desc


def page(body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{STYLE}</style></head><body>{body}</body></html>'


def shot(markup, out):
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(markup)
    try:
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=1', '--window-size=1200,630',
                        f'--screenshot={out}', f'file://{f.name}'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.unlink(f.name)


def main():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    out_dir = os.path.join(ROOT, 'previews')
    os.makedirs(out_dir, exist_ok=True)
    found = list(tiles(src))
    for slug, art, name, desc in found:
        big = art.replace('<svg ', '<svg width="520" height="286" ', 1)
        shot(page(f'<div class="art">{big}</div><div><h1>{name}</h1><p>{desc}</p>'
                  f'<p class="url">arcade.wabmalia.eu/{html.escape(slug)}</p></div>'),
             os.path.join(out_dir, f'{slug}.png'))
        print('previews/' + slug + '.png')
    grid = ''.join(art for _, art, _, _ in found[:4])
    shot(page(f'<div class="grid">{grid}</div><div><h1>ARCADE</h1>'
              f'<p>Browser games I build: mini golf, football, cards and more.</p>'
              f'<p class="url">arcade.wabmalia.eu</p></div>'),
         os.path.join(out_dir, 'arcade.png'))
    print('previews/arcade.png')


if __name__ == '__main__':
    main()
