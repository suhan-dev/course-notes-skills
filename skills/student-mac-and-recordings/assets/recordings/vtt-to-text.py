#!/usr/bin/env python3
"""vtt-to-text.py — WebVTT captions to timestamped paragraphs (Markdown).

    vtt-to-text.py [--start 1:58] [--para 45] [--slice 600] FILE.vtt [MORE.vtt ...] > raw.md

Each paragraph starts with its time, e.g. ``**[12:40]** …``, which is the
format the cleaned transcript keeps (see references/recordings.md).

Two kinds of input:

* YouTube auto captions (``<date>_<id>.ko.vtt`` from yt-dlp). Each cue shows the
  previous line again and adds the new words with inline timing tags
  (``<00:00:01.500><c> word</c>``); tags are stripped and the repeats collapsed.
* whisper.cpp slices (``part-000.vtt``, ``part-001.vtt`` …). Pass them in order
  with ``--slice SECONDS``: file k is shifted by k × SECONDS.

Options:
  --start T   drop everything before T (where the class actually begins)
  --para S    start a new paragraph after S seconds (default 45) or after a
              pause of 6 s or more
  --slice S   slice length for whisper.cpp output (default 600 when several
              files are given)

Warnings on stderr: a stretch of two minutes or more with no text (a break, or
a slice the model dropped), and in whisper.cpp output a line repeated three or
more times in a row (the repetition loop that ``-mc 0`` prevents).
"""
import argparse
import html
import re
import sys

TS = re.compile(r'(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})')
TAG = re.compile(r'<[^>]*>')
INLINE = re.compile(r'<((?:\d+:)?\d{1,2}:\d{2}[.,]\d{3})>')
NOISE = re.compile(r'^[\[(][^\])]{1,24}[\])]$')       # [음악], [박수], [BLANK_AUDIO], (music)


def seconds(m):
    h, mi, s, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000


def parse_clock(t):
    v = 0.0
    for part in t.split(':'):
        v = v * 60 + float(part)
    return v


def clock(t):
    t = int(t)
    h, m, s = t // 3600, t // 60 % 60, t % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def cues(path):
    """(start, end, [lines]) for every cue in a WebVTT file."""
    text = open(path, encoding='utf-8-sig').read().replace('\r\n', '\n')
    # Cues are separated by empty lines. A line holding one space is not
    # empty: YouTube puts one right after the timing line of every cue.
    for block in re.split(r'\n\n+', text):
        lines = block.split('\n')
        for i, line in enumerate(lines):
            if '-->' in line:
                a, b = line.split('-->', 1)
                ma, mb = TS.search(a), TS.search(b)
                if ma:
                    yield seconds(ma), seconds(mb) if mb else seconds(ma), lines[i + 1:]
                break


def clean(line):
    line = html.unescape(TAG.sub('', line)).replace(' ', ' ')
    return ' '.join(line.split())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('files', nargs='+')
    ap.add_argument('--start', default='0')
    ap.add_argument('--para', type=float, default=45)
    ap.add_argument('--slice', type=float, default=None)
    args = ap.parse_args()
    start = parse_clock(args.start)
    step = args.slice if args.slice is not None else (600 if len(args.files) > 1 else 0)

    # 1. Lines with the time they first appear.
    lines, youtube = [], False
    for k, path in enumerate(args.files):
        raw = open(path, encoding='utf-8-sig').read()
        youtube = youtube or '<c>' in raw or '</c>' in raw
        for a, b, body in cues(path):
            for line in body:
                text = clean(line)
                if text and not NOISE.match(text):
                    # A line with word timings ends just after its last word;
                    # the cue itself runs on until the next one starts.
                    words = [seconds(TS.search(m.group(1))) for m in INLINE.finditer(line)]
                    end = min(b, max(words) + 0.6) if words else b
                    lines.append((a + k * step, end + k * step, text))

    # 2. Collapse repeats (rolling captions; whisper loops are counted).
    kept, run, warnings = [], 1, []
    for a, b, text in lines:
        if kept and text == kept[-1][2]:
            run += 1
            continue
        if not youtube and run >= 3:
            warnings.append(f'"{kept[-1][2][:40]}" repeated {run} times at {clock(kept[-1][0])}: '
                            'rerun that slice (is -mc 0 set?)')
        run = 1
        kept.append((a, b, text))
    if not youtube and run >= 3 and kept:
        warnings.append(f'"{kept[-1][2][:40]}" repeated {run} times at {clock(kept[-1][0])}')
    kept = [x for x in kept if x[0] >= start]

    # 3. Paragraphs.
    paras, cur, cur_t, last_end = [], [], None, None
    for a, b, text in kept:
        if last_end is not None and a - last_end >= 120:
            warnings.append(f'no text from {clock(last_end)} to {clock(a)}')
        if cur and (a - cur_t >= args.para or (last_end is not None and a - last_end >= 6)):
            paras.append((cur_t, ' '.join(cur)))
            cur = []
        if not cur:
            cur_t = a
        cur.append(text)
        last_end = max(b, last_end or 0)
    if cur:
        paras.append((cur_t, ' '.join(cur)))

    for t, text in paras:
        print(f'**[{clock(t)}]** {text}\n')
    for w in warnings:
        print('warning: ' + w, file=sys.stderr)
    words = sum(len(t.split()) for _, t in paras)
    span = f'{clock(paras[0][0])}–{clock(kept[-1][1])}' if paras else 'nothing'
    print(f'{len(paras)} paragraphs, {words} words, {span}, '
          f'{"YouTube captions" if youtube else "plain cues"}', file=sys.stderr)


if __name__ == '__main__':
    main()
