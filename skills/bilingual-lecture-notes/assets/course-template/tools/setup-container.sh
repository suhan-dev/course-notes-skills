#!/usr/bin/env bash
# Prepare a Debian/Ubuntu container (a cloud session) to build the notes.
#
#   bash tools/setup-container.sh
#
# 1. TeX Live with XeLaTeX, Korean (xetexko), TikZ/pgfplots and latexmk;
#    poppler-utils for pdfinfo/pdftoppm/pdftotext; ghostscript for crop.py.
# 2. The Nanum fonts, also registered under the macOS family names.
#    Debian's fonts-nanum calls the families "NanumMyeongjo" / "NanumGothic";
#    macOS calls them "Nanum Myeongjo" / "Nanum Gothic".  coursenotes.sty
#    accepts either, but older style files ask for the macOS names only, so
#    renamed copies go into ~/.fonts.  Takes a few minutes; run it once.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq texlive-xetex texlive-lang-korean texlive-science \
  texlive-pictures texlive-latex-extra latexmk fonts-nanum poppler-utils ghostscript \
  python3-fonttools >/dev/null
python3 - <<'PY'
import glob, os
from fontTools.ttLib import TTFont
out = os.path.expanduser("~/.fonts"); os.makedirs(out, exist_ok=True)
FAMILIES = {"NanumMyeongjo": "Nanum Myeongjo", "NanumGothic": "Nanum Gothic"}
for path in glob.glob("/usr/share/fonts/truetype/nanum/Nanum*.ttf"):
    base = os.path.basename(path)[:-4]                 # NanumMyeongjoBold
    fam = next((f for f in FAMILIES if base.startswith(f) and base[len(f):] in ("", "Bold", "ExtraBold")), None)
    if not fam:
        continue
    style = base[len(fam):] or "Regular"
    new = FAMILIES[fam]
    font = TTFont(path)
    # drop the typographic family/style records so fontconfig sees one name
    font["name"].names = [r for r in font["name"].names if r.nameID not in (16, 17, 21, 22)]
    for rec in list(font["name"].names):
        if rec.nameID == 1:
            rec.string = new if style in ("Regular", "Bold") else new + " " + style
        elif rec.nameID == 2:
            rec.string = style if style in ("Regular", "Bold") else "Regular"
        elif rec.nameID == 4:
            rec.string = new + ("" if style == "Regular" else " " + style)
        elif rec.nameID == 6:
            rec.string = (new + "-" + style).replace(" ", "")
    font.save(os.path.join(out, "Spaced-" + base + ".ttf"))
    print("registered", new, style)
PY
fc-cache -f >/dev/null
fc-list | grep -E "Nanum (Myeongjo|Gothic)" | head -4
xelatex --version | head -1
