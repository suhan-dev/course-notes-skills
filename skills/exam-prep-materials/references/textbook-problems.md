# Textbook problem collections

The student may upload the textbook as OCR'd plain text (`<book>.pdf.txt`,
about a megabyte) and ask for "the interesting end-of-section problems, ordered
by importance, as a PDF with full calculations".

## Reading an OCR'd textbook

- Prose survives; mathematics does not. Fractions, exponents, Greek letters,
  subscripts and many numbers are garbled, and figures are lost.
- Problems follow headers like `PROBLEMS` (OCR variants: `PROlJLEMS`,
  `PROBLEM`). Numbers look like `4.5-9.` at the start of a line:
  `grep -n '^4\.5-9\.' book.txt`.
- Find where the part the course covers ends (for example where statistical
  mechanics begins) so the selection stays in range.
- Printed "Answer:" lines, where present, help confirm a reconstruction.

## Selecting

- Choose by topic and by what the student liked (a problem type they named),
  and rank: ★★★ (must do), ★★, ★. A table of the ★★★ problems on page 1.
- Group by topic in the order of the notes (for example photon gas,
  stability, maximum work, engines, Maxwell relations, phase transitions,
  van der Waals, mixing, other systems), one source file per topic.

## Writing each problem

```latex
\prob{3.6-1}{The expanding universe as a photon cavity}{3}
문제 … (the statement, reconstructed where needed)
설정 … (reservoirs, what is fixed, what is varied, what is extremised)
풀이 … (every step)
포인트 … (what to remember)
```

- Reconstruct garbled statements from context, units and the printed answer,
  and **flag every reconstruction inside the problem text**; list the shakiest
  ones in the README.
- **Verify every number with sympy** (a `checks/` folder next to the sources).
- Where the book's printed answer is wrong, give the corrected value and say
  so in the problem.

## Building

One main file that `\InputIfFileExists` each topic file, so a topic can be
added later; three XeLaTeX passes. Copy the PDF to the Mac course folder.
