#!/usr/bin/env python3
"""Make the hub's preview thumbnail of a course from page 1 of its notes.

    python3 make-thumb.py Notes-EN.pdf thumbs/<course>.jpg [--width 700]

Renders the title page at about twice the target width (pdftoppm), maps it to
the hub's dark palette (white paper -> --bg-like #0d0e12, black ink -> the
light ink #f4f1ea, greys in between, so it reads as a dark page rather than a
photographic negative), downsamples to the target width with a light sharpen
so small type stays legible, and writes a progressive JPEG.  Letter paper
gives 700 x 906, A4 700 x 990.

Needs: pdftoppm (poppler-utils), Pillow.
"""
import argparse
import os
import subprocess
import tempfile

from PIL import Image, ImageFilter

BG = (13, 14, 18)        # page colour of the thumbnails (#0d0e12)
INK = (244, 241, 234)    # the hub's --ink


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('pdf')
    ap.add_argument('out')
    ap.add_argument('--width', type=int, default=700)
    ap.add_argument('--page', type=int, default=1)
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        stem = os.path.join(tmp, 'p')
        # 2x the target width, then downsample: crisper than rendering at size
        subprocess.run(['pdftoppm', '-f', str(a.page), '-l', str(a.page), '-singlefile',
                        '-scale-to-x', str(2 * a.width), '-scale-to-y', '-1',
                        '-gray', '-png', a.pdf, stem], check=True)
        grey = Image.open(stem + '.png').convert('L')

    # duotone: luminance 255 (paper) -> BG, 0 (ink) -> INK
    lut = []
    for ch in range(3):
        lut += [round(BG[ch] + (INK[ch] - BG[ch]) * (1 - v / 255)) for v in range(256)]
    dark = Image.merge('RGB', (grey, grey, grey)).point(lut)

    h = round(dark.height * a.width / dark.width)
    small = dark.resize((a.width, h), Image.LANCZOS)
    small = small.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=2))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    small.save(a.out, 'JPEG', quality=86, optimize=True, progressive=True)
    print('%s: %d x %d' % (a.out, a.width, h))


if __name__ == '__main__':
    main()
