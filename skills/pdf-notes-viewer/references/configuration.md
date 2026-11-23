# Configuration

## The course-settings block ("과목 설정")

At the top of the script in `index.html`. Nothing below it knows which course
it serves.

```js
var DOCS = [
  { id:'notes', tab:'강의노트', title:'샘플 과목 강의노트',
    files:{ ko:'Notes-KO.pdf', en:'Notes-EN.pdf' } },
  { id:'problems', tab:'문제풀이', title:'샘플 과목 문제풀이', solutions:true,
    files:{ ko:'Problems-KO.pdf', en:'Problems-EN.pdf' } }
];
var DEFAULT_LANG = 'en';
var LS_LANG      = 'sample.lang';
var LS_POS       = 'sample.pos.';
var SS_SOL       = 'sample.sol.';
var MARK         = 'pb';
```

| Setting | Meaning |
|---|---|
| `DOCS[i].id` | document id; `?doc=<id>` in the URL, `docs.<id>` in the manifest. The first entry is the default document and reads its page counts from the manifest's top-level `pages`. |
| `DOCS[i].tab` | tab label (shown only with two or more documents) |
| `DOCS[i].title` | `document.title` while this document is open (with tabs) |
| `DOCS[i].files` | PDF file names per language, relative to `index.html` |
| `DOCS[i].solutions` | `true` for a problem book whose solution pages are covered |
| `DEFAULT_LANG` | edition for a first-time reader. If you change it, also change `LS_LANG` (for example `.lang2` → `.lang3`), or the old saved choice keeps winning for returning readers. |
| `LS_LANG` | `localStorage` key of the chosen language (shared by all documents) |
| `LS_POS` | prefix of the reading-place keys: `LS_POS + lang` for the first document, `LS_POS + id + '.' + lang` for the others |
| `SS_SOL` | `sessionStorage` prefix of the revealed solutions, per document |
| `MARK` | prefix of the problem book's named destinations (`pb.sol.1.2`) |

**Use a prefix unique to the course** for the three storage keys. Every Pages
site of one GitHub account is served from `<account>.github.io/<repo>/`, one
origin, so all of them share one `localStorage`; with equal keys, reading
place and language would leak from one course to another.

A course with one document has one `DOCS` entry: no tabs, and the bar looks
as it always did.

## The three HTML places

They must be right without JavaScript (browser tab title, link previews):

```html
<title>샘플 과목 강의노트</title>
<meta name="description" content="샘플 과목 (2027년 2학기) 학기 누적 강의노트">
<div id="title"><span class="long">샘플 과목 강의노트</span><span class="short">샘플 과목</span></div>
```

The long title shows on wide screens with a single document; the short one on
phones and whenever there are tabs.

## UI words

The interface is in Korean, for a Korean reader studying in both languages
(the edition buttons say English / 한국어). To translate it, change these
strings in place:

| Korean | Where | Meaning |
|---|---|---|
| 목차 | button, panel heading, aria labels | contents |
| 목차 닫기 | close button, backdrop | close contents |
| 언어 선택 | language group label | choose language |
| PDF 내려받기 | download link | download PDF |
| 불러오는 중… | CSS `content` on undrawn pages | loading… |
| 풀이 N, (이어짐), 눌러서 풀이 보기 | veils | solution N, (continued), tap to show |
| 풀이 모두 보기 / 풀이 모두 가리기 | contents header | show / cover all solutions |
| 한국어판 준비 중입니다 | tooltip on the locked Korean button | Korean edition in preparation |
| 아직 올라온 문서가 없습니다 | message | nothing published yet |
| … 불러오지 못했습니다 … | error messages | could not load … |

## The manifest contract

`manifest.json` next to `index.html`, written by the publish script:

```json
{
  "version": "1795443645",
  "updated": "2027-09-06 21:40 KST",
  "pages": {"en": 4, "ko": 5},
  "lectures": {"count": 2, "last": "2027-09-06"},
  "docs": {"problems": {"pages": {"en": 8, "ko": 8}}}
}
```

- `version` (string): appended to every PDF URL. Unix time of the publish.
- `updated`: shown in the bar as is. Keep the 20-character format
  `YYYY-MM-DD HH:MM KST` (the bar reserves exactly that width).
- `pages`: the first document's editions. A missing or `null` language means
  that edition is not published: its button is locked.
- `docs.<id>.pages`: the same for every further document. A document absent
  from the manifest gets no tab.
- `lectures`: not read by the viewer; the hub (`course-notes-hub`) shows it.

## File names

The names in `DOCS[i].files`, in `build.sh` and in `publish.sh` must be the
same. The course template uses `Notes-EN.pdf`, `Notes-KO.pdf`,
`Problems-EN.pdf`, `Problems-KO.pdf`; real courses used names like
`<Course>-Notes-EN.pdf` or `<course>_notes_ko.pdf`. The manifest keys are
always `en`/`ko`, whatever the files are called.

## Where the file lives

`docs/index.html` with `docs/.nojekyll`, Pages from `main` / `docs`; or the
repository root when Pages serves the root (a layout with sources under
`src/`). The PDFs and `manifest.json` sit next to it.

## Changing pdf.js

`PDFJS_VERSION` and the `<script src>` in the head name the version (now
3.11.174, the last 3.x line with a non-module `pdf.min.js` that works without
a bundler). Change both, keep the jsdelivr data URL in step, run the test.
