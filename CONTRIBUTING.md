# How a skill in this repository is built

Every skill is a folder under `skills/<name>/`. Keep this layout;
`tools/check-skills.py` and the README depend on it.

```
skills/<name>/
├── SKILL.md            the entry point: frontmatter, steps, rules, self-check (aim for 100–250 lines)
├── references/         the detail, one topic per file
├── assets/             working templates and scripts, generalised from what was used, with their tests
└── screenshots/        optional PNGs of a sample, placeholder content only, each under 1 MB
```

## SKILL.md

```markdown
---
name: <folder name>
description: <one sentence: what it does and when to use it; starts with a verb; under 400 characters>
---

# <Readable title>

<two or three paragraphs: what you get, and where it came from>

## When to use
## What you get            (the files in assets/ and what each does)
## Steps: <a job>          (numbered, imperative, each one checkable; one section per job)
## Rules                   (the non-negotiable ones, each with its reason when not obvious)
## Configuration           (when the skill has settings: every one, its meaning, an example)
## Self-check              (a checklist to run before reporting)
## References              (links to references/*.md)
```

`When to use`, `What you get`, at least one `Steps` section, `Rules`,
`Self-check` and `References` are required (`check-skills.py` checks).

Write for another agent that has never seen the student or the courses. Say
*why* a rule exists when it is not obvious ("the KO edition keeps the EN
numbers because the student flips between them while studying"). When a rule
came from a mistake, the mistake is the best reason; give it.

## Placeholders and sample data

Assets must build or run once placeholders are filled. Use these everywhere so
the skills agree:

| Placeholder | Meaning | Sample value |
|---|---|---|
| course name | `\coursename{…}`, viewer title, hub row | `Sample Course` / `샘플 과목` |
| term | `\term{…}`, hub header | `Fall 2027` / `2027-2` |
| lecture dates | `\lecturebreak[…]`, lecture log | `2027-09-01`, `2027-09-06` … (real weekdays) |
| note-taker | `\notesby{…}` | `Student` |
| `ACCOUNT` | GitHub account in Pages URLs | `ACCOUNT.github.io` |
| `HUB-REPO` | the hub's repository | `ACCOUNT.github.io/HUB-REPO/` |
| `<course>`, `<term>` | folders on the Mac | `~/Desktop/<term>/<course>/` |
| storage-key prefix | viewer `LS_LANG`, `LS_POS`, `SS_SOL` | `sample.` (unique per course) |
| named-destination prefix | viewer `MARK`, problem macros | `pb` |
| school | hub footer | `학교 이름` |

Sample content is written fresh: the sample notes are about random walks,
diffusion and steady states; the sample problems are new. Never paste text,
equations, figures or problems from a real course's notes, handouts or exams,
even rephrased.

## Assets

- Generalise from what was actually used, then **run it**: every template in
  `assets/` must build, and every script must pass its test, in a fresh
  folder. Say in the skill what was tested and how.
- Scripts that run on the student's Mac (zsh by default, bash 3.2) or in the
  agent's device shell (Linux) avoid features those shells lack.
- LaTeX strings in Python are raw strings (`r'…'`).
- Pin third-party versions (pdf.js 3.11.174, KaTeX 0.16.9) and say where they
  load from.
- No PDFs, no build output, no fonts, no vendored libraries.

## References

One topic per file, linked from `SKILL.md`. History is worth keeping when it
explains a rule: "a version without X did Y" saves the next agent from
reintroducing Y. Keep it about the method, not about the student.

## Before a commit

```bash
bash tools/privacy-scan.sh       # needs tools/private-patterns.txt (git-ignored) for names
python3 tools/check-skills.py
```

plus the tests of the skill you changed. A new skill is also listed in
`.claude-plugin/marketplace.json`, `README.md`, `llms.txt` and
`docs/START-HERE.md`.
