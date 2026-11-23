# Cheat sheets and derivation summaries

## Cheat sheet (allowed formula sheet or a one-look review)

Built as HTML and printed to PDF with Playwright: CSS grid columns, KaTeX for
the mathematics, inline SVG figures. HTML gives fine control of dense layout,
and the browser can measure and pack the boxes.

### Files (`assets/cheatsheet/`)

| File | Role |
|---|---|
| `content.py` | the content: title, part colours, and `BOXES`, a list of (part, chip, title, HTML body) |
| `build.py` | writes `cheatsheet.html`; the browser packs the boxes into A4 pages of three columns after the fonts load, adding pages as needed, and writes each page's section range in its header |
| `pw.js` | Playwright: waits for packing, prints how full each column is (%) and its overflow in pixels and the number of KaTeX errors, then prints `cheatsheet.pdf` |

```sh
npm pack katex@0.16.9 && tar xzf katex-0.16.9.tgz       # once
KATEX_DIST=$PWD/package/dist python3 build.py && node pw.js
```

### Rules

- **Every LaTeX string in Python is a raw string** `r'…'` (`"\frac"` starts
  with a form feed, `"\b"` is a backspace).
- **No raw `<` or `>` inside `$…$`** (it opens an HTML tag); `build.py`
  converts them to `\lt` / `\gt`.
- **Fill**: every column under 100%, overflow 0, KaTeX errors 0. Aim for
  96–98% when the student wants "as much as possible".
- **Body size** is the lever: one sheet used 7.25pt for derivations, the
  largest that still fit. When an edition runs longer (English often does),
  lower its size slightly (6.45–7pt) or move a box, rather than cutting
  content.
- **Colour by part of the notes**, with a legend in the header, so a box shows
  where it belongs.
- **Each derivation box opens with a set-up line**
  `설정 · 고정 · 바꿈 · 극값` (set-up · held fixed · varied · extremised), from
  `st()` in `content.py`. Students said this line was what made a derivation
  usable under exam pressure.
- **A map of extremum principles** (for each setting: what is fixed, which
  potential is extremised) and a **problem-type → set-up table** are worth a
  band across the top of the first derivation page.
- A box "헷갈리는 것" for notation and sign traps (whose work, which `h`, words
  used in two senses).
- Content outside the notes is tagged.
- Both editions when the notes have both: same boxes, same order; the
  English edition may need a smaller size.
- Deliver to the Mac course folder as well (`치팅시트/`), and replace it after
  every rebuild.

### Figures

Small SVGs drawn from computed data (a script writes them into a JSON the
builder reads), greyscale or the part colour, labels in the sheet's language.
A numerically solved curve (a coexistence curve, say) is computed, not
sketched.

## Derivation summary ("유도 총정리")

A PDF, typically the night before an exam, of every derivation in one area
(for example everything thermochemical: chemical potential, mixing, reaction
equilibrium, osmotic pressure, boiling and freezing points, dilute
solutions).

- LaTeX with the notes' style, one file, Korean (or the student's language).
- Before every extremum argument a set-up box with four fields
  (set-up · held fixed · varied · extremised), and both the first- and the
  second-order condition checked.
- Results outside the notes tagged "[노트 밖]"; name clashes flagged (when the
  notes call one formula by a name a textbook uses for another).
- Extend the existing summary for the next exam rather than starting over.
- A README with the rebuild command next to the source.
