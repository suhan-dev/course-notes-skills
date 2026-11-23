# The style file, and why it is that way

`assets/course-template/coursenotes.sty` is the shared style for both editions.
`\usepackage{coursenotes}` for English, `\usepackage[korean]{coursenotes}` for
Korean. Each course renames it (`<course>notes.sty`) and its internal prefix
(`cn@`) when it adds course-specific macros.

## Look

- MIT-OCW-scribe-note look: `article`, 11pt, letter paper, 1in margins, a
  ruled masthead instead of a title page, bold left-aligned section heads, a
  running head (title left, date right), page number centred at the foot.
- **Black and white only.** Boxes differ by their rules (heavy left rule,
  thin closed frame, rules above and below), never by colour. The notes are
  printed and read on e-ink as often as on screens.
- No paragraph indent, a small paragraph skip, `\emergencystretch=3em`: the
  prose is full of unbreakable inline mathematics.
- `\Needspace` before sections (6 lines), subsections (4 lines) and lecture
  breaks (8 lines): a heading or a break is never stranded at a page foot.

## Fonts

- Both editions compile with **XeLaTeX**, so they share Latin Modern for Latin
  text and mathematics and the same microtype behaviour.
- Korean: `xetexko` with `[hangul]`, Nanum Myeongjo for text, Nanum Gothic for
  sans and mono. macOS registers these as "Nanum Myeongjo" / "Nanum Gothic";
  Debian's `fonts-nanum` registers "NanumMyeongjo" / "NanumGothic". The style
  takes whichever exists (`\IfFontExistsTF`). Older style files asked for the
  macOS names only; `tools/setup-container.sh` also installs renamed copies so
  those build in a container.
- Expect harmless warnings in the Korean build: microtype "Unknown slot
  number" for Hangul, and a missing small-caps shape for Nanum (small capitals
  in a lecture break fall back to upright).

## Bookmarks

`hyperref` with `bookmarksnumbered=true`. Without it the PDF outline says
"Diffusion" instead of "2 Diffusion", and the viewer, which matches the
reader's place across the two editions by these numbers, has nothing to match.
Links are black.

## Commands

| Command | Does |
|---|---|
| `\coursename` `\courseno` `\term` `\lectitle` `\lecdate` `\lecturer` `\notesby` | masthead fields; `\lecnum` adds "Lecture N:" for single-lecture documents |
| `\makelecheader` | prints the masthead and sets the running head |
| `\isodate{2027-09-14}` | "14 September 2027" / "2027년 9월 14일" |
| `\partdivider{Part I --- Title}` | new page, title between hairlines, ToC and bookmark at part level, unnumbered |
| `\lecturebreak[2027-09-14]{Lecture 3}` | hairline with the label at the right margin; with a date also `\label{lec:<date>}` |
| `\sourcenote{…}` | grey line under the break: what this lecture's notes rest on |
| `\scribe{…}` | the note-taker's addition: small, indented, ▸ in the margin |
| `\keyword{…}` | a term at its point of definition (bold) |
| `\d` `\dv` `\pd` `\pdc{U}{S}{V,N}` `\avg` `\vv` `\bs` `\mat` `\T` `\half` | notation |

Environments: `definition`, `example`, `theorem`, `proposition`, `lemma`,
`corollary`, `remark`, `note` (one counter per section), `proof`, `caution`
(numbered, heavy left rule), `review` (heading Check / 검토), `keybox` (thin
frame), and the optional reading boxes `why`, `glance`, `procedure`,
`pitfall`. Environment names are the same in both languages; the style prints
the words in the edition's language.

`review` is not called `check` because amsmath already defines `\check` (the
accent): `\newenvironment{check}` fails with "Command \check already defined".

## Adding course macros

Put them in the course's style file, not in the editions, so both editions get
them. Words that the style prints go in its two word lists (`\cn@…word`).
Words inside figures go in the editions' preambles as `\lbl…` macros (see
`figures.md`).

## Captions

Small type, "Figure 3." in bold, centred when it fits on one line. In the
Korean edition `xetexko` already prints 그림 and 표.
