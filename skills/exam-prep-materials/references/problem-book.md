# Problem books

A problem book is a second document of the course site ("문제풀이" tab next to
"강의노트"), in both languages, in which problems and solutions alternate:
every problem starts a new page and its solution starts the next new page. On
paper you can work a problem before turning the page; in the viewer the
solution pages stay covered until tapped.

## Files (in the course repository)

```
problems-en.tex  problems-ko.tex       the two editions (masthead, how-to page, \input chapters)
problems/common.tex                    the macros below
problems/figs.tex                      shared figures, if any (same rules as the notes' figures)
problems/en/ch1.tex … chN.tex          one chapter per topic, English
problems/ko/ch1.tex … chN.tex          the same chapters, Korean
tools/probcheck.py                     both editions match; where each problem sits
```

`./build.sh problems` builds both editions with latexmk and runs
`probcheck.py`; `./build.sh` builds the problem book after the notes whenever
`problems-en.tex` exists. The PDFs are `Problems-EN.pdf` / `Problems-KO.pdf`;
`publish.sh` copies them to `docs/` and adds `docs.problems.pages` to the
manifest.

## Macros (`problems/common.tex`)

| Macro | Does |
|---|---|
| `\probchapter{Title}{Notes §16--§17}` | new page, chapter number (section counter), title, the notes range in italics; a bookmark "3 Title" |
| `\problem{Title}{Source}{Notes §}` | new page (except right after a chapter head), problem number n.m (subsection counter), the source and the related sections on one line; a bookmark "3.2 Title (Source)"; the named destination `pb.prob.3.2` |
| `\solution` | new page, "Solution 3.2  Title"; the named destination `pb.sol.3.2` |
| `\solpart{a}{Short title}` | a part of a solution |
| `parts` environment | (a), (b), … in a statement |
| `\ans{…}` | a boxed final answer |
| `\pbmark{end}` | after the last solution, on a new page, before any back matter, so the last solution's cover ends there |
| `\probheads` | running head: the current problem or solution on the right |

Equations restart in every problem ((1), (2), … inside 3.2).

Each edition defines `\ProbWord`, `\SolWord`, `\SourceWord`, `\NotesWord`
(Problem / 문제, Solution / 풀이, Source / 출처, Notes / 노트).

## How the viewer finds the solutions

The PDF itself carries the ranges: a solution is covered from the page of its
`pb.sol.<id>` destination to the page before the next `pb.*` destination, or
to the end. No page numbers in the manifest, nothing to keep in sync. The
prefix `pb` must equal `MARK` in the viewer's settings. The viewer also adds
each solution start to its language-switch anchors, so switching language
while reading problem 3.2 lands on problem 3.2, not on its solution.

## What a chapter looks like

```latex
\probchapter{The canonical ensemble}{Notes \S20--\S21}

\problem{A two-level system}{Final 2021, 1}{\S20.2}
Statement, with all data and what is asked.
\begin{parts}
  \item …
  \item …
\end{parts}

\solution
\solpart{a}{The partition function}
… every step …
\begin{equation}
  \ans{Z=1+e^{-\beta\varepsilon}}
\end{equation}
Check: …
```

## Choosing problems

- Scope by notes sections (for example the final-exam range only); one
  chapter per topic, in the order of the notes.
- Sources, in order: the instructor's past exams (with official solutions
  where they exist), the instructor's problem sets and worked examples,
  earlier mock exams, then new problems for what the past ones do not cover.
- Pitch at the level of the latest real exam (see `exam-level.md`): include
  unfamiliar systems given only through an equation of state, a
  "to leading order" part, a symmetry-broken generalisation.
- Extend past problems with new parts when they are too easy; say
  "+ new parts" in the source line.
- Note convention differences in the solution (for example a density of
  states with or without the spin degeneracy).
- Where the class has not yet reached a topic a problem needs, the solution
  explains the idea briefly and says so.

## Writing solutions

- Start with the set-up: what is given, what is held fixed, what is asked.
- Every step written; every derivative with what is held fixed.
- Box the final answers; add a check (limit, units, sign, a special case).
- Verify every number with a script; keep the scripts.
- Prose, not bullet lists, between equations.
- Korean edition: same equations, same order, Korean prose; particles after
  numbers as in the notes.

## The front pages

- Title masthead (the notes' `\makelecheader`), contents.
- "How to use this collection": the alternating layout and the covered
  solutions, the sources and their labels, notation, conventions that differ
  between sources, anything scheduled after the book was written.
- "Useful mathematics and constants" if the exam allows a formula sheet.

## Tall-page variant (one sheet per problem)

`assets/tall-page-problems/`: for courses whose problems and solutions are
short, or when every problem and every solution should be exactly one sheet
in the viewer.

- `tallproblems.sty` (load after the course style) sets 30-inch-tall paper, no
  running head or foot, and provides `\probpart{Part title}` (an unnumbered
  top-level bookmark), `problem` environment `{title}{stars 1–3}`, `solution`
  environment, `parts`, `\sol{a}`, an `answer` box, and `\problemlist` (a list
  of problems with difficulty stars on the first page, written through a
  `.ptl` file like a table of contents).
- It writes the same destinations (`pb.prob.N`, `pb.sol.N`) and the labels
  `probstart:N` / `solstart:N`, so the same viewer and `probcheck.py` work.
- After building, `python3 crop.py Problems-EN.pdf Problems-KO.pdf` measures
  each page's ink with Ghostscript's `bbox` device and raises the bottom of
  the MediaBox/CropBox to 40pt below the lowest ink (pages never under 2.5in).
  The top stays where it was, so bookmarks and links still land correctly.
  Needs `gs` and `pypdf`.

An older form of this variant gave the viewer the solution page ranges in the
manifest (`"prob": {"sol": {"en": [[3,3],[5,5],…]}}`, from a script reading the
labels); named destinations made that unnecessary.

## probcheck.py

```
       EN  prob | sol   KO  prob | sol
1.1      3 | 4            3 | 4
1.2      5 | 6-7          5 | 6-7
OK: 3 problems, EN 8 pages, KO 8 pages
```

It fails when the editions differ in chapters, problems or their order, when
a problem has no solution, or when page labels are not plain numbers.
