#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Rebuild the PDFs and publish them to the GitHub Pages site (main:/docs).
#
#   ./publish.sh                       pull, build, docs/, manifest, commit, push
#   ./publish.sh -m "notes: Lecture 3 — diffusion"   the same, with this commit message
#   ./publish.sh --no-build            publish the PDFs that are already built
#   ./publish.sh --no-push             update docs/ only: no commit, no push
#
# The viewer (docs/index.html) reads docs/manifest.json on every load: the page
# counts tell it which documents and language buttons to unlock, and "version"
# is appended to every PDF URL so a new publish is never hidden by a cache.
# There is no version string inside index.html: this script writes the
# manifest on every publish.
#
#   {"version":"<unix time>","updated":"YYYY-MM-DD HH:MM KST",
#    "pages":{"en":N,"ko":M},                  <- the notes (first document)
#    "lectures":{"count":12,"last":"YYYY-MM-DD"},   <- optional, for the hub
#    "docs":{"problems":{"pages":{"en":N,"ko":M}}}} <- optional, more documents
#
# The keys are en/ko even when the files are named EN/KO: that is what the
# viewer reads.  Never force-push: other sessions push to this repository too.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"

PDF_EN="Notes-EN.pdf"           # must match build.sh and DOCS in docs/index.html
PDF_KO="Notes-KO.pdf"
PROB_EN="Problems-EN.pdf"       # optional second document (problem book)
PROB_KO="Problems-KO.pdf"

BUILD=1; PUSH=1
MSG="notes: rebuild ($(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M'))"
while (( $# )); do
  case "$1" in
    --no-build) BUILD=0 ;;
    --no-push)  PUSH=0 ;;
    -m) shift; MSG="${1:?-m needs a message}" ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

# Start from whatever is on the remote; --autostash carries local edits across.
if (( PUSH )); then
  git pull -q --rebase --autostash origin main \
    || { echo "pull failed: resolve the rebase, then rerun" >&2; exit 1; }
fi

if (( BUILD )); then ./build.sh; fi

for f in "$PDF_EN" "$PDF_KO"; do
  [[ -f "$f" ]] || { echo "missing $f: run ./build.sh first" >&2; exit 1; }
done

mkdir -p docs
cp "$PDF_EN" "$PDF_KO" docs/
touch docs/.nojekyll

pages() { pdfinfo "$1" | awk '/^Pages:/ { print $2; exit }'; }
EN_PAGES="$(pages "docs/$PDF_EN")"
KO_PAGES="$(pages "docs/$PDF_KO")"

# lectures.py prints {"count":N,"last":"YYYY-MM-DD"} or nothing (then the field
# is left out; a parsing problem never blocks a publish).
LEC="$(python3 tools/lectures.py || true)"
LEC_FIELD=""; [[ -n "$LEC" ]] && LEC_FIELD=",\"lectures\":$LEC"

DOCS_FIELD=""
if [[ -f "$PROB_EN" && -f "$PROB_KO" ]]; then
  cp "$PROB_EN" "$PROB_KO" docs/
  DOCS_FIELD=",\"docs\":{\"problems\":{\"pages\":{\"en\":$(pages "docs/$PROB_EN"),\"ko\":$(pages "docs/$PROB_KO")}}}"
fi

VERSION="$(date +%s)"
UPDATED="$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M') KST"
printf '{"version":"%s","updated":"%s","pages":{"en":%s,"ko":%s}%s%s}\n' \
  "$VERSION" "$UPDATED" "$EN_PAGES" "$KO_PAGES" "$LEC_FIELD" "$DOCS_FIELD" > docs/manifest.json
echo "manifest: $(cat docs/manifest.json)"

if (( ! PUSH )); then echo "docs/ updated (--no-push)"; exit 0; fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "no git remote: docs/ is up to date, nothing pushed."
  echo "  git remote add origin <repository URL> && git push -u origin main"
  echo "  then Settings > Pages > Source: main, folder /docs"
  exit 0
fi

git add -A
if git diff --cached --quiet; then
  echo "nothing changed."
  exit 0
fi
git commit -q -m "$MSG"
push_once() {
  git fetch -q origin
  git rebase -q origin/main || { echo "rebase conflict: resolve, git rebase --continue, git push" >&2; exit 1; }
  git push -q origin HEAD:main
}
push_once || { echo "push rejected: fetching again and retrying"; push_once; }
echo "pushed. The site updates within a minute (check the 'pages build and deployment' run)."
