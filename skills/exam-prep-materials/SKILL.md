---
name: exam-prep-materials
description: Make a course's study and exam material from its notes and past papers - problem books with covered solutions, homework answer sheets, past-exam keys, mock exams, cheat sheets, derivation summaries, textbook problem collections - and explain answers in chat with rendered math.
---

# Exam-prep materials

Everything around the lecture notes that a student uses to prepare for
homework and exams. Each product has a fixed form that the student agreed to
once, and the forms below are those. All of them follow the notes' notation
and are pitched at the level of the course's hardest recent exam, not its
easiest past one.

## When to use

| The student says | Make |
|---|---|
| "풀만한 문제를 사이트에 탭으로", "문제와 답이 번갈아" | a **problem book** shown as a tab of the notes site, solutions covered |
| "과제 답지", a problem set PDF | an **answer sheet** for that set (English, working only) |
| a past-year zip, "기출 답지" | typed **keys** for the past exams and problem sets |
| "모의고사" | **mock exams** in the instructor's format, with keys |
| "치팅시트", "한 장 요약" | a **cheat sheet**, A4, columns packed to the edge |
| "유도 총정리", "○○ 관련 다 정리" | a **derivation summary** PDF |
| the textbook as text + "연습문제" | a **textbook problem collection** with full solutions |
| "이거 왜?", "뭔 뜻?" | an **explanation**, with math rendered |

## What you get (assets)

- `assets/problem-book/`: macros (`problems/common.tex`), both editions, two
  sample chapters, `tools/probcheck.py`. Builds next to the course style;
  `build.sh problems` in the course template runs it.
- `assets/tall-page-problems/`: the one-sheet-per-problem variant
  (`tallproblems.sty`, `crop.py`, a sample).
- `assets/answer-key/ps-solutions.tex`: an answer-sheet skeleton.
- `assets/cheatsheet/`: `content.py` (boxes), `build.py` (HTML, auto-packed
  columns), `pw.js` (PDF + fill/overflow/KaTeX report).
- `assets/katex-widget/`: `check.js` and `mkwidget.py` for math in chat.

## Steps: a problem book on the site

1. Agree on the **scope** (which sections; for example the final-exam range)
   and the **level** (see [exam-level.md](references/exam-level.md)).
2. Collect sources: past exams and problem sets (with the instructor's
   official solutions where they exist), the instructor's worked examples,
   earlier mock exams, plus new problems written to cover what the past ones
   miss. Every problem gets a source line ("Final 2021, 2", "New",
   "+ new parts").
3. Copy `assets/problem-book/` into the course repository. One chapter file
   per topic, per language (`problems/en/chN.tex`, `problems/ko/chN.tex`).
4. Write each problem with `\problem{title}{source}{notes sections}`, then
   `\solution` and `\solpart{a}{…}` parts. Solve everything yourself and
   check every number with a short script (sympy, numpy). Box the final
   answers with `\ans{…}`.
5. `./build.sh problems` (latexmk, then `probcheck.py`: same chapters and
   problems in both editions, every problem has a solution).
6. Add the document to the viewer's `DOCS` with `solutions:true`; the publish
   script adds `docs.problems.pages` to the manifest. Publish and test the
   tab. See [problem-book.md](references/problem-book.md).

## Steps: an answer sheet for a problem set

1. Read the problem set from the rendered page (fractions can come out upside
   down in `pdftotext -layout`), note its notation and due date.
2. Solve every part, checking each result numerically or symbolically.
3. Write it from `assets/answer-key/ps-solutions.tex`: English, the notes'
   notation, working only, but every gradeable step justified. Build next to
   the problem set (`TEXINPUTS=../notes:`).
4. Put the PDF and source next to the problem set (`HW<n>/PS<n>-solutions`)
   on the student's Mac and in the shared folder.
   See [answer-keys-and-exams.md](references/answer-keys-and-exams.md).

## Rules

- **Correct first.** Every number is checked by a second route (a script, a
  limit, units). Where a printed answer (textbook, official key) is wrong, say
  so and give the corrected value.
- **Complete derivations.** No "it can be shown"; every step of a derivation
  is written or one line of justification away. For any extremum claim check
  the first-order and the second-order condition.
- **State the set-up before the algebra**: the system and subsystems, what it
  touches (reservoirs), what is held fixed, what is varied, what is
  extremised.
- **Define every symbol** at first use; for every derivative say what is
  differentiated, with respect to what, holding what fixed.
- **The notes' notation**, and say so once when the source's differs.
- **Material outside the notes is tagged** ("[노트 밖]" / "outside the notes").
- **Same structure in both editions** wherever there are two.
- **Exam papers and keys stay private.** Past exams, official solutions and
  anything that reproduces them are the instructor's; they never go into a
  public repository.
- **Deliver where the student studies**: the site, the Mac course folder, the
  shared folder. After every rebuild, replace the copies.

## Self-check

- [ ] Every number checked by script; scripts kept next to the sources.
- [ ] `probcheck.py` OK (problem books), both editions built, pages looked at.
- [ ] Answer sheets: nothing but working, every gradeable step justified.
- [ ] Mock exams: format and level match the latest real exam; topics not
      repeated from earlier sets.
- [ ] Cheat sheets: every column under 100%, overflow 0, no KaTeX errors.
- [ ] Copies delivered and the report says where.

## References

- [problem-book.md](references/problem-book.md): layout, macros, the viewer
  link, sources, adding problems, the tall-page variant.
- [answer-keys-and-exams.md](references/answer-keys-and-exams.md): answer
  sheets, past-exam keys, typesetting exam photos, mock exams.
- [exam-level.md](references/exam-level.md): calibrating to the latest exam;
  the three "differentiator" moves to train.
- [cheat-sheets-and-summaries.md](references/cheat-sheets-and-summaries.md):
  cheat sheets (HTML → PDF, packing), derivation summaries, both editions.
- [textbook-problems.md](references/textbook-problems.md): working from an
  OCR'd textbook; selection, reconstruction, verification.
- [explaining.md](references/explaining.md): how to answer study questions,
  and math in chat.
