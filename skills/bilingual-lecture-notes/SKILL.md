---
name: bilingual-lecture-notes
description: Write and grow a term's lecture notes as one topic-ordered XeLaTeX document in English and Korean editions with identical numbering, from handouts, slides, handwriting and recordings, then build and publish them.
---

# Bilingual lecture notes

A student hands over a course's material lecture by lecture: the instructor's
handwritten iPad handouts, slide decks, posted notes, their own handwriting,
class recordings, board photos. The notes turn all of it into **one continuous
document per language**, ordered by topic rather than by date, that grows
through the term. Both editions carry the same parts, sections, equations,
figures and labels, so a reader (and the web viewer from `pdf-notes-viewer`)
can switch language and stay at the same place.

This skill was distilled from one term of nine courses written this way:
physics courses taught from iPad handouts or on the board, engineering courses
taught from slides (one of them in two sections with different instructors),
and a lab course. Their differences are kept as options; the defaults are what
worked best.

## When to use

- The student says "강의노트 업데이트해", "add lecture 7", "8-1 반영해", or
  uploads a handout or a recording without further words.
- A new course starts and needs notes, a repository and a site.
- Existing notes need restructuring: new parts, a moved section, a second
  edition, a renumbering problem, Korean particles, a figure redrawn.

Not for the site itself (`pdf-notes-viewer`), the page that lists every course
(`course-notes-hub`), problem books, answer keys and cheat sheets
(`exam-prep-materials`), or getting files to and from the student's Mac
(`student-mac-and-recordings`).

## What you get

- `notes-en.tex` and `notes-ko.tex` built to `Notes-EN.pdf` and `Notes-KO.pdf`
  (any names; the manifest records them), with a masthead, course information,
  the arc of the course, how the notes are organised, a lecture log, a table of
  contents, then parts and sections.
- Identical `\label`s, numbers and numbered PDF bookmarks in both editions,
  checked by `tools/labelcheck.py`.
- `docs/` with the PDFs and `manifest.json` for the viewer, committed and pushed
  by `publish.sh`.
- A short report to the student: what was added, figure and page counts, site
  status, and the list of corrections made to the source material.

The working skeleton is `assets/course-template/` (style, both editions with
sample content, one figure, build and publish scripts, checks). It builds as it
is; copy it and replace the sample content.

## Steps: adding a lecture

1. **Find what is new.** Read the last rows of the lecture log and the last
   `\lecturebreak`, then list the course folder or the uploads and pick the
   material that is not in the notes yet. A terse request ("업데이트해") means
   exactly this: the newest material that is not covered. If two files could
   be "the next lecture", say which one you took.
   See [materials-and-intake.md](references/materials-and-intake.md).
2. **Read it properly.** Render handwritten pages to images and read the
   images; the text layer of a handwriting PDF is junk OCR. Pull slide text
   with `pdftotext -layout` but render any page with a diagram. Get a
   transcript of the recording when the handouts are thin or when something is
   ambiguous. Read the whole lecture before writing anything.
3. **Place it by topic.** New material goes into the part whose topic it
   belongs to, as new sections (or into an existing section when it extends
   it). Open a new part with `\partdivider` only when a genuinely new topic
   starts. Never restart or change published section numbers.
4. **Mark where the lecture began.** `\lecturebreak[YYYY-MM-DD]{Lecture N}`
   (Korean `{제N강}`) at the first new material, then
   `\sourcenote{…}` saying what this lecture's notes rest on, and one new row in
   the lecture log of each edition.
5. **Write both editions in the same pass.** Write a section in one language,
   then the same section in the other, before moving on. Same environments,
   same labels, same equation order. See
   [document-structure.md](references/document-structure.md) and
   [korean-edition.md](references/korean-edition.md).
6. **Draw figures** as TikZ macros in the shared `figures.tex`, greyscale,
   with every word supplied by a `\lbl…` macro from each preamble. Compute
   plotted curves from the formula in the caption. See
   [figures.md](references/figures.md).
7. **Build and check.** `./build.sh` (both editions, three passes, then
   `labelcheck.py`), `python3 tools/ko-particles-check.py notes-ko.tex
   build/notes-ko.aux`, `python3 tools/lectures.py`. Fix every warning about
   undefined references, label mismatches and particles.
8. **Look at the pages.** Render the new pages
   (`pdftoppm -r 80 -f A -l B -png build/notes-en.pdf /tmp/p`) and look at
   each one: overfull lines, figures colliding with text, a part divider at the
   foot of a page, boxes split badly. Do the same for the Korean edition.
9. **Publish.** `./publish.sh` copies the PDFs into `docs/`, writes
   `docs/manifest.json`, commits and pushes. Confirm the GitHub Pages deploy
   through the repository's Actions run "pages build and deployment" rather
   than by fetching the site. See
   [build-and-publish.md](references/build-and-publish.md).
10. **Deliver copies** where the student reads them (their Mac course folder,
    a shared project folder), then **report**. See
    [reporting.md](references/reporting.md).

## Steps: a new course

1. Copy `assets/course-template/` into a new **private** repository (course
   material is the instructor's; the notes quote and paraphrase it).
2. Choose the layout from [repo-layouts.md](references/repo-layouts.md): a
   single file per edition is right until an edition passes about 3,000 lines
   or the course is organised by slide chapters.
3. Fill in the course fields, the course information, and the arc of the
   course from evidence only (the syllabus, the instructor's announcements).
4. Decide the per-course options with the student or from their earlier
   courses (below), and write them at the top of both editions and in the
   repository README.
5. Add the site: `docs/index.html` from `pdf-notes-viewer`, Pages from
   `main` / `docs`, then a row on the hub (`course-notes-hub`).
6. Write the first lecture as in "adding a lecture".

## Rules

- **Topic order, not date order.** Lectures are woven into parts by topic;
  `\lecturebreak` hairlines and the lecture log keep the chronology visible.
- **Numbers are permanent.** Sections number straight through all parts and
  are never renumbered once published: the viewer, cross-references and the
  student's own annotations depend on them. Parts are unnumbered in the
  bookmarks (`\partdivider` puts them one level above sections without a
  number), because the viewer treats every numbered bookmark as a place to
  match across languages.
- **The two editions are one document in two languages.** Same parts, sections,
  subsections, equations, figures, tables, theorem-like environments and
  labels, in the same order. A section exists in both or in neither.
- **Never run ahead of the class.** Posted notes and slide decks often contain
  material the lecture did not reach; the notes stop where the class stopped.
  Text written before a class (only when asked) sits under
  `\lecturebreak[date]{Planned}` / `{예정}`, stays out of the lecture log and
  is checked against the class afterwards.
- **Sources have an order of authority**: what was taught in class (the
  handwriting from class, then the recording) over the instructor's posted
  notes, over textbooks, which only verify. See
  [materials-and-intake.md](references/materials-and-intake.md).
- **The notes stand on their own.** No "the professor said", no "see handout
  p. 3", no quoted handwriting. State the physics (or the engineering) as
  settled text, with derivations complete enough to follow without the
  handout.
- **Errors in the source material are fixed, never copied.** By default the
  notes give the correct statement silently and the report lists every
  correction (where, what the source had, what the notes say, why). A course
  may choose a visible `review` box (Check / 검토) for a lecture argument that
  does not survive checking; agree on it once per course.
- **Additions are marked.** A step, check or example the class did not give
  goes in `\scribe{…}` (small type, ▸ in the margin), so the student can tell
  what is lecture material.
- **Do not repeat; refer.** Material already in the notes is cited with
  `\ref`/`\eqref`, not written again.
- **Figures are greyscale and language-neutral** and live in one shared file.
- **Leave the site's `docs/index.html` alone** during note updates. Change the
  viewer only when the student asks for a viewer change.
- **Course material never goes into a public repository.** `sources/` is
  ignored by git; handouts stay in the course folder.

## Configuration (per course)

| Option | Default | Alternatives seen |
|---|---|---|
| Division of the notes | topic parts via `\partdivider` | slide chapters as parts with the slides' own numbers (courses taught from slide decks) |
| Chronology markers | `\lecturebreak[date]{Lecture N}` + lecture log | `\deckbreak{Deck N}` where a slide deck first appears; none, with a slide-file table in the front matter |
| Grouping | one break per lecture | one break and one log row for a block ("Lectures 7–10") |
| Errors in sources | fixed silently, listed in the report | visible `review` box (Check / 검토); corrected with a remark in the repository README |
| Reading boxes | off | `why` to open a section, `glance` to close it, `procedure`, `pitfall` (a course that wanted short, exam-oriented notes of about 110 pages) |
| Korean terminology | Korean terms with the English at first use | class terms kept in English (state, pole, eigenvalue) with Korean prose |
| Missing lecture | reconstruct from neighbouring sources, say so in the README | fill from the instructor's notes from an earlier year taught in the same order |

## Self-check before reporting

- [ ] `./build.sh` ran clean: no undefined references, no `??` in either PDF,
      `labelcheck: ok`.
- [ ] Section, equation and figure numbers are the same in both editions, and
      no published number moved.
- [ ] The lecture log has the new row in both editions and `tools/lectures.py`
      prints the new count and date.
- [ ] `ko-particles-check.py` reports nothing except copula 이다/이며 after a
      vowel, which is correct.
- [ ] You looked at every new page of both PDFs as images.
- [ ] Nothing past the point the class reached; planned text is marked.
- [ ] The publish commit pushed, the Pages run succeeded, the manifest version
      changed.
- [ ] The report lists the corrections made to the source material.

## References

- [materials-and-intake.md](references/materials-and-intake.md): how the
  student supplied material, every kind of file and how to read it, the order
  of authority, gaps and reconstruction.
- [document-structure.md](references/document-structure.md): front matter,
  parts, sections, lecture breaks, source notes, scribe notes, environments,
  cross-references.
- [latex-style.md](references/latex-style.md): what `coursenotes.sty` does
  and why (fonts, bookmarks, headings, boxes, dates).
- [figures.md](references/figures.md): the shared figure file, word macros,
  greyscale, computed curves, simulation snapshots.
- [korean-edition.md](references/korean-edition.md): particles after numbers,
  terminology, dates, typography.
- [repo-layouts.md](references/repo-layouts.md): single file, `en/` + `ko/`,
  `src/parts`, assembled parts.
- [build-and-publish.md](references/build-and-publish.md): container setup,
  build, checks, manifest, publish, deploy check.
- [reporting.md](references/reporting.md): the report after an update.
