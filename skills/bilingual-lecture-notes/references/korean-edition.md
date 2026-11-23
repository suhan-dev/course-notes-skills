# The Korean edition

The Korean edition is the same document, not a summary or a loose
translation: same parts, sections, equations, figures and labels in the same
order. It should read as Korean written by someone who knows the subject, not
as translated English.

## Particles after numbers (조사)

A particle after `\eqref{…}` or `\ref{…}` attaches to the **number as it is
read aloud**, and the number is not known when the source is written. Get it
from the `.aux` after a build.

| Last syllable read | Numbers ending in | 와/과 | 는/은 | 를/을 | 가/이 | 로/으로 |
|---|---|---|---|---|---|---|
| vowel: 이, 사, 오, 구 | 2, 4, 5, 9 | 와 | 는 | 를 | 가 | 로 |
| ㄹ: 일, 칠, 팔 | 1, 7, 8 | 과 | 은 | 을 | 이 | **로** |
| ㅁ: 삼 | 3 | 과 | 은 | 을 | 이 | 으로 |
| ㄱ: 육 | 6 | 과 | 은 | 을 | 이 | 으로 |
| ㅂ: 십 | 10, 20, … (ending in 0, tens) | 과 | 은 | 을 | 이 | 으로 |
| ㄱ: 백 | 100, 200, … | 과 | 은 | 을 | 이 | 으로 |

- 3.2-style numbers: read the last number (3.2 → 이 → 와).
- ㄹ takes 로, not 으로 (식 (1)로).
- Part numerals are read in Sino-Korean: I 일, II 이, III 삼, IV 사, V 오,
  VI 육, VII 칠, VIII 팔, IX 구, X 십.
- The copula after a vowel-final number, `(2)이다`, `(4)이며`, is correct
  Korean (이다 is not the subject particle). The checker flags it; leave it.

`tools/ko-particles-check.py notes-ko.tex build/notes-ko.aux [start_line]`
prints every reference whose particle does not match the number. Run it after
every build and fix every flag except the copula. Starting line lets you check
only the new text.

Write sentences so that the particle is not forced where possible ("식
\eqref{…}에서", "식 \eqref{…}에 넣으면" never change), but do not contort
the prose to avoid particles.

## Terminology

- Use the standard Korean term with the English in parentheses at first use:
  `엔트로피(entropy)` is unnecessary, but `준정적 과정(quasi-static process)`
  helps. After that, the Korean term only.
- Some courses are taught with English terms in Korean speech; keep the class's
  terms (state, transfer function, pole, eigenvalue) in English inside Korean
  prose, as the class says them. Decide per course.
- One word, one meaning. If the class uses a word in two senses (for example a
  word meaning both "an internal constraint that is released" and "a quantity
  held fixed in an extremum principle"), pick a distinct Korean word for each
  and define both at the first use.
- Keep a term list per course in the repository README when the choices are
  not obvious.

## Dates and numbers

- Dates through `\isodate{YYYY-MM-DD}` → "2027년 9월 14일". The lecture log
  writes `2027.\,09.\,14 (화)`.
- Lecture labels `제3강`; blocks `제7$\sim$10강`.
- Part titles `제2부 --- 제목`.

## Typography

- `xetexko` handles line breaking; leave a normal space before `\eqref` and
  use `~` before a reference that must not start a line: `식~\eqref{eq:var}`.
- Korean italic does not exist in Nanum Myeongjo; the style fakes a slant
  (`AutoFakeSlant=0.2`) for emphasis. Prefer bold (`\keyword`) for terms.
- Korean is wider: check figures and tables in the Korean PDF separately.
- The Korean edition usually runs one or two pages longer than the English one.

## Writing order

Write a section in one language and then the same section in the other before
moving on. Do not let one edition lag: the student switches languages in the
viewer and notices immediately.
