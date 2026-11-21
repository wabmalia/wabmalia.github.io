# arcade

Live at https://arcade.wabmalia.eu. This is the `wabmalia.github.io` user-site repo with the custom
domain `arcade.wabmalia.eu`, so every other Pages repo without its own domain appears under it:
the games are at `arcade.wabmalia.eu/<repo>/` (squared, turn7, sinkhole, ink-kick). Tile links are
root-relative (`/ink-kick/`). DNS: `arcade` CNAME to `wabmalia.github.io.` in the Hetzner zone
`wabmalia.eu`. The old `wabmalia/arcade` repo only redirects here.

A landing page for my games, drawn as an arcade cabinet. The page eases in
from the whole cabinet to its screen; picking a game zooms the rest of the way
in, fills a loading bar and opens the game.

Plain HTML/CSS/JS, no build step. Open `index.html` in a browser.

## Adding a game

Copy one of the `<a class="tile">` blocks in `index.html` and change its
`href` (`/<repo>/`), `data-name` (shown on the loading screen), artwork, name and
description. The artwork is an inline 200x110 SVG. The screen shows it as a
thumbnail and, for the selected game, big in the preview with the name and
description beside it.

A game that needs a keyboard can be kept off phones and tablets with a
`data-desktop-only` attribute on its tile: it's only offered where there's a
mouse or trackpad.

## Link previews

Every game shows a card when its link is pasted in Discord, Slack, etc. The images are
`previews/<repo>.png` (plus `previews/arcade.png`), rendered from the tiles' artwork, name and
description by `python3 _src/build-previews.py` (needs Google Chrome). A new game: add its tile,
rerun the script, and copy the `og:`/`twitter:` meta block from another game's `index.html`,
pointing at `https://arcade.wabmalia.eu/previews/<repo>.png?v=1`. Bump `?v=` after changing an
image so the apps fetch it again.

## Installing as an app (PWA)

The arcade installs as one app (`manifest.webmanifest`, scope `/`), and because the games live
under the same domain they open inside it: no browser bar, no separate installs. `sw.js` is
registered at the root, so it controls the game pages too. For now it only catches page loads
that fail offline and shows `offline.html`; everything else goes to the network untouched.

- **Games must not register their own service worker or manifest.** A worker at `/<repo>/`
  would take that path over from the arcade's.
- Icons are `icons/`, rendered from `icon.svg` by `python3 _src/build-icons.py` (needs Google
  Chrome). Rerun it after changing `icon.svg`.
- Changing `offline.html`: bump `CACHE` in `sw.js` so installed apps fetch the new one.

## Controls

Hover or tap a thumbnail to select it, click or tap it again to start. The
joystick moves the selection and any of the three buttons starts the game.
The selection clears after 5 seconds; until something is selected the
preview cycles through the games.

## Tuning

- Camera shots (how much of the cabinet each step shows) and timings are at
  the top of `arcade.js`.
- Colours are the CSS variables at the top of `style.css`, the same palette as
  turn7 and squared.
- Respects `prefers-reduced-motion`: no camera moves or blinking, just a quick
  cut to the loading screen.

## Deploying to GitHub Pages

Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/`.
