#!/bin/sh
# Rebuilds the raster images from their sources with headless Chrome:
#   _src/social-preview.html -> social-preview.png (1200x630)
#   favicon.svg -> favicon-32.png, icon-192.png, apple-touch-icon.png
# After changing social-preview.png, bump ?v= on og:image/twitter:image in index.html.
set -eu
cd "$(dirname "$0")/.."
CHROME=${CHROME:-"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
root=$(pwd)

shot() { # shot <url> <width> <height> <out.png>
  "$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --default-background-color=00000000 \
    --window-size="$2,$3" --screenshot="$root/$4" "$1" >/dev/null 2>&1
}

shot "file://$root/_src/social-preview.html" 1200 630 social-preview.png

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
for spec in 32:favicon-32.png 192:icon-192.png 180:apple-touch-icon.png; do
  size=${spec%%:*}; out=${spec#*:}
  printf '<html><body style="margin:0;background:transparent"><img src="file://%s/favicon.svg" width="%s" height="%s" style="display:block"></body></html>' \
    "$root" "$size" "$size" > "$tmp/icon.html"
  shot "file://$tmp/icon.html" "$size" "$size" "$out"
done
