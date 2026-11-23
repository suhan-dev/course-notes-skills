#!/usr/bin/env bash
# Build the lecture notes (both editions) with XeLaTeX through latexmk.
#
#   ./build.sh            notes (both editions), then the problem book if present
#   ./build.sh en         English notes only
#   ./build.sh ko         Korean notes only
#   ./build.sh notes      notes, both editions
#   ./build.sh problems   problem book only (problems-en.tex / problems-ko.tex,
#                         from the exam-prep-materials skill)
#
# Everything is XeLaTeX: the Korean edition has to be (xetexko), and keeping
# the English one on pdflatex would set the two editions in different fonts.
# latexmk reruns until cross-references and the table of contents settle
# (three passes on a clean build) and skips a document whose sources did not
# change.  TeX droppings stay in build/; the finished PDFs are copied to the
# repository root under the names the site publishes.
set -euo pipefail
cd "$(dirname "$0")"

# The published file names.  publish.sh and the DOCS list in docs/index.html
# use the same names.
PDF_EN="Notes-EN.pdf"
PDF_KO="Notes-KO.pdf"
PROB_EN="Problems-EN.pdf"
PROB_KO="Problems-KO.pdf"

build_one() {   # <source basename> <published name>
  latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build "$1.tex" >/dev/null 2>&1 \
    || { echo "!! $1.tex failed; first errors:" >&2
         grep -n -m 5 -A 3 '^!' "build/$1.log" >&2 || true; exit 1; }
  cp "build/$1.pdf" "$2"
  echo "  -> $2 ($(pdfinfo "$2" | awk '/^Pages:/{print $2}') pages)"
}

build_notes() {
  build_one notes-en "$PDF_EN"; build_one notes-ko "$PDF_KO"
  # the two editions must carry the same labels and numbered bookmarks
  python3 tools/labelcheck.py build/notes-en build/notes-ko
}
build_problems() {
  build_one problems-en "$PROB_EN"; build_one problems-ko "$PROB_KO"
  # same chapters and problems in both editions, every problem has a solution
  python3 tools/probcheck.py build/problems-en build/problems-ko >/dev/null \
    || { python3 tools/probcheck.py build/problems-en build/problems-ko; exit 1; }
}

case "${1:-all}" in
  en)       build_one notes-en "$PDF_EN" ;;
  ko)       build_one notes-ko "$PDF_KO" ;;
  notes)    build_notes ;;
  problems) build_problems ;;
  *)        build_notes
            if [[ -f problems-en.tex && -f problems-ko.tex ]]; then build_problems; fi ;;
esac
echo "done."
