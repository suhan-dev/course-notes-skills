#!/usr/bin/env python3
"""slice-wav.py IN.wav OUT_DIR [SECONDS] — split a PCM WAV file into
OUT_DIR/part-000.wav, part-001.wav, … of SECONDS each (default 600; the last
one is shorter) and print how many were written. Standard library only, so it
runs with the python3 that ships with macOS developer tools."""
import os
import sys
import wave

if len(sys.argv) < 3:
    sys.exit(__doc__)
src, out = sys.argv[1], sys.argv[2]
length = int(sys.argv[3]) if len(sys.argv) > 3 else 600
os.makedirs(out, exist_ok=True)
count = 0
with wave.open(src, 'rb') as w:
    params = w.getparams()
    per = params.framerate * length
    while True:
        frames = w.readframes(per)
        if not frames:
            break
        with wave.open(os.path.join(out, f'part-{count:03d}.wav'), 'wb') as o:
            o.setparams(params)
            o.writeframes(frames)
        count += 1
print(count)
