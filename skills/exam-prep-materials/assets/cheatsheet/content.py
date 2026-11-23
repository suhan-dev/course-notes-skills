# content.py --- what goes on the cheat sheet.  build.py turns it into
# cheatsheet.html; pw.js prints the PDF and reports how full each column is.
#
# Every string that holds LaTeX must be a raw string r'...': in a normal
# string "\frac" starts with a form feed and "\b" is a backspace.
# Inside $...$ write \lt and \gt for < and > (build.py also converts them).

TITLE = '샘플 과목 · 치팅시트'
SUBTITLE = '노트 요약'
META = '2027-2 · 중간고사 대비'
FOOT = '노트 기준 요약 · 노트 밖 내용은 [노트 밖] 표시'

# One colour per part of the notes, so a box shows at a glance where it lives.
# (class, colour, tint, legend label)
PARTS = [
    ('p1', '#2f63b0', '#e8f0fb', '1부 무작위 걷기와 확산'),
    ('p2', '#23806f', '#e3f3ef', '2부 정상 상태'),
    ('pw', '#a8741a', '#fbf2e1', '헷갈리는 것'),
]


def st(setup, fixed, varied, extremum):
    """The first line of a derivation box: what the system touches, what is
    held fixed, what is varied, what is extremised (설정 · 고정 · 바꿈 · 극값)."""
    return (f'<div class="st"><b>설정</b>{setup}<b>고정</b>{fixed}'
            f'<b>바꿈</b>{varied}<b>극값</b>{extremum}</div>')


# (part class, number shown in the header chip, title, body HTML)
BOXES = [
    ('pw', '!', '표기와 관례', r'''
<ul>
<li>$D$의 정의: 노트는 $\langle x^2\rangle=2Dt$ (1차원). $\langle x^2\rangle=Dt$로 쓰는 책도 있다.</li>
<li>흐름 $J=-D\,\partial c/\partial x$: 농도가 높은 쪽 → 낮은 쪽.</li>
</ul>'''),
    ('p1', '§1', '무작위 걷기', r'''
<div class="k">$x_n=\sum_{k=1}^n s_k,\quad s_k=\pm a\ \Rightarrow\ \langle x_n\rangle=0,\ \ \langle x_n^2\rangle=na^2$</div>
<ul>
<li>분산이 더해지는 이유: 독립이면 $\langle s_js_k\rangle=0\ (j\ne k)$.</li>
<li>치우친 걷기(확률 $p$로 $+a$): $\langle x_n\rangle=na(2p-1)$, $\operatorname{Var}x_n=4na^2pq$.</li>
</ul>'''),
    ('p1', '§2', '확산 방정식', r'''
<div class="k">$\dfrac{\partial c}{\partial t}=D\dfrac{\partial^2c}{\partial x^2},\qquad c(x,t)=\dfrac{e^{-x^2/4Dt}}{\sqrt{4\pi Dt}}$</div>
<ul>
<li>$t=n\tau$, $D=a^2/2\tau$ → $\langle x^2\rangle=2Dt$. 폭은 $\sqrt t$에 비례.</li>
<li>거리 10배 → 시간 100배. 물속 작은 분자 $D\sim10^{-9}\,\mathrm{m^2/s}$: 1 mm에 약 500 s.</li>
</ul>'''),
    ('p2', '§3', '정상 상태의 막', st('두 저장소 사이의 막', r'$c(0)=c_0,\ c(L)=c_L$', r'$c(x)$', r'없음 ($\partial_t c=0$)') + r'''
<div class="k">$c''=0\ \Rightarrow\ c(x)=c_0+(c_L-c_0)\,x/L,\qquad J=D\,(c_0-c_L)/L$</div>
<ul><li>정상 상태에서는 $J$가 어디서나 같다(쌓이는 곳이 없다).</li></ul>'''),
]
