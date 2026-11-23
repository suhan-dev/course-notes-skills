# Build and publish

## Container setup (once per machine)

```sh
bash tools/setup-container.sh
```

installs TeX Live with XeLaTeX, Korean (`texlive-lang-korean`), TikZ and
pgfplots, `latexmk`, the Nanum fonts (and renamed copies under the macOS family
names), poppler (`pdfinfo`, `pdftoppm`, `pdftotext`), ghostscript and
fontTools. A few minutes. On macOS: MacTeX plus the Nanum fonts.

## Build

```sh
./build.sh          # both editions
./build.sh en       # one edition
```

- `latexmk -xelatex -outdir=build`: as many passes as the table of contents and
  `\pageref`s need (usually three).
- Afterwards `tools/labelcheck.py build/notes-en build/notes-ko` compares the
  labels and numbers in the two `.aux` files and the numbered PDF bookmarks.
  A failure means the editions have drifted: fix it before publishing.
- Then, by hand:
  ```sh
  python3 tools/ko-particles-check.py notes-ko.tex build/notes-ko.aux
  python3 tools/lectures.py              # {"count":N,"last":"YYYY-MM-DD"}
  grep -n -E "undefined|Overfull .{0,8}[0-9]{2,}" build/notes-*.log | head
  ```
- Look at the new pages as images, in both editions.

Build time is a few seconds per 10 pages; long notes (100+ pages with many
TikZ figures) take minutes. Never run XeLaTeX in the source folder: aux files
there go stale and get committed by accident.

## The manifest

`docs/manifest.json`, read by the viewer and the hub:

```json
{
  "version": "1795442102",
  "updated": "2027-09-06 21:40 KST",
  "pages": {"en": 4, "ko": 5},
  "lectures": {"count": 2, "last": "2027-09-06"},
  "docs": {"problems": {"pages": {"en": 86, "ko": 87}}}
}
```

| Key | Meaning |
|---|---|
| `version` | Unix time of the publish. The viewer appends `?v=<version>` to the PDF URLs, so a new publish is never hidden by a cache. |
| `updated` | shown in the viewer header and on the hub |
| `pages` | page counts of the notes, per edition |
| `lectures` | optional; the hub shows "Lecture N · date". From `tools/lectures.py`. Omitted when no dated lecture exists. |
| `docs.<id>.pages` | optional; page counts of additional documents shown as tabs (a problem book) |

One course used `"prob": {"pages": …, "sol": {"en": [[start, end], …]}}` for a
problem book with solution page ranges; the current viewer finds solutions
from named destinations instead and needs only `docs.<id>.pages`.

## Publish

```sh
./publish.sh                                  # pull, build, docs/, manifest, commit, push
./publish.sh --no-build                       # PDFs already built
./publish.sh --no-push                        # everything but the push
./publish.sh -m "notes: Lecture 7 — <topic>"  # the commit message (default: "notes: rebuild (<KST time>)")
```

1. `git pull --rebase --autostash`, so a commit made elsewhere (another
   session, the student's Mac) is not overwritten.
2. Build (unless `--no-build`).
3. Copy the PDFs to the repository root and to `docs/`; keep `docs/.nojekyll`.
4. Write `docs/manifest.json` (page counts from `pdfinfo`, lectures from
   `tools/lectures.py`, problem-book pages if those PDFs exist).
5. One commit: sources, PDFs and `docs/` together, message
   `notes: Lecture N — <topic>` (or the course's usual form), passed with
   `-m`.
6. Push; on rejection fetch, rebase and push once more. **Never force-push**:
   the rejected commits may be the student's own.

If the work happens on a branch, push the branch too, but the site is served
from `main`.

## GitHub Pages and checking a deploy

- Pages serves `main` / `docs` (or the root, layout C). Settings → Pages,
  "Deploy from a branch".
- A private repository can still serve a Pages site on plans that allow it;
  the site is reachable by anyone with the link and is not indexed if nothing
  links to it. Do not put a site's URL anywhere public if the notes should stay
  private.
- Many agent sandboxes cannot reach `*.github.io`. Check the deploy through
  the repository's Actions run "pages build and deployment" (status
  `completed`, conclusion `success`, head SHA = the publish commit) instead of
  fetching the site.
- The viewer fetches `manifest.json` with `cache: 'no-store'`; after a
  successful run the student sees the new PDFs on the next load.

## Copies

After a publish, put the PDFs where the student reads them: the course folder
on their Mac (`notes/` is a clone; see `student-mac-and-recordings` for moving
a commit there), and any shared project folder. Say in the report that you
did.
