# Variants still deployed, and the history of fixes

The viewer started as one file copied into each course's `docs/` and was fixed
course by course. Older copies are still deployed; knowing what each lacks
helps when the student reports a glitch on one site but not another.

## Variants

| Variant | Used by | Has | Lacks |
|---|---|---|---|
| Baseline (≈1,060 lines) | most courses at mid-term | language switch at a section, contents drawer with sticky part headers, canvas→image rendering, reserved widths | keeping the place across a resize; tabs; solutions |
| Baseline + resize hold | the long textbook-companion notes | `spot` / `holdSpot` / `ResizeObserver` | tabs; solutions |
| Two documents, manifest ranges | a course with a practice-problem book | a second document at `?tab=problems`, a per-document settings object, solution page ranges read from the manifest (`"prob": {"pages": …, "sol": {"en": [[3,3],[5,5],…]}}`), problem pages made 30in tall and cropped to their content so each problem and each solution is one sheet | named-destination ranges, `?doc=` routing for any number of documents |
| **Current** (`assets/index.html`) | the latest course | `DOCS` list, `?doc=` routing with `pushState`, tabs as real links, solution ranges from named destinations in the PDF, `sol:` anchors in the language switch, resize hold | — |

To upgrade an older site: copy the current file, then re-create its settings
block and the three HTML places from the old file, adapt the manifest if it
used `prob.sol`, and run the test.

A different kind of site served a lab course: not a PDF viewer but one HTML
file of tabbed study pages (before the lab, grading, one tab per experiment,
lab-notebook format, report writing), assembled from `site/parts/*.html` into
`site/_shell.html`. Its "자료실" (library) tab opens a PDF **from the reader's
own device** in the browser: the lab manual is a published book and is never
uploaded.

## Glitches and their fixes

In the order they were met. Each one is still guarded against in the current
file.

1. **Korean text missing in the rendered pages.** pdf.js needs CMaps for the
   Korean fonts; cdnjs does not serve them. → CMaps and standard fonts from
   jsdelivr's `pdfjs-dist` of the same version.
2. **The language switch landed on the wrong section.** The two editions have
   different page counts. → Match by section number from the bookmarks.
3. **…and still drifted by a page on each round trip.** Positions were whole
   pages. → Fractional positions from each destination's top.
4. **Bookmarks without numbers.** `hyperref` drops the number from article's
   `\numberline` unless `bookmarksnumbered=true`; without numbers there was
   nothing to match. → The option in every course style.
5. **All subsections of a section collapsed onto one key.** amsart writes
   "2.3. Title", article "2.3 Title"; a regex requiring the dot cut "2" from
   "2.3 Title". → Optional dot, then whitespace.
6. **Parts treated as sections.** A numbered part bookmark looked like a
   section. → Parts unnumbered in the bookmarks (`\partdivider`).
7. **The tab stuttered after coming back to it.** Kept canvases held hundreds
   of MB; the GPU re-uploaded them. → Draw to canvas, keep a PNG `<img>`,
   free the canvas.
8. **Blank sheets inside an app's built-in browser.** It reported
   `visibilityState: hidden` while visible, and drawing paused. → Never pause
   on visibility.
9. **The language toggle jumped** when the date arrived, when the page count
   gained a digit, when the contents button appeared, when the scrollbar
   appeared, when a tab became bold. → Reserved widths, `visibility` instead
   of `display`, `scrollbar-gutter: stable`, `::after` width holders.
10. **A closed contents panel covered the text.** An ID selector's `display`
    beat the `hidden` attribute. → `[hidden]{display:none !important}`.
11. **Pressing the contents button right after closing did nothing.** The
    fading backdrop caught the click. → No pointer events while fading.
12. **A rapid second language click was lost.** → `pending` queue.
13. **Rotating a tablet or resizing a window moved the reader to another
    page.** → `spot` kept in page terms, restored before paint, measured only
    on user scrolls.
14. **Solutions visible for an instant** before being covered. → Do not draw a
    solutions document until its ranges are known.
15. **Switching language while reading a problem opened its solution.** →
    `sol:<id>` anchors.
16. **Rows showed through the sticky part header.** The bar colour is
    translucent. → Paint it twice.
17. **The sticky header let go in the gap between parts.** The gap was
    padding, outside the box the header sticks within. → An empty `::after`
    block inside the part's box.
18. **The section just chosen in the contents was not the one marked.**
    Scroll positions round to whole pixels. → 3px slack.
