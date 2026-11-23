# Behaviour, and the reason for each piece

Line references are to `assets/index.html`. The comments in that file (in
Korean) give the same reasons next to the code.

## 1. The screen

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ☰ 목차  Course name  [강의노트|문제풀이]  2027-09-06 21:40 KST  (English|한국어)   ↓  12 / 86 │
└──────────────────────────────────────────────────────────────────────────┘
        ┌──────────── page 1 (image) ────────────┐
        │                                         │   grey backdrop, white sheets,
        └─────────────────────────────────────────┘   max 980px wide, 16px apart
```

- A sticky bar, 44px high (42px on phones), translucent with a backdrop blur.
  Left: the contents button (☰ 목차). Then the course title (a long and a
  short form), the document tabs when there is more than one document, and
  the time of the last publish. Centre: the language switch, a segmented
  control with a sliding knob. Right: download (↓) and the page indicator
  (`12 / 86`).
- Pages are white sheets with a hairline border and a soft shadow on a grey
  backdrop, at most 980px wide, aspect ratio taken from the PDF.
- Dark mode (`prefers-color-scheme: dark`) darkens the bar, backdrop and
  drawer; the paper stays white, and so do the solution veils.

### Nothing moves under the reader

The centre of the bar must not shift while the page loads or while the reader
scrolls. Each element that changes late reserves its final width from the
first paint:

| Element | Problem it caused | Fix |
|---|---|---|
| update time | arrives with the manifest; the toggle jumped left | `min-width: 19.2ch` (the format is always `YYYY-MM-DD HH:MM KST`, 20 characters) |
| page indicator | `–` → `1 / 32` → `100 / 216` widened at each digit; the toggle moved while scrolling | `min-width: 8.2ch`, tabular numerals (fits `999 / 999`) |
| contents button | enabled only after the bookmarks are read; the toggle jumped 33px (16px on phones) | always laid out, `visibility:hidden` + `disabled` + `aria-hidden` + `tabindex=-1` while unusable |
| bold current tab | bold text is wider; the toggle moved on every tab change | each tab reserves its bold width with an invisible `::after { content: attr(data-label) }` |
| language buttons | bold active label widened the control | fixed button width (5.9em; 5.3em / 3.7em on phones) |
| vertical scrollbar | appears when pages arrive and disappears when they are cleared; 15–17px shift | `html { scrollbar-gutter: stable }` |
| the knob | slid on first paint when the saved language was restored | `.noanim` until after the first frame (and a 400ms timer, because background tabs run no animation frames) |

### Collapsing on narrow screens

Less important things fold first, by width only (folding by content would make
things appear and disappear and move the toggle):

| Width | Change |
|---|---|
| ≤ 800px with tabs | hide the update time |
| ≤ 680px | hide the update time |
| ≤ 640px with tabs | hide the course title (the tab says which document it is) |
| ≤ 560px | compact bar; short title; contents button shows only ☰; with tabs, the language buttons read EN / 한국어 and the title disappears; the contents drawer becomes a bottom sheet |
| ≤ 350px | hide the page indicator |

`prefers-reduced-motion: reduce` turns every transition off.

A global `[hidden] { display: none !important }` is needed because several
elements get `display` from ID selectors, which beat the `hidden` attribute's
default style: without it a closed contents panel stayed on screen over the
text.

## 2. Loading

1. `fetch('manifest.json', {cache: 'no-store'})`. The update time goes into the
   bar.
2. `docs` = the entries of `DOCS` that have at least one edition in the
   manifest (the first document's page counts are `pages`, the others'
   `docs[id].pages`). Two or more → tabs.
3. The document comes from `?doc=<id>` (the first document has no query).
4. The language comes from `localStorage[LS_LANG]`, else `DEFAULT_LANG`; if
   that edition of this document does not exist, the other one.
5. `#page=N` in the URL opens at page N.
6. The PDF URL is `files[lang] + '?v=' + manifest.version`, so every publish
   gets new URLs and no cache can show an old edition. The download link
   points at the same URL with the `download` attribute.
7. pdf.js 3.11.174 from cdnjs (library and worker). Character maps (CMaps)
   and standard font data come from jsdelivr's `pdfjs-dist@3.11.174`, because
   cdnjs does not serve them; without CMaps, Korean text in the PDFs renders
   as empty boxes.
8. One `div.page` per page is created at once, with the aspect ratio of
   page 1 (each page corrects its own ratio when drawn) and
   `content-visibility: auto`, so the scroll height is right from the start
   and off-screen pages cost no paint. An undrawn page shows a faint
   "불러오는 중…" (loading…) so a slow connection does not look broken.

Failures show a short message in the page instead of a blank screen: pdf.js
did not load (network), the manifest could not be read, a PDF could not be
read (naming the file).

## 3. Rendering pages

- An `IntersectionObserver` with a 900px margin queues pages near the
  viewport. One page is drawn at a time, nearest first; pages that drifted
  more than `max(1600px, 2.5 × viewport height)` away leave the queue.
- Scale = page width in CSS px × `min(devicePixelRatio, 2)` / PDF width. A
  third device pixel adds no legibility, only 2.25× the pixels. One page is
  capped at 6 million pixels so a large monitor does not stall on one page.
- Each page is drawn to a canvas, converted to a PNG blob, shown as an
  `<img>`, and the canvas is freed at once. Keeping canvases cost hundreds of
  MB for a 20-page document, and when the reader came back to the browser tab
  the GPU had to re-upload them: seconds of stutter. Images are decoded only
  when visible and are cheap to drop and re-decode.
- The old image of a page is released only after the new one has loaded, so
  a redraw never flashes an empty sheet.
- `page.cleanup()` after each page releases pdf.js's per-page resources.
- Drawing does not pause when `document.visibilityState` is hidden: some
  in-app browsers (web views) report hidden while visible, and pausing left
  blank sheets. On becoming visible the queue is pumped again.
- A generation counter cancels the work of an edition that was replaced
  (language or document switch), and the running render task is cancelled.

## 4. Remembering the reading place

- Per document and language, `localStorage[LS_POS + (id + '.' unless first
  document) + lang] = {p, o}`: page and the fraction of that page above the
  bar. Saved 250ms after scrolling stops, on `pagehide`, and when the page is
  hidden (phones often switch apps without `pagehide`).
- When an edition opens, the place is, in order: the `#page=` target; the
  place carried over from the other language (below); the saved place; the
  top.
- Switching to another **document** does not carry the place; it opens that
  document where the reader left it.

## 5. Switching language at the same section

The two editions have different page counts (Korean runs longer), so a page
number is meaningless across them. The section numbers are the same.

1. When an edition opens, its outline is read once and cached: for each
   bookmark, the **key** is its leading number, `2`, `2.3`, `A`, `A.1` (regex
   `^\s*([0-9]+(?:\.[0-9]+)*|[A-Z](?:\.[0-9]+)*)\.?(?=\s|$)`, which accepts
   both article's "2.3 Title" and amsart's "2.3. Title"); a bookmark without a
   number gets its path in the tree (`#1.2.3`), which still matches when the
   two trees have the same shape.
2. Its **position** is the page index plus the fraction of the page above the
   destination (from the `XYZ` / `FitH` / `FitBH` top and the page's view
   box). With page numbers only, several sections on one page collapsed, and
   a section starting low on a page counted as already passed while reading
   its top: each round trip drifted a page.
3. `whereAmI()` turns the current scroll into "section key, fraction through
   that section" (plus the fraction through the document as a fallback).
4. `locate()` finds the same key in the other edition and the same fraction
   through it. No key → same fraction of the whole document.
5. In a problem book, the start of each solution is added as its own key
   (`sol:<id>`): otherwise a problem and its solution formed one span, and
   switching language while reading a problem could land on its solution.

Clicks during a load are not dropped: the last request is kept in `pending`
and run when the current load finishes (the knob moves at once). Earlier the
viewer ignored clicks while busy and sometimes ended in the language that was
not clicked last.

## 6. Keeping the place across a resize

Page heights follow the width. After a resize the browser keeps the scroll
offset in pixels (Safari) or the top of the page in view (Chrome and Firefox
scroll anchoring), and both now point elsewhere: halve the width and the same
pixel offset is twice as far into the document. The first fix restored "the
current page" 220ms after resizing stopped, but the current page was often
measured after the jump, and the position within the page was lost.

Now the viewer keeps `spot = {p, o, w, y}` (page, fraction of that page above
the bar, the page width when measured, the scroll offset it set). On every
`resize` event and in a `ResizeObserver` on the viewer (both run after layout,
before paint), if the page width changed it scrolls to the same page and
fraction at the new height. No wrong position is ever painted, even while
dragging the window edge. `spot` is re-measured only when the reader scrolls
(the offset differs from the one the viewer set), so rounding never
accumulates and narrowing then widening returns exactly. A height-only change
(a phone's address bar folding) is ignored, so the viewer never fights a
scrolling finger. Images are redrawn at the new width 220ms after resizing
stops; their boxes already have the right size, so nothing moves.

## 7. Contents (table of contents)

- Built on first open from the cached outline rows, so it asks pdf.js
  nothing more; rebuilt for the other edition when the language or document
  changes (in place, if the panel is open).
- Desktop: a drawer from the left, `min(340px, 86vw)` wide, over a dimmed
  backdrop. Phones (≤ 560px): a bottom sheet up to 72% of the height, rounded
  top corners, so the reader still sees where they are.
- A top-level bookmark with children is a **part header**: bigger, bold, a
  thin rule above, and **sticky** at the top of the list while its sections
  scroll under it, pushed away by the next part. Top-level bookmarks without
  children (front or back matter) stay plain rows. The decision uses only the
  shape of the tree, so it works whatever the parts are called (Part I,
  Appendix A, 제3장). The gap between parts is inside the part's box
  (`::after`), so the header stays stuck through the gap; the header paints the
  translucent bar colour twice so rows passing under it do not show through.
- Indentation by depth; a bookmark whose destination cannot be resolved is
  shown but not clickable.
- The section being read is marked (`.cur`, `aria-current`), with 3px of
  slack so the section just jumped to is marked rather than the one before
  it. Opening the panel scrolls the list (not the page) so the marked row is
  visible below the sticky header.
- Keyboard: focus goes to the marked row; ↑/↓, Home/End move; one roving tab
  stop in the list; Tab cycles only through the panel's controls (the
  reveal-all button, close, the list); Escape closes and returns focus to the
  button.
- Closing: the `.in` class is removed, and `hidden` is set only after the
  slide-out ends (`transitionend`, or a 400ms timer when no transition runs),
  so a closed panel never keeps focus, screen-reader presence or clicks. The
  fading backdrop takes no pointer events, so pressing the button again
  right after closing works.
- The button is unusable (invisible, still occupying its place) for an edition
  without bookmarks and while a new edition loads.

## 8. Document tabs and routing

- Each tab is a real link: the first document is the bare path, the others
  `?doc=<id>`. ⌘/Ctrl/Shift-click and middle-click open a new browser tab as
  usual; a plain click switches documents in place with `pushState`, so Back,
  reload and copying the address all keep the document. `popstate` switches
  back.
- With several documents, `document.title` follows the document's title.
- The language choice is shared by all documents; reading places are kept per
  document and language. A missing edition locks its language button for that
  document, with a tooltip ("한국어판 준비 중입니다" / "English edition not
  available yet").

## 9. Covered solutions

For a `DOCS` entry with `solutions: true`:

- The PDF carries named destinations `<MARK>.prob.<id>` where problem *id*
  starts, `<MARK>.sol.<id>` where its solution starts, and `<MARK>.end` where
  back matter after the last solution starts (written by the problem book's
  `\problem`, `\solution` and `\pbmark{end}`). A solution covers its pages
  from its `sol` mark to the page before the next mark, or to the last page.
  The PDF itself carries the ranges, so nothing in the manifest can disagree
  with it.
- Pages of such a document are not drawn until the ranges are known, so a
  solution never flashes uncovered.
- A veil is a button laid over the page image: a pale striped sheet reading
  "풀이 1.2" ("(이어짐)" on continuation pages) and "눌러서 풀이 보기". The text
  sits near the top so it is visible where the solution begins on a large
  screen. Because the veil lies on top of the image, revealing changes no
  layout.
- Tapping reveals every page of that solution. Revealed solutions are kept by
  id in `sessionStorage` per document: they survive a reload and a language
  switch, and are forgotten when the browser tab closes, so the next study
  session starts covered.
- The contents header gets "풀이 모두 보기" (reveal all) or "풀이 모두 가리기"
  (cover all), depending on whether anything is covered.

## 10. Accessibility

`aria-pressed` on the language buttons, `aria-current` on the current tab and
the current contents row, `aria-expanded` on the contents button, the panel is
`role="dialog" aria-modal="true"`, visible focus outlines everywhere,
`aria-live="off"` on the page indicator (it changes on every scroll), `lang`
on `<html>` follows the edition.
