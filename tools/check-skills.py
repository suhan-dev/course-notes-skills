#!/usr/bin/env python3
"""check-skills.py — checks the layout of every skill and the lists that name them.

    python3 tools/check-skills.py

* each skills/<name>/SKILL.md has frontmatter whose name is the folder name and
  a description (under 1024 characters), and the required sections;
* every relative link and image in every Markdown file resolves, and every
  `references/<file>.md` a skill mentions exists;
* every skill is listed in .claude-plugin/marketplace.json, README.md,
  docs/START-HERE.md and llms.txt, and llms.txt is up to date;
* no PDF, no file over 1 MB, scripts in assets/ are executable or run with an
  interpreter.
Exits 1 on any problem.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED = ['## When to use', '## What you get', '## Steps', '## Rules', '## Self-check', '## References']
problems = []


def bad(msg):
    problems.append(msg)


def tracked():
    out = subprocess.run(['git', 'ls-files', '-co', '--exclude-standard', '-z'], cwd=ROOT,
                         capture_output=True, check=True).stdout.decode()
    return [ROOT / p for p in out.split('\0') if p]


skills = sorted(p.name for p in (ROOT / 'skills').iterdir() if p.is_dir())

# 1. SKILL.md
for name in skills:
    sk = ROOT / 'skills' / name / 'SKILL.md'
    if not sk.exists():
        bad(f'{name}: no SKILL.md')
        continue
    text = sk.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        bad(f'{name}: SKILL.md has no frontmatter')
        continue
    meta = dict(line.split(':', 1) for line in m.group(1).splitlines() if ':' in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    if meta.get('name') != name:
        bad(f'{name}: frontmatter name is {meta.get("name")!r}')
    desc = meta.get('description', '')
    if not desc:
        bad(f'{name}: no description')
    elif len(desc) > 1024:
        bad(f'{name}: description is {len(desc)} characters (limit 1024)')
    if '<' in desc or '>' in desc:
        bad(f'{name}: angle brackets in the description')
    for sec in REQUIRED:
        if not re.search('^' + re.escape(sec), text, re.M):
            bad(f'{name}: SKILL.md lacks a "{sec}" section')
    if not (ROOT / 'skills' / name / 'references').is_dir():
        bad(f'{name}: no references/ folder')

# 2. links
LINK = re.compile(r'\]\(([^)\s]+)\)|<img[^>]+src="([^"]+)"')
REF = re.compile(r'(?:\b([a-z0-9-]+)/)?references/([A-Za-z0-9_.-]+\.md)')
for md in [p for p in tracked() if p.suffix == '.md']:
    text = md.read_text(encoding='utf-8')
    rel = md.relative_to(ROOT)
    prose = re.sub(r'`[^`\n]*`', '', re.sub(r'(?ms)^```.*?^```', '', text))   # links only outside code
    for m in LINK.finditer(prose):
        target = (m.group(1) or m.group(2)).split('#')[0]
        if not target or re.match(r'^[a-z]+:', target) or target.startswith('#'):
            continue
        if not (md.parent / target).exists():
            bad(f'{rel}: broken link {target}')
    parts = rel.parts
    here = parts[1] if parts[0] == 'skills' and len(parts) > 2 else None
    for m in REF.finditer(text):
        owner, fname = m.group(1), m.group(2)
        if owner in skills:
            path = ROOT / 'skills' / owner / 'references' / fname
        elif owner is None and here:
            path = ROOT / 'skills' / here / 'references' / fname
        else:
            continue
        if not path.exists():
            bad(f'{rel}: mentions {m.group(0)}, which does not exist')

# 3. lists
market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
listed = {s.split('/')[-1] for p in market['plugins'] for s in p['skills']}
for name in skills:
    if name not in listed:
        bad(f'{name}: not in .claude-plugin/marketplace.json')
for f in ['README.md', 'docs/START-HERE.md', 'llms.txt']:
    text = (ROOT / f).read_text(encoding='utf-8')
    for name in skills:
        if name not in text:
            bad(f'{name}: not mentioned in {f}')
for name in listed - set(skills):
    bad(f'marketplace.json lists {name}, which has no folder')
r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'make-llms.py'), '--check'],
                   capture_output=True, text=True)
if r.returncode:
    bad(r.stdout.strip() or r.stderr.strip())

# 4. files
for p in tracked():
    rel = p.relative_to(ROOT)
    if p.suffix.lower() == '.pdf':
        bad(f'{rel}: PDF files are not committed')
    if p.is_file() and p.stat().st_size > 1024 * 1024:
        bad(f'{rel}: over 1 MB')
    if p.suffix in ('.sh',) and 'assets' in rel.parts and not p.stat().st_mode & 0o111:
        bad(f'{rel}: not executable')

for msg in problems:
    print('✗', msg)
print(f'{len(skills)} skills checked: ' + ('ok' if not problems else f'{len(problems)} problem(s)'))
sys.exit(1 if problems else 0)
