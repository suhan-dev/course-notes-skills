# Document structure

One document per language, read from start to finish like a short book. This
is the order of things and the reasons behind it.

## 1. Front matter (unnumbered, before the table of contents)

| English | Korean | Content |
|---|---|---|
| masthead (`\makelecheader`) | same | course name and term on the left, "Updated 6 September 2027" / "2027년 9월 6일 기준" on the right, the title between double rules, then lecturer and note-taker if given |
| Course information | 수업 정보 | meeting times, exam dates, grading, textbook: only what the syllabus or the instructor announced |
| The arc of the course | 강의의 흐름 | one line per part with its state: done / in progress / planned. A planned item needs evidence (the instructor said so in class, the posted schedule) |
| How these notes are organised | 이 노트의 구성 | a few sentences: topic order, what a lecture break and a source note are, what the ▸ scribe notes are |
| Lecture log | 회차표 | one row per lecture: number, date with weekday, the sections it added, `\pageref{lec:<date>}` |
| Contents | 차례 | `\tableofcontents`, small |

All of these are `\section*`. If one of them should appear in the PDF
bookmarks, add `\phantomsection\pdfbookmark[1]{The arc of the course}{arc}`
before it: an unnumbered bookmark is ignored by the viewer's place matching,
which is what we want.

## 2. Parts

```latex
\partdivider{Part III --- The covariant derivative}      % English
\partdivider{제3부 --- 공변 미분}                           % Korean
```

- A part is a **topic**, not a week. It starts on a fresh page with the title
  in small capitals between hairlines.
- It enters the table of contents and the PDF bookmarks at part level, one step
  above sections, **without a number**. The viewer treats any bookmark that
  starts with a section-style number (`3`, `3.2`, `A`, `A.1`) as a place to
  match across the editions; a numbered part would be mistaken for a section.
  The roman numeral lives inside the title text only.
- Open a new part only when a genuinely new topic begins. Material that extends
  an earlier topic goes back into that part, even weeks later.

## 3. Sections, subsections, numbering

- `\section{…}\label{sec:<slug>}`. Slugs are words (`sec:geodesic`), never
  numbers, so moving a section does not make its label lie.
- Sections number straight through all parts (1, 2, …, 24) and never restart
  per part. Once a number has been published it never changes: the viewer
  remembers the reader's place by section number, the student annotates by
  number, and the two editions are matched by it.
- If a section has to be inserted between published ones, make it a subsection
  of the earlier section, or add it at the end of the part and cross-reference
  it. Do not renumber.
- Equations are numbered straight through the document: (1), (2), … (352).
  Theorem-like environments and cautions share one counter per section
  (Definition 3.1, Example 3.2, Caution 3.3).
- Subsections are fine; sub-subsections are rarely worth it. Some courses used
  run-in subsections (heading and text on one line) to save space.

## 4. Lecture breaks and source notes

```latex
\lecturebreak[2027-09-14]{Lecture 3}        \lecturebreak[2027-09-14]{제3강}
\sourcenote{Handout 3-1 and the recording.}  \sourcenote{강의 자료 3-1과 녹음.}
```

- The break is a hairline with the lecture label (and the date, printed in the
  edition's language) at the right margin, placed **where that lecture's new
  material begins**. It is a mark, not a division: no ToC entry, no bookmark.
- Give the date only when it is certain. With a date the break sets
  `\label{lec:2027-09-14}`, which the lecture log reads with `\pageref`, and
  which `tools/lectures.py` reads for the site.
- Name the lecture as the source names it. If the handwritten title on page 1
  says "Lecture 7", it is Lecture 7 even when the file is called `6-2_…`.
- When a lecture continues an earlier part, the break goes inside that part.
  The breaks therefore do not appear in date order through the document; the
  lecture log does.
- Several lectures written up as one block get one break and one log row:
  `\lecturebreak{Lectures 7--10}` and a row `7--10 & Wed, 23 Sep -- Wed, 7 Oct`.
- `\sourcenote{…}` right under the break says what the notes for that lecture
  rest on, especially when it is unusual: "no recording; the handwriting
  only", "no record of this class; reconstructed from the posted notes",
  "the board was not recorded; filled from the instructor's notes from an
  earlier year".
- Text written before a class, when the student asks for it:
  `\lecturebreak[date]{Planned}` / `{예정}`, no log row. After the class,
  check it against the class, then rename the break and add the row.

Alternatives used by courses taught from slide decks: `\deckbreak{Deck 3}` /
`\deckbreak{강의자료3}` where a deck's material first appears (once in every part
where that deck appears), or no breaks at all and a table in the front matter
that maps slide files to sections.

## 5. Inside a section

- **Definitions** (`definition`) for every new term, with the term in
  `\keyword{…}` at its point of definition.
- **Derivations** written out in full, each step either shown or one line of
  justification away. Number an equation only if it is referred to later or
  is a result worth finding again.
- **Examples** (`example`) the class worked, plus `\scribe{…}` examples the
  notes add (marked).
- **Key results** in a `keybox`, sparingly: one or two per section at most.
- **Cautions** (`caution`, numbered, optional short title) for subtleties a
  reader would get wrong: a convention clash, a limit that does not commute,
  a sign that depends on whose point of view. Not for recording slips in the
  source.
- **Figures** from the shared `figures.tex` (see `figures.md`).
- **Cross-references** `\S\ref{sec:…}`, `\eqref{eq:…}`,
  `Figure~\ref{fig:…}` / `그림~\ref{fig:…}`. Refer back instead of re-deriving.
- **Scribe notes** (`\scribe{…}`) for anything the lecture did not give: a
  missing step, a check by another route, a limiting case, a dimension check.
  Small type, ▸ in the margin. They make it possible to add help without
  blurring what the course actually taught.

What does not go in:

- Attributions to the source ("as the professor said", "handout p. 3",
  "the recording at 41:10").
- Copies of the source's slips. Write the correct version; list the correction
  in the report.
- Anything the class did not reach.
- Repetition of earlier material.

## 6. Labels

| Prefix | For |
|---|---|
| `sec:` | sections and subsections |
| `eq:` | equations |
| `fig:` / `tab:` | figures, tables |
| `def:` `thm:` `prop:` `ex:` `caut:` | theorem-like environments |
| `lec:` | set by `\lecturebreak[date]` only |

Labels are identical in the two editions. `tools/labelcheck.py` compares every
`\newlabel` in the two `.aux` files (name and number) and the numbered PDF
bookmarks, and fails on any difference.

## 7. Errors in the source material, three policies

1. **Silent correction, listed in the report** (default). The notes say the
   right thing; the student gets a list of every place the source was wrong.
   This keeps the notes clean for exam study.
2. **A visible `review` box** (Check / 검토) where the lecture's own argument
   does not survive checking: the box gives the argument's gap and the
   correct reasoning. Good for an advanced course where the gap is itself
   instructive.
3. **Correct in the text; record the source slip in the repository README**
   (a list "the posted notes have …; the notes write …"), for courses whose
   posted notes are the primary source for some lectures.

Choose once per course and write the choice at the top of both editions.

## 8. End of document

`\phantomsection\label{lec:end}` as the last thing, so the lecture log or a
script can find where the last lecture's material ends.
