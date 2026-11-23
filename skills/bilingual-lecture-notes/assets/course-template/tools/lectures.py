#!/usr/bin/env python3
r"""Read how far the notes have got, for the site manifest and the hub.

    python3 tools/lectures.py [notes-ko.tex notes-en.tex]
    -> {"count":12,"last":"2027-10-13"}

count is the number of the last lecture folded into the notes, last its date.
Both come from the lecture breaks in the Korean edition,

    \lecturebreak[2027-10-13]{제12강}        \lecturebreak[2027-10-13]{Lecture 12}
    \lecturebreak[2027-10-13]{제7$\sim$10강}  (several lectures in one unit: the
                                              last number counts)

Breaks without a date, and breaks whose label carries no number ("Planned",
"예정", written before the class), are skipped.  The English edition and the
lecture log (its rows read \pageref{lec:<date>}) are cross-checked; a mismatch
only prints a warning on stderr, the value still comes from the Korean breaks.

If nothing can be read, nothing is printed and the exit code is 1: publish.sh
then leaves "lectures" out of the manifest and publishes the rest.  A parsing
problem must never block a publish.  Standard library only.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BREAK = re.compile(r"\\lecturebreak\[(\d{4}-\d{2}-\d{2})\]\{([^{}]*)\}")
LOGROW = re.compile(r"\\pageref\{lec:(\d{4}-\d{2}-\d{2})\}")


def warn(msg):
    sys.stderr.write("!! lectures.py: %s\n" % msg)


def strip_comments(text):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def read(path):
    with open(path, encoding="utf-8") as f:
        return strip_comments(f.read())


def last_lecture(text):
    """(number, ISO date) of the last dated, numbered break, or None."""
    best = None
    for date, label in BREAK.findall(text):
        nums = re.findall(r"\d+", label)
        if nums:
            best = (int(nums[-1]), date)
    return best


def main(argv):
    ko_path = os.path.join(ROOT, argv[0] if argv else "notes-ko.tex")
    en_path = os.path.join(ROOT, argv[1] if len(argv) > 1 else "notes-en.tex")
    try:
        ko_text = read(ko_path)
    except OSError as e:
        warn("cannot read %s: %s" % (ko_path, e))
        return 1
    ko = last_lecture(ko_text)
    if ko is None:
        warn("no dated, numbered \\lecturebreak in %s; leaving lectures out" % ko_path)
        return 1
    try:
        en = last_lecture(read(en_path))
        if en != ko:
            warn("Korean edition says %r, English edition %r; using the Korean value" % (ko, en))
    except OSError:
        warn("cannot read %s; skipped the cross-check" % en_path)
    rows = LOGROW.findall(ko_text)
    if rows and rows[-1] != ko[1]:
        warn("last lecture-log row is %s but the last break is %s" % (rows[-1], ko[1]))
    print(json.dumps({"count": ko[0], "last": ko[1]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
