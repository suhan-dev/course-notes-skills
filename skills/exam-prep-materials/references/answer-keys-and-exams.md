# Answer sheets, past-exam keys, mock exams

## Homework answer sheets

The student hands these in (or copies from them), so they are written to be
graded.

- **English**, typeset with the notes' style
  (`\usepackage[english]{<course>notes}`), named `PS<n>-solutions.tex/.pdf`
  next to the problem set in `HW<n>/`. Build with the notes' folder on the
  search path: `TEXINPUTS=../notes: latexmk -xelatex PS1-solutions.tex`.
- **Working only.** No conventions table, no "[Notes §3]" citations, no side
  remarks, no restating whole problems. Brief explanations between steps are
  fine.
- **Nothing a grader could mark down is left implicit**:
  - state assumptions (quasi-static, the process is reversible, η ≠ 0, the
    steps are independent);
  - derive any formula used that the course did not hand out ready-made (an
    entropy change, a conservation law in a throttling process);
  - use every condition the problem gives (if it states the third law, it is
    needed somewhere);
  - add a one-line check where an answer could look suspicious (a sign, a
    limit, a known special case, units).
- Notation follows the notes; when the problem set uses another (ε for
  efficiency, T1/T2 for hot/cold), say once which one the answer uses.
- Copy the PDF next to the problem set on the student's Mac and to the shared
  folder.

## Keys for past exams and problem sets

Past material usually arrives as a zip of scans (GoodNotes exports) holding
the problem sheets, sometimes the instructor's handwritten official solutions,
sometimes other students' answers.

1. Unzip with the names re-decoded (see the intake notes in
   `bilingual-lecture-notes`), render every page, and list what is there:
   which exam, which year, which pages are problems, official solutions,
   students' answers. Duplicated pages are common.
2. Solve every problem yourself; then compare with the official solution where
   it exists. Where they differ, find out who is right and say so.
3. Typeset an English key per exam (`2020-midterm-solutions.tex`), in the
   notes' style, with the problem statements transcribed.
4. Record in a README which exam is where and what was checked.
5. These keys reproduce the instructor's exams: they stay private.

### Exam photos after an exam

The student may photograph the paper they just sat. Typeset the problem sheet
from the photos with the exact wording (`2026-midterm.tex`), then a key with
every result verified by script. Figures in the paper are redrawn from
coordinates read off the photo. Add a short difficulty note: which parts were
standard derivations from the notes and which were new moves; it calibrates
everything that follows (`exam-level.md`).

## Mock exams

- **Mirror the instructor's format**: the number of problems, points, time,
  the kind of first problem (for example four short "logical connection"
  parts: prove B from A), multi-part problems after it.
- **One set = one exam**: problem sheet and an English key, both PDFs. Ten
  sets were made for one midterm; a combined "all problems" and "all
  solutions" PDF is handy.
- **A README with a topic table per set**, so later sets do not repeat
  topics.
- **Level**: at least that of the latest real exam (`exam-level.md`). Mock
  sets that matched the easy 70% of an exam but never trained its hard parts
  left the student unprepared for exactly those parts.
- Keys follow the explaining rules (set-up first, every derivative with what
  is held fixed, both orders for extrema).

## A practice exam in a hurry

Before an exam the student may ask for "one page of everything about X" or "a
practice exam for tomorrow". Use what exists (problem book, keys, cheat sheet)
and extend it rather than starting over; deliver a PDF, not a long chat
message.
