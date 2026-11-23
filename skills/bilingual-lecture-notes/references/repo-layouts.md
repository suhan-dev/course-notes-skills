# Repository layouts

Four layouts were used. All of them produce two PDFs with identical numbering
and publish them with the same viewer; they differ in how the sources are
split.

## A. One file per edition (the default)

```
notes-en.tex   notes-ko.tex   figures.tex   <course>notes.sty
build.sh   publish.sh   tools/   docs/   README.md
```

- Right for most courses, up to roughly 3,000–5,000 lines per edition.
- Both editions are complete documents (preamble, front matter, body).
- `build.sh` builds into `build/`; `publish.sh` copies the PDFs to the root and
  to `docs/`.
- This is `assets/course-template/`.

## B. `en/` and `ko/` folders with shared course data

```
<course>notes.sty   figures.tex
course.tex          course data for the English edition (\coursename, \term, \lecturer …)
course-ko.tex       the same for the Korean edition
en/<course>_notes.tex   ko/<course>_notes.tex
build.sh   publish.sh   lectures.py   docs/   pdf/{en,ko}/   build/{en,ko}/
```

- The editions `\input{../course}` and `\input{../figures}`.
- Course fields are edited once per language.
- The README records the source authority order, the conventions table
  (signature, units, index placement) and any reconstructed lectures.

## C. `src/` with guarded parts

```
src/<course>_notes.tex   src/<course>_notes_ko.tex   src/<course>book.sty
src/parts/en/part1.tex … part4.tex     src/parts/ko/part1.tex …
src/build.sh   src/publish.sh
index.html   manifest.json   <course>_notes.pdf   <course>_notes_ko.pdf
```

- Each part is `\IfFileExists{parts/en/part3a.tex}{\input{parts/en/part3a}}{}`,
  so the document builds while later parts are still being written.
- GitHub Pages serves the repository root, so the PDFs, `index.html` and
  `manifest.json` live there; the build writes the PDFs one level up from
  `src/` and deletes the aux files.
- Used for long companion notes to a textbook, written in a few big pushes.

## D. Assembled from parts by a script

```
parts/assemble.py
parts/en/<code>.tex   parts/ko/<code>.tex      one file per part, the SOURCES
parts/figs/<code>.tex                           that part's figures
parts/words/<code>-en.tex  <code>-ko.tex        that part's figure words
en/<course>_notes.tex   ko/<course>_notes.tex  generated, never edited
figures.tex   figwords-en.tex   figwords-ko.tex generated
```

- `assemble.py` holds the front matter, the masthead date and a `CHAPTERS`
  list: each chapter has its number (as the slides number it), title in both
  languages, and the ordered codes of its parts with the section ranges they
  cover.
- It copies part bodies verbatim, skips parts not written yet, and checks the
  two things that only go wrong once parts share a document: a macro, length,
  counter or style defined by two parts (the later one silently changes the
  earlier part's figures), and a figure reaching outside its part
  (`\input`, `\includegraphics`, `table {file}`). `--check` runs only the
  checks.
- Several agents or sessions can write different parts at once without
  touching the same file.
- Used for courses taught from slide decks, where the slides' chapter
  numbers are kept (they can skip: 1, 2, 3, 5) and there are no lecture-date
  breaks; a table in the front matter maps slide files to sections.

## Choosing

| Situation | Layout |
|---|---|
| A normal course, lecture by lecture | A |
| You want course fields separate, or a third language later | B |
| Long notes written in a few large pushes, parts may lag | C |
| Taught from slide chapters, several writers in parallel | D |

## Common to all

- `.gitignore` the build droppings and `sources/` (course material).
- A README with: how to build, how to add a lecture (the house rules), the
  per-course options, the source authority order, reconstructed lectures, and
  a coverage table (Korean courses kept it in Korean).
- `docs/` (or the root) holds only what the site serves: `index.html`,
  `manifest.json`, the PDFs, `.nojekyll`.
