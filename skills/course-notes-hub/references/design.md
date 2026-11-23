# Hub design

## Look

- **Palette** (CSS custom properties): `--bg #08080a`, `--ink #f4f1ea` (warm
  off-white), `--ink-2 #a8a49b`, `--dim #55524c`, hairlines `#ffffff14`,
  `--accent #e9b872` (a muted amber, used only for the hovered row number,
  focus rings and the card's term line). `color-scheme: dark`,
  `theme-color #08080a`.
- **Type**: Pretendard Variable (dynamic subset from jsdelivr) with system
  fallbacks; a monospace stack for small labels (rail, numbers, meta line,
  footer) in uppercase with wide letter-spacing. Korean headings use
  `word-break: keep-all` so lines break between words, not inside them.
- **Grain**: a fixed, 3.5%-opacity SVG fractal-noise layer over everything so
  the flat black does not look digital.
- **Layout**: max 1180px, fluid side padding `clamp(20px, 4vw, 56px)`.
  Top rail (hub name left, term right), an opening sentence in large type
  whose second half is dimmed, a "LAST UPDATED yyyy.mm.dd" stamp, the list of
  rows, a footer (school name left, "국문 / 영문 전환은 각 과목 사이트에서" right).
- **Rows**: a grid of number · name · side (English name over the meta line) ·
  arrow. Names are big (`clamp(24px, 4vw, 44px)`, weight 800, tight
  tracking) and do not wrap on desktop.

## Interactions

- **Hover**: the other rows fade to 26% opacity; the hovered row's name slides
  right a few pixels, its number turns amber, its arrow moves right and
  brightens, and a 1px underline grows from the left across the row. Only on
  devices with hover (`@media (hover:hover)`).
- **Cursor preview**: a fixed card (`#peek`, A-ratio, tilted −3.5°) shows the
  hovered course's thumbnail. Its horizontal position is pinned at 72% of the
  viewport width (following the cursor sideways would cover the name being
  read); vertically it follows the cursor, eased (each frame moves 14% of the
  remaining distance), so it glides between rows like a sheet of paper. It
  stops animating when it reaches the target. Thumbnails are preloaded.
  Touch pointers never trigger it.
- **Entrance**: the number and name of each row slide up from a clipping mask
  (`.rv`), the side text and the intro fade up (`.fv`), staggered 52ms apart in
  screen order as they enter the viewport.
- **Phones (≤ 720px)**: the side column and arrow are hidden, names may wrap,
  and a 62px thumbnail sits at the end of each row instead of the cursor
  preview.
- **Reduced motion**: everything appears in place, no transitions.
- **Focus**: rows are links with an amber focus ring.

## The live line

For each row the page fetches `/<data-repo>/manifest.json` (`cache:
'no-store'`) and writes, from what is present:

```
12강  ·  11/16 수업까지  ·  국문 112p  ·  영문 96p  ·  2026.11.21
```

| Part | From |
|---|---|
| `12강` | `lectures.count` (only courses that count lectures) |
| `11/16 수업까지` | `lectures.last` (through the class of that date) |
| `국문 112p`, `영문 96p` | `pages.ko`, `pages.en` |
| `2026.11.21` | the date part of `updated` |

The newest `updated` among all courses becomes the "LAST UPDATED" stamp under
the intro. A failed fetch leaves the line empty, silently.

## The link-preview card

`og-card.tex` draws a 1200×630bp page in TikZ: background `#08080a` with a
faint amber radial glow at the top right, a hairline, the term in amber, the
hub name in very large Korean type, one or two lines of course names joined by
centred dots in `--ink-2`, another hairline, and the hub URL in `--dim`.
`pdftoppm -r 72` turns it into exactly 1200×630 pixels.

Meta tags carry the card: `og:type`, `og:site_name`, `og:locale ko_KR`,
`og:url`, `og:title`, `og:description`, `og:image` (+ `secure_url`, type,
width, height, alt) and the `twitter:` equivalents with
`summary_large_image`. Image URLs are absolute and end in `?v=N`; raise N after
every change of the card, because messengers cache previews per URL.

## Thumbnails

`make-thumb.py` renders page 1 of the English notes at twice the target width
in greyscale, maps paper → `#0d0e12` and ink → `#f4f1ea` linearly (a duotone,
so it reads as a dark page rather than a negative), downsamples to 700px with
a light unsharp mask, and saves a progressive JPEG (quality 86). Letter paper
gives 700×906, A4 700×990. Re-make a thumbnail only when the title page
changes noticeably (a new title, a new term).

History: the first previews were interior pages, which turned to grey mush
at preview size, so every course looked alike; the title page, with its
display type, is what tells courses apart. Rendering at about 200 dpi (twice
the target width) and resampling with a light unsharp pass keeps the small
type crisp; the cursor preview grew to about 310px so the titles read. If a
title page carries a person's name or e-mail (a lab handout with a TA's
contact, say), use a content page instead: the hub is reachable by anyone with
the link.
