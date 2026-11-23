# Testing the viewer

## The automated test

```sh
# once: a local copy of pdf.js, if the sandbox blocks cdnjs / jsdelivr
npm pack pdfjs-dist@3.11.174 && tar xzf pdfjs-dist-3.11.174.tgz

PDFJS_DIR=$PWD/package node assets/test/viewer-test.js <course>/docs --shots /tmp/viewer-shots
```

It serves the folder on 127.0.0.1, answers every pdf.js CDN request from
`PDFJS_DIR` (omit it when the CDNs are reachable), and checks, using only
`manifest.json` and what the page shows:

| Area | Checks |
|---|---|
| first load | English edition first, page count from the manifest, page indicator, update time, PDF URL carries `?v=<version>` |
| contents | button usable, rows from the bookmarks, focus moves in, Tab trapped, Escape closes, a row jumps to its section |
| language | the section marked in the contents is the same after EN → KO and after KO → EN; `<html lang>` follows; Korean button locked when there is no Korean edition |
| deep link | `#page=3` opens page 3 |
| resize | 1280 → 700 → 1280px keeps page and fraction within 3% |
| tabs | tabs appear for two or more documents, a click routes to `?doc=<id>`, Back returns |
| solutions | veils exist, a tap reveals that solution, it stays revealed after reload, reveal-all and cover-all |
| phone 375×667 | no horizontal scroll, contents opens as a bottom sheet |
| always | no console errors |

It needs `node` and `playwright` with a Chromium it can launch. Exit code 0
means every check passed. With `--shots`, it saves screenshots of the first
load, the open contents, the problem book and the phone sheet: look at them.

To test before publishing, build the PDFs and run the publish script with
`--no-push` so that `docs/` holds the new PDFs and manifest.

## Manual checks worth doing after a viewer change

- Safari on iOS/iPadOS: rotate while reading (resize hold), switch apps and
  come back (place saved on `visibilitychange`), the bottom sheet.
- Dark mode: bar and drawer dark, paper and veils white.
- A slow connection (DevTools throttling): placeholders, then pages near the
  viewport first; clicking languages quickly ends on the last one clicked.
- An in-app browser (a messaging app's link preview): pages draw.
- Keyboard only: open contents, arrows, Enter, Escape.

## Checking a deploy

Sandboxes usually cannot fetch `*.github.io`. After pushing, check the
repository's Actions run named "pages build and deployment": `completed` /
`success`, with the head SHA of the publish commit. The site serves the new
files within a minute after that; the manifest is fetched with
`cache: 'no-store'` and the PDFs carry the new version, so no cache hides
them.

## Screenshots for the student

Take them at `deviceScaleFactor: 2` when the student will see them (1 for
your own checks), at 1280×800 and 390×844, in the language the student reads.
