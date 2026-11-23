# Explaining in chat

Study questions arrive as short messages ("이거 왜 이렇게 돼?", "뭔 뜻?",
a photo of a key with a circle on one line). The student wants answers that
never stop halfway. These rules came from the moments when an answer failed.

## The rules

1. **Answer the literal question first**, in two or three lines. For an
   ambiguous "what does this mean / why", answer the simplest reading first
   (often: what a symbol stands for), then go deeper.
2. **Finish every derivation** to its conclusion and check it. No filler, no
   skipped middle steps, no "it can be shown".
3. **Any minimum or maximum claim checks both orders**: the first-order
   condition and the second-order condition (stability).
4. **Set-up up front**: the system and its subsystems, what it touches, what
   is held fixed, which internal variable is varied, what is extremised.
5. **Words with two meanings get both defined at once.** Example: a word used
   both for "an internal constraint that is released" and for "the quantity
   held fixed in an extremum principle". Say which one is meant each time.
6. **Signs by whose ledger**: say from which subsystem's point of view heat
   and work are counted.
7. **If the student's reasoning is right, say so** and add only what is
   missing; if one step is wrong, point to that step.
8. **Define every symbol at first use**, and for every derivative say what is
   differentiated, with respect to what, holding what fixed, for example
   μ_A = (∂G/∂N_A)_{T,P,N_B}. Do it unasked; when walking through someone
   else's key, flag where it skips either.
9. **After a second confused follow-up on one concept, stop answering
   piecemeal**: give one complete explanation with a comparison table, then the
   general rule with both orders.
10. **Prose, like a teaching assistant**, with few headings and bullets.
    Lists of fragments read as machine output.

## Math in chat

If the chat surface does not render LaTeX in plain messages, post the
explanation as an HTML widget with KaTeX (`assets/katex-widget/`):

1. Write the body as HTML with `$…$` and `$$…$$`.
2. `NODE_PATH=<dir with katex> node check.js body.html`: every formula parses,
   and no raw `<` or `>` sits inside math. Write `\lt` and `\gt` there:
   `$T<T_c$` opens an HTML tag and swallows the rest of the line.
3. `python3 mkwidget.py body.html out.json TITLE` wraps it with KaTeX 0.16.9
   and auto-render; post `out.json`'s title and code as the widget.
4. In the chat message itself, one line saying what the widget answers.

Macros available in the widget: `\dbar` (đ) and `\pdc{f}{x}{held}` for
(∂f/∂x)_held; write `\mathrm{d}` and `k_B` explicitly. Titles: letters,
digits, `_`, `-` only.
