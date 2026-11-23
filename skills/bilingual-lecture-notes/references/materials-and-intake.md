# Materials and intake: how the material arrives and how to read it

This is how one student supplied a term's worth of course material to an agent
that wrote their notes, and what each kind of file needs. Nothing here is
specific to one university; paths are shown with placeholders.

## 1. Where the material lives

### The course folder on the student's Mac

Each term has a folder on the Desktop, one subfolder per course:

```
~/Desktop/<term>/<course>/            e.g. ~/Desktop/26-2/<course name in Korean>/
├── 강의노트/          instructor handouts or posted notes (PDF), one per lecture
├── 필기원본/          the student's own handwriting from class (GoodNotes PDF exports)
├── 수업녹음/          class recordings (m4a) and captions/transcripts
├── HW1/ HW2/ …        problem sets (PS1.pdf …) and the answer sheets made for them
├── <past years>.zip   past problem sets and exams collected from seniors
├── 기출/ 모의고사/     exams after they are taken; practice exams made for the student
└── notes/             a git clone of the notes repository
```

Not every course has every folder. Typical mixes:

| Course type | What arrived |
|---|---|
| Physics course taught on an iPad | instructor handwriting PDFs `<week>-<n>_<topic>.pdf` (4–12 pages each), one Keynote PDF for the first lecture, YouTube recordings by date, problem sets, a zip of past years |
| Theory course taught on a board | the student's handwriting (`필기MMDD.pdf`, sometimes cumulative), class recordings in `수업녹음/`, the instructor's posted typed notes (`<COURSE>-<Mon><DD>.pdf`), the textbook for checking |
| Engineering course from slides | slide decks per chapter (`ch01.pdf` …) or numbered decks (`강의자료N.pdf`), board photos, sometimes the instructor's notes from an earlier year |
| Lab course | the lab manual (a published book: never copied into the repository), weekly lab handouts, the student's lab notebook |

### Reaching the folder

- **Folder access on the device.** Ask once for the exact course folder (or
  the term folder when several courses are involved). Request the canonical
  path the device reports.
- **Korean folder names are NFD on macOS.** Typing a Korean name such as `강의노트` composed
  (NFC) does not match. In a shell on the device, `cd` by glob
  (`cd ~/mnt/*/` or `ls -d */ | …`) or normalise names with Python
  `unicodedata.normalize('NFD', …)`.
- **The laptop with the files may be offline.** The Desktop of that Mac syncs
  to iCloud Drive, so another Mac of the same account sees the same tree
  under `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/<term>/<course>/`.
  Request that path instead. iCloud may hold files as cloud-only placeholders:
  staging them downloads them, so warn before pulling many large files.
- **Writing back** (PDFs, answer sheets, the notes clone): see the
  `student-mac-and-recordings` skill. Git on the device cannot reach GitHub;
  move commits with a bundle.

### Uploads in chat

When away from the Mac the student uploads files directly in chat. In the
agent environment used here they land in a shared project folder as
`uploads/<id>` **with no extension and no original name**. For each upload:

```sh
file uploads/<id>            # PDF? zip? PNG? plain text?
pdfinfo uploads/<id>         # pages, producer (GoodNotes, Keynote, Notability, xdvipdfmx)
pdftotext -l 1 uploads/<id> - | head
```

then copy it under a real name into the course's working folder
(`<course>/handouts/8-1_<topic>.pdf`) so the next session can find it, and
note where it came from. Several handouts of one week often arrive in one
message.

### Links

- **YouTube recordings** (an unlisted course channel, videos titled by date,
  e.g. `1015`). The cloud container usually cannot reach YouTube. What
  worked: run `yt-dlp` on the student's Mac (a Remote Control session) to save
  the audio and the Korean auto captions into `수업녹음/`, then stage the
  caption file. Auto captions cleaned with the lecture context beat local
  Whisper. Details in `student-mac-and-recordings`.
- **The course LMS** (syllabus, announcements, deadlines): the student copies
  the relevant text into chat; the agent does not log in anywhere.

### Other forms seen

- **Exam papers after the exam**: phone photos (PNG) of each page. Typeset the
  problem sheet from the photo, then a key (see `exam-prep-materials`).
- **Past years**: a zip of GoodNotes exports (scanned exams, official
  solutions, other students' answers). Zip member names are often UTF-8 stored
  without the UTF-8 flag, so they appear as cp437 mojibake; re-decode them:
  ```python
  import zipfile
  for i in zipfile.ZipFile(path).infolist():
      name = i.filename if i.flag_bits & 0x800 else i.filename.encode('cp437').decode('utf-8')
  ```
- **A textbook as OCR'd plain text** (`<book>.pdf.txt`, ~1 MB). Prose is fine;
  equations, exponents, Greek letters and many numbers are garbled. Find a
  problem by its number at line start (`grep -n '^4.5-9\.'`), reconstruct
  garbled equations from context and the printed answer, and flag every
  reconstruction in the output.
- **Typed transcriptions** made by other students (LaTeX PDFs; text extracts
  cleanly). Treat as unofficial; check every result.

## 2. Reading each kind of file

| Kind | How to read it | Watch for |
|---|---|---|
| Instructor iPad handwriting | `pdftoppm -r 110 -png file.pdf /tmp/h` and read every page image; zoom (`-r 200`, crop) on dense pages | The text layer is junk OCR: never trust `pdftotext`. The **title on page 1** ("Lecture 7: …") names the lecture; the file name may not (a file named `6-2_…` can be self-titled "Lecture 7"). Byte-identical duplicates exist (`cmp`). |
| The student's handwriting | same as above | Files can be **cumulative**: a later export repeats all earlier pages; take the union once. A blank page means no notes that day, not a short lecture. |
| Slide decks (Keynote/PowerPoint PDFs) | `pdftotext -layout`; render pages with plots, block diagrams, tables | Decks cover more than one lecture and more than the class reached. Chapter numbers in the deck are the instructor's: courses taught from slides keep them. |
| Instructor's posted notes (typed) | `pdftotext -layout`, render equations you rely on | Often contain material the lecture did not reach, and occasional slips (a sign, a missing δ, units set to 1). Reference only, unless they are the only record of a class. |
| Board photos | view the image; straighten/crop if needed | Partial: a photo shows one board. Combine with the recording. |
| Recordings | transcript (auto captions, cleaned) | Use them to settle what was said, where the class stopped, and the order of topics. Times: note where class actually starts. |
| Problem sets | `pdftotext -layout` (ligatures fi/fl may drop out) | Notation may differ from the lectures (ε vs η, T1/T2 vs T_h/T_c); say which one the answer uses. Fractions can print upside down in `-layout`; check the rendered page. |

## 3. Order of authority

When sources disagree, or one has material the others lack:

1. **What was taught in class**: the handwriting from that class is the
   spine; the recording settles anything the handwriting leaves unclear.
2. **The instructor's posted notes** are reference only, except for a class
   that left no other record; then they are the primary source for that
   lecture, and the repository README says so.
3. **Textbooks verify** statements and conventions; they are never a source of
   content.

The material a course runs on decides what "the class" means: for a course
taught from iPad handouts, the handout **is** the class record; for a course
taught from slides, the slides plus board photos are.

## 4. Gaps, reconstruction and planned text

- **A missing lecture** (no handwriting, no recording): reconstruct it from
  where the neighbouring sources stop and start. Write down the evidence in the
  repository README: the last equation of the previous record, the opening of
  the next (e.g. a recap "we saw that…" spoken in the past tense), and what the
  posted notes contain between them. If a record turns up later, check the
  sections against it.
- **Board content missing this year**: some instructors teach the same course
  in the same order every year; the student may have their notes from an
  earlier year. Fill the gap from those, in the same order.
- **Never run ahead.** Stop where the class stopped, even if the posted notes
  continue. If the student asks for notes before a class ("미리 써 줘"),
  write them under `\lecturebreak[date]{Planned}` / `{예정}`, keep them out of
  the lecture log, and after the class compare and convert the break into
  `Lecture N` / `제N강` with a log row.
- **Dates**: the lecture date is the class date (from the recording title, the
  syllabus or the handwriting), not the PDF's creation date or the upload time.

## 5. What the requests look like

The student writes short messages and expects the agent to work out the rest:

| Request | Meaning |
|---|---|
| `강의노트 업데이트해` | Add every lecture whose material is in the folder or uploads but not in the notes, both editions, publish, report. |
| `8-1 반영해`, `오늘 수업 반영` | Add that lecture specifically. |
| (a file, no words) | Identify it (handout? exam photo? past year?) and do the obvious thing; say what you took it to be. |
| `녹음 있어` + a link | Get the transcript and use it to check or complete the lecture. |
| `미리 써 줘` | Planned text, marked as such. |
| `맥에 없는데` | Deliverables are expected in the Mac course folder too, after every rebuild. |

The student reads the notes on the site and on the Mac, studies from them for
exams, and notices when an edition lags, when a number moved, or when a Korean
particle is wrong.

## 6. What never goes public

Handouts, slides, posted notes, recordings, past exams, the textbook and the
student's handwriting are not the student's to publish. The notes repository
is private; the `sources/` folder is git-ignored; generated material that
reproduces exam problems stays in private repositories or project folders.
A public repository (like this skills repository) carries only the method.
