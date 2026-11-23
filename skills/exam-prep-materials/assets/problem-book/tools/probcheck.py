#!/usr/bin/env python3
"""Check that the two editions of a problem book match, and list where each
problem and solution sits.

    python3 tools/probcheck.py [build/problems-en build/problems-ko]

Reads the .aux files of the two editions (the labels chapstart:<n>,
probstart:<n.m>, solstart:<n.m> written by problems/common.tex) and fails if
the editions do not carry the same chapters and problems in the same order,
or if a problem has no solution.  The web viewer keys on these numbers when
the reader switches languages, so a mismatch would land them on the wrong
problem.  Standard library only.
"""
import re
import sys

LABEL = re.compile(r'\\newlabel\{(chapstart|probstart|solstart):([^}]*)\}\{\{[^}]*\}\{([^}]*)\}')
LAST = re.compile(r'\\gdef\s*\\@abspage@last\{(\d+)\}')


def read(base):
    path = base if base.endswith('.aux') else base + '.aux'
    try:
        text = open(path, encoding='utf-8').read()
    except OSError:
        sys.exit('missing %s: build that edition first' % path)
    rows = [(kind, ident, page) for kind, ident, page in LABEL.findall(text)]
    last = LAST.search(text)
    return rows, int(last.group(1)) if last else None


def main(argv):
    bases = argv[1:3] if len(argv) >= 3 else ['build/problems-en', 'build/problems-ko']
    ed = {'en': read(bases[0]), 'ko': read(bases[1])}
    bad = []
    seq = {lang: [(k, i) for k, i, _ in rows] for lang, (rows, _) in ed.items()}
    if seq['en'] != seq['ko']:
        only_en = sorted(set(seq['en']) - set(seq['ko']))
        only_ko = sorted(set(seq['ko']) - set(seq['en']))
        bad.append('the editions differ: only EN %s, only KO %s%s' % (
            only_en or '-', only_ko or '-',
            '' if only_en or only_ko else ' (same labels, different order)'))
    for lang, (rows, last) in ed.items():
        probs = [i for k, i, _ in rows if k == 'probstart']
        sols = [i for k, i, _ in rows if k == 'solstart']
        if not probs:
            bad.append('%s: no problems found (is problems/common.tex loaded?)' % lang.upper())
        if probs != sols:
            bad.append('%s: problems without a solution: %s' % (
                lang.upper(), sorted(set(probs) - set(sols)) or '(order differs)'))
        for k, i, p in rows:
            if not p.isdigit():
                bad.append('%s: %s:%s is on page "%s"; page numbers must be plain '
                           'arabic numbers counted from the title page' % (lang.upper(), k, i, p))
    if bad:
        print('\n'.join('FAIL: ' + b for b in bad))
        return 1

    # problem n.m: statement page, solution pages, in both editions
    print('%-6s %-16s %-16s' % ('', 'EN  prob | sol', 'KO  prob | sol'))
    ranges = {}
    for lang, (rows, last) in ed.items():
        marks = [(k, i, int(p)) for k, i, p in rows]
        out = {}
        for n, (k, i, p) in enumerate(marks):
            if k != 'solstart':
                continue
            nxt = next((q for kk, _, q in marks[n + 1:] if kk != 'solstart' and q > p), None)
            end = (nxt - 1) if nxt else last
            start = next(q for kk, ii, q in marks if kk == 'probstart' and ii == i)
            out[i] = (start, p, end)
        ranges[lang] = out
    for i in ranges['en']:
        cells = []
        for lang in ('en', 'ko'):
            s, a, b = ranges[lang][i]
            cells.append('%3d | %d-%d' % (s, a, b) if b and b > a else '%3d | %d' % (s, a))
        print('%-6s %-16s %-16s' % (i, cells[0], cells[1]))
    print('OK: %d problems, EN %s pages, KO %s pages' % (
        len(ranges['en']), ed['en'][1], ed['ko'][1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
