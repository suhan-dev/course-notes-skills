# Security and privacy

This repository is public. It holds a method, never the material or the
people it was used with.

## Never committed

| What | Why |
|---|---|
| Course material: handouts, slides, the instructor's notes, textbooks (also as OCR text), lab manuals | It belongs to the instructors and publishers. |
| Recordings, captions, transcripts | Class material, and the voices of the instructor and students. |
| Exam papers, problem sets, official solutions, keys or mock exams that reproduce them | The instructor's; reusing them publicly harms later classes. |
| The student's handwriting and their real notes | Theirs, and derived from the class. |
| Names of the student, instructors, TAs, classmates | Personal data. |
| E-mail addresses, phone numbers, scores and grades | Personal data. |
| School, course codes, LMS names, YouTube channels, real site URLs and repository names | They identify the people above. |
| Device names, account names, home-directory paths | Personal data, and they map the student's machines. |
| Tokens, keys, passwords, cookies | Secrets. None are needed: GitHub Pages and the scripts here need no secret in the repository. |

Sample data replaces all of it (`CONTRIBUTING.md`).

## How it is checked

`bash tools/privacy-scan.sh` scans every tracked or new file for e-mail
addresses, mail and school domains, tokens and keys, macOS home paths,
`github.io` URLs that are not the `ACCOUNT` placeholder, YouTube links and
phone numbers, and for every pattern in `tools/private-patterns.txt`: the real
names, logins, course repositories and device names. That file is
git-ignored, so the names themselves are never published; copy
`tools/private-patterns.example.txt` to start one. Run the scan before every
push; it must print only ✓.

## Reporting

If you find personal data or course material in this repository, open an
issue without quoting it ("personal data in skills/x/y.md, line N"), and it
will be removed together with its history.
