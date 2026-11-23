# Start here: a term with these skills

This is the order in which one student's term went, and the order to follow
for a new one. Each step names the skill that holds the detail.

## 1. Ask once, at the start of the term

One message, in the student's language. Everything else is found out from the
material.

1. **The courses**: name in Korean and English, course number if it should
   appear, section ("B반") when one course has two sections.
2. **Where the material is**: the term folder on the Mac
   (`~/Desktop/<term>/<course>/` was the convention), which Mac is usually
   online, or "I'll upload it in chat".
3. **What each course runs on**: iPad handouts, slides, the board (then the
   student's handwriting and recordings), typed notes posted by the
   instructor, a lab manual.
4. **Editions**: English and Korean (the default), or one of them.
5. **Publishing**: the GitHub account; one private repository and one Pages
   site per course; a hub page listing them.
6. **Dates**: exams and homework deadlines (they set the priorities).

Write the answers into the project's memory (or the notes repository's
README) at once, so no later session asks again.

## 2. Set up each course

1. Notes repository from the course template, private
   (`bilingual-lecture-notes` → "Steps: a new course"; container set-up with
   `tools/setup-container.sh`).
2. The site: `docs/index.html` from `pdf-notes-viewer`, its settings block
   filled in (a storage-key prefix unique to the course), Pages from
   `main` / `docs`, the first publish, the viewer test.
3. A row on the hub (`course-notes-hub`), with its thumbnail.
4. The Mac: the course folder found and granted, the notes repository cloned
   into `<course>/notes/` (`student-mac-and-recordings`).

## 3. Every lecture

The request is short: "강의노트 업데이트해", "8-1 반영해", or a file with no
words.

1. Find what is new: handouts or handwriting in the folder or the uploads that
   the lecture log does not have yet; a recording if there is one
   (`student-mac-and-recordings` → recordings).
2. Write the lecture into both editions (`bilingual-lecture-notes` → "Steps:
   adding a lecture"): topic order, never ahead of the class, figures,
   corrections to the source kept for the report.
3. Build, check labels and Korean particles, publish (`publish.sh -m "notes:
   Lecture N — …"`).
4. Sync the Mac's clone with a bundle; put any other rebuilt PDF in its folder.
5. Report (`bilingual-lecture-notes/references/reporting.md`).

## 4. Homework

A problem set arrives as a PDF → an English answer sheet next to it, working
only, nothing a grader could mark down left implicit
(`exam-prep-materials` → answer sheets). Copy it to the Mac.

## 5. Before an exam

1. Calibrate to the latest real exam, not the easiest past one
   (`exam-prep-materials/references/exam-level.md`).
2. Keys for the past exams in the zip from seniors; mock exams in the
   instructor's format; a problem book on the site with covered solutions;
   a cheat sheet in both languages; derivation summaries for the areas the
   student names (`exam-prep-materials`).
3. Questions while studying are answered in chat by the explaining rules,
   with math rendered (`exam-prep-materials/references/explaining.md`).

## 6. After an exam

Photos of the paper → the problem sheet typeset with its exact wording, a key
with every result checked by script, and a note on which parts were standard
and which were new moves. It recalibrates everything after it.

## Requests and the skill that answers them

| The student writes | Skill | Notes |
|---|---|---|
| 강의노트 업데이트해 / 오늘 수업 반영 / N-M 반영해 | `bilingual-lecture-notes` | every lecture with material and no log row |
| (a file, no words) | depends on the file | identify it, do the obvious thing, say what you took it for |
| 녹음 있어 + link | `student-mac-and-recordings` | transcript, then check the lecture against it |
| 미리 써 줘 | `bilingual-lecture-notes` | planned text, marked as such |
| 뷰어가 …해 / 사이트에서 … | `pdf-notes-viewer` | change, then the viewer test on every course site |
| 허브에 … 추가 | `course-notes-hub` | row, thumbnail, live line |
| 과제 답지 | `exam-prep-materials` | English, working only |
| 기출 답지 / 모의고사 / 문제집 / 치팅시트 / 유도 총정리 | `exam-prep-materials` | at the latest exam's level |
| 이거 왜? / 뭔 뜻? | `exam-prep-materials` → explaining | literal answer first, then the full derivation |
| 맥에 없는데 | `student-mac-and-recordings` | deliver now, and after every rebuild from then on |

## The environment this came from

The agent worked in a cloud container with git access to the student's
repositories, a project folder shared by all sessions of the project, a
project memory, tools to reach folders on the student's Mac (read, write, a
shell without network or deleting), and Remote Control sessions on the Mac
for anything that needed the Mac's own network or tools. The skills say where
they depend on one of these; with other tools, the same steps apply.
