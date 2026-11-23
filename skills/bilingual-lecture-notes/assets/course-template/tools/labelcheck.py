#!/usr/bin/env python3
r"""Check that the two editions carry the same labels, numbers and bookmarks.

    python3 tools/labelcheck.py build/notes-en build/notes-ko

Reads <base>.aux of each edition and compares every \newlabel: the same label
names must exist in both, with the same printed number (section 2.3 in one
edition must be 2.3 in the other, equation (17) must be (17)).  Page numbers
are allowed to differ: the two editions have different page counts.

If pypdf is installed it also compares the PDF bookmarks: the sequence of
NUMBERED bookmarks ("2", "2.3", "A.1" ...) must be identical in the two PDFs,
because the site viewer keys on those numbers to carry the reader's place
across the EN/KO switch, and each number must appear only once.

Exit code 1 on any mismatch, with a list of what differs.
"""
import os
import re
import sys

NEWLABEL = re.compile(r"\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}\{([^{}]*)\}")
NUMKEY = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)*|[A-Z](?:\.[0-9]+)*)\.?(?=\s|$)")
SKIP = ("lec:",)          # lecture-break labels: dates, same in both, pages differ


def labels(base):
    path = base + ".aux"
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        sys.exit("missing %s: build both editions first" % path)
    out = {}
    for name, num, _page in NEWLABEL.findall(text):
        if name.startswith(SKIP) or name.endswith("@cref"):
            continue
        out[name] = num
    return out


def bookmark_keys(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    keys = []

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
            else:
                m = NUMKEY.match(str(it.title))
                if m:
                    keys.append(m.group(1))
    walk(PdfReader(pdf_path).outline)
    return keys


def main(a, b):
    la, lb = labels(a), labels(b)
    bad = []
    only_a = sorted(set(la) - set(lb))
    only_b = sorted(set(lb) - set(la))
    if only_a:
        bad.append("only in %s: %s" % (a, ", ".join(only_a[:20])))
    if only_b:
        bad.append("only in %s: %s" % (b, ", ".join(only_b[:20])))
    for name in sorted(set(la) & set(lb)):
        if la[name] != lb[name]:
            bad.append("%s is %r in %s but %r in %s" % (name, la[name], a, lb[name], b))
    ka, kb = bookmark_keys(a + ".pdf"), bookmark_keys(b + ".pdf")
    if ka is not None and kb is not None:
        if ka != kb:
            bad.append("numbered bookmarks differ: %s vs %s" % (ka[:30], kb[:30]))
        dup = sorted({k for k in ka if ka.count(k) > 1})
        if dup:
            bad.append("bookmark numbers used twice: %s" % ", ".join(dup))
    if bad:
        print("\n".join("FAIL: " + x for x in bad))
        return 1
    extra = "" if ka is None else ", %d numbered bookmarks" % len(ka)
    print("ok: %d labels match%s" % (len(la), extra))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
