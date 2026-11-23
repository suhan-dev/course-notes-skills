#!/usr/bin/env python3
"""Check the Korean particle after \\eqref{...} / \\ref{...} against the spoken number.

usage: python3 tools/ko-particles-check.py notes-ko.tex build/notes-ko.aux [start_line]

In Korean the particle after a number follows how the number is read aloud:
  ...1, ...7, ...8 (일, 칠, 팔) end in ㄹ: 과/은/을/이 and 로 (not 으로)
  ...3 (삼) ㅁ, ...6 (육) ㄱ, ...10/20 (십) ㅂ, ...100 (백) ㄱ: 과/은/을/이/으로
  ...2, ...4, ...5, ...9 (이, 사, 오, 구) end in a vowel: 와/는/를/가/로
  Part numerals: I 일, II 이, III 삼, IV 사, V 오, VI 육.  For "3.2" read the last number.
Build first, so the .aux holds the printed numbers.  The checker also flags the
copula 이다/이며 after a vowel-final number, which is correct Korean: leave those.
"""
import re
import sys

tex, aux = sys.argv[1], sys.argv[2]
start = int(sys.argv[3]) if len(sys.argv) > 3 else 1
labels = {}
for m in re.finditer(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}', open(aux, encoding='utf-8').read()):
    labels[m.group(1)] = m.group(2)

DIG = {'1': ('일', 'ㄹ'), '2': ('이', ''), '3': ('삼', 'ㅁ'), '4': ('사', ''), '5': ('오', ''),
       '6': ('육', 'ㄱ'), '7': ('칠', 'ㄹ'), '8': ('팔', 'ㄹ'), '9': ('구', '')}
ROMAN = {'I': 'ㄹ', 'II': '', 'III': 'ㅁ', 'IV': '', 'V': '', 'VI': 'ㄱ',
         'VII': 'ㄹ', 'VIII': 'ㄹ', 'IX': '', 'X': 'ㅂ'}


def batchim(num):
    num = num.strip()
    if num in ROMAN:
        return ROMAN[num]
    last = re.split(r'[.\-]', num)[-1]
    if not last.isdigit():
        return None
    if last[-1] != '0':
        return DIG[last[-1]][1]
    if len(last) >= 2 and last[-2] != '0':
        return 'ㅂ'          # 십
    if len(last) >= 3 and last[-3] != '0':
        return 'ㄱ'          # 백
    return 'ㄴ'              # 천 / 영 is not used


# particle pairs: (after vowel, after consonant); 로/으로 depends on ㄹ too
PAIRS = [('와', '과'), ('는', '은'), ('를', '을'), ('가', '이'), ('랑', '이랑'),
         ('나', '이나'), ('며', '이며'), ('라', '이라'), ('다', '이다'), ('였', '이었')]

ref_re = re.compile(r'\\(?:eq)?ref\{([^}]*)\}\)?((?:\\[a-z]+\{[^}]*\})?)([가-힣]{1,3})')
bad = 0
for ln, line in enumerate(open(tex, encoding='utf-8'), 1):
    if ln < start:
        continue
    for m in ref_re.finditer(line):
        lab, _, word = m.groups()
        if lab not in labels:
            print(f'{ln}: unknown label {lab}')
            continue
        b = batchim(labels[lab])
        if b is None:
            continue
        vowel = (b == '')
        problem = None
        if word.startswith('으로'):
            if vowel or b == 'ㄹ':
                problem = '로'
        elif word.startswith('로'):
            if not vowel and b != 'ㄹ':
                problem = '으로'
        else:
            for v, c in PAIRS:
                if word.startswith(c) and vowel and not word.startswith(v):
                    # e.g. '이' after a vowel-final number (unless it is part of a noun)
                    problem = v
                    break
                if word.startswith(v) and not vowel and not word.startswith(c):
                    problem = c
                    break
        if problem:
            bad += 1
            print(f'{ln}: {labels[lab]} + "{word}"  -> use "{problem}…"   | {line.strip()[:110]}')
print('problems:', bad)
