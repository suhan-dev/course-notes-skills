# Course-notes template

A working skeleton for one course: the shared style, both editions with sample
content, one language-neutral figure, the build and publish scripts and the
checks. Copy the whole folder into a new repository, then replace the sample
content. Everything here builds as it is (`./build.sh`) on a machine with
XeLaTeX, Korean support and the Nanum fonts (`bash tools/setup-container.sh`
prepares a Debian/Ubuntu container).

| File | What it is |
|---|---|
| `coursenotes.sty` | Masthead, environments, `\partdivider`, `\lecturebreak`, `\sourcenote`, `\scribe`, reading boxes, notation, bilingual words (`[korean]` option) |
| `notes-en.tex`, `notes-ko.tex` | The two editions: front matter (course information, arc of the course, how the notes are organised, lecture log, contents), then parts and sections |
| `figures.tex` | Every figure as a `\fig<Name>` macro; words come from `\lbl...` macros defined in each edition's preamble |
| `build.sh` | `./build.sh` builds the notes (both editions, then `tools/labelcheck.py`) and, when `problems-en.tex` / `problems-ko.tex` exist, the problem book (then `tools/probcheck.py`); `./build.sh en`, `ko`, `notes` or `problems` builds one part |
| `publish.sh` | pull → build → `docs/` → `docs/manifest.json` → commit → push (rebase and retry, never force); `--no-build`, `--no-push`, `-m "<commit message>"` |
| `tools/lectures.py` | Reads the last dated lecture break → `{"count":N,"last":"YYYY-MM-DD"}` for the manifest and the hub |
| `tools/labelcheck.py` | The editions must have the same labels, numbers and numbered bookmarks |
| `tools/ko-particles-check.py` | Korean particles after `\eqref`/`\ref` must match the spoken number |
| `tools/setup-container.sh` | TeX Live, Nanum fonts (also under the macOS family names), poppler, ghostscript |

The site itself (`docs/index.html`, the PDF viewer) comes from the
`pdf-notes-viewer` skill. The problem book that `build.sh` builds and
`publish.sh` publishes when its sources exist comes from
`exam-prep-materials` (`assets/problem-book/`: copy `problems-en.tex`,
`problems-ko.tex`, `problems/` and `tools/probcheck.py` into the course
folder).
