#!/usr/bin/env python3
r"""Cut the empty bottom off every page of a tall-page problem book.

    python3 crop.py Problems-EN.pdf [more PDFs ...]

tallproblems.sty sets 30in-tall paper so that one problem and one solution
always fit on one page; left alone, every page ends in a long empty stretch.
Ghostscript's bbox device measures what is actually printed on each page;
the MediaBox (and CropBox) is then raised to BOTTOM pt below the lowest ink,
leaving the top untouched.  Because the top coordinates do not change, the
bookmarks' and links' destinations (the "top" of an XYZ destination) stay
right.  The document must have no running foot (a page number at the bottom
would stop the crop).

Needs: gs (ghostscript), pypdf (pip install pypdf).
"""
import re
import subprocess
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("crop.py needs pypdf:  pip install pypdf")

BOTTOM = 40.0      # margin kept below the content (pt); the top margin is 0.7in = 50pt
MIN_H = 180.0      # lowest page height (pt): flatter pages look like strips in the viewer

BBOX = re.compile(r"%%HiResBoundingBox:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")


def bboxes(path):
    run = subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=bbox", path],
        capture_output=True, text=True)
    return [tuple(float(v) for v in m.groups()) for m in BBOX.finditer(run.stderr)]


def main(paths):
    for path in paths:
        reader = PdfReader(path)
        boxes = bboxes(path)
        if len(boxes) != len(reader.pages):
            sys.exit(f"{path}: gs measured {len(boxes)} pages, the PDF has {len(reader.pages)}")
        # clone_from copies the whole document: bookmarks, named destinations, info
        writer = PdfWriter(clone_from=reader)
        heights = []
        for page, (_, lly, _, _) in zip(writer.pages, boxes):
            x0, y0, x1, y1 = (float(v) for v in page.mediabox)
            low = max(y0, min(lly - BOTTOM, y1 - MIN_H))
            page.mediabox.lower_left = (x0, low)
            page.cropbox.lower_left = (x0, low)
            heights.append(y1 - low)
        with open(path, "wb") as f:
            writer.write(f)
        print(f"cropped {path}: {len(heights)} pages, "
              f"height {min(heights)/72:.1f}-{max(heights)/72:.1f} in")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
