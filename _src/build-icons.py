#!/usr/bin/env python3
"""Rebuild the app icons (for installing the arcade as an app) from icon.svg.

    python3 _src/build-icons.py

Writes icons/icon-192.png and icons/icon-512.png (icon.svg as is, rounded corners) and
icons/maskable-512.png (full-bleed background, cabinet shrunk into the safe zone, so Android
can crop it to a circle or squircle). Renders with headless Chrome, like build-previews.py.
"""
import os
import re
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
BG = '#12152a'


def shot(svg, size, out):
    markup = ('<!doctype html><html><head><style>html,body{margin:0;background:transparent}'
              f'svg{{display:block;width:{size}px;height:{size}px}}</style></head>'
              f'<body>{svg}</body></html>')
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(markup)
    try:
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=1', f'--window-size={size},{size}',
                        '--default-background-color=00000000',
                        f'--screenshot={out}', f'file://{f.name}'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.unlink(f.name)


def main():
    src = open(os.path.join(ROOT, 'icon.svg')).read()
    src = re.sub(r'\s*<!--.*?-->', '', src, flags=re.S)
    # The cabinet without its rounded background tile.
    inner = re.sub(r'<rect width="64" height="64"[^>]*/>', '', src.split('>', 1)[1].rsplit('</svg>', 1)[0])
    # Maskable: the safe zone is the centre circle of radius 40%; 70% scale keeps the cabinet in it.
    maskable = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
                f'<rect width="64" height="64" fill="{BG}"/>'
                f'<g transform="translate(9.6 9.6) scale(0.7)">{inner}</g></svg>')
    out = os.path.join(ROOT, 'icons')
    os.makedirs(out, exist_ok=True)
    for size in (192, 512):
        shot(src, size, os.path.join(out, f'icon-{size}.png'))
        print(f'icons/icon-{size}.png')
    shot(maskable, 512, os.path.join(out, 'maskable-512.png'))
    print('icons/maskable-512.png')


if __name__ == '__main__':
    main()
