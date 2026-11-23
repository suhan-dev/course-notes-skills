#!/bin/bash
# test-recordings.sh — checks vtt-to-text.py on YouTube-style rolling captions,
# and runs transcribe-mac.sh end to end with stand-ins for afconvert and
# whisper-cli (so it runs anywhere; on a Mac the real tools are used instead).
#
# Usage: bash test-recordings.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail() { echo "FAIL: $*"; exit 1; }

# 1. YouTube auto captions: every line appears three times, with timing tags.
cat > "$T/yt.ko.vtt" <<'VTT'
WEBVTT
Kind: captions
Language: ko

00:00:05.000 --> 00:00:07.000 align:start position:0%
[음악]

00:01:58.000 --> 00:02:01.500 align:start position:0%
 
네<00:01:58.400><c> 수업</c><00:01:58.900><c> 시작하겠습니다</c>

00:02:01.500 --> 00:02:01.510 align:start position:0%
네 수업 시작하겠습니다
 

00:02:01.510 --> 00:02:05.000 align:start position:0%
네 수업 시작하겠습니다
지난<00:02:02.000><c> 시간에는</c><00:02:02.600><c> 상전이를</c>

00:02:05.000 --> 00:02:05.010 align:start position:0%
지난 시간에는 상전이를
 

00:02:20.000 --> 00:02:23.000 align:start position:0%
지난 시간에는 상전이를
(판서 뒤) 엔트로피&nbsp;&gt; 0
VTT
python3 "$HERE/vtt-to-text.py" --start 1:58 "$T/yt.ko.vtt" > "$T/yt.md" 2> "$T/yt.err"
cat "$T/yt.md"
[ "$(grep -c '수업 시작하겠습니다' "$T/yt.md")" = 1 ] || fail "rolling lines not collapsed"
grep -q '^\*\*\[1:58\]\*\* 네 수업 시작하겠습니다 지난 시간에는 상전이를$' "$T/yt.md" || fail "first paragraph"
grep -q '^\*\*\[2:20\]\*\* (판서 뒤) 엔트로피 > 0$' "$T/yt.md" || fail "pause should start a paragraph; entities"
! grep -q '음악' "$T/yt.md" || fail "noise tag or --start"
grep -q 'YouTube captions' "$T/yt.err" || fail "source detection"

# 2. transcribe-mac.sh with stand-ins: 25 minutes of audio = 3 slices.
mkdir -p "$T/bin"
cat > "$T/bin/afconvert" <<'STUB'
#!/bin/bash
out="${!#}"
python3 -c "
import wave, sys
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(b'\0\0' * 16000 * 1500)
" "$out"
STUB
cat > "$T/bin/whisper-cli" <<'STUB'
#!/bin/bash
while [ $# -gt 0 ]; do case "$1" in -f) f="$2"; shift ;; -of) of="$2"; shift ;; -mc) mc="$2"; shift ;; esac; shift; done
[ "${mc:-}" = 0 ] || { echo "stub: -mc 0 missing" >&2; exit 1; }
k="$(basename "$f" .wav)"; k="${k#part-}"; k=$((10#$k))
{ echo WEBVTT; echo
  echo "00:00:05.000 --> 00:00:09.000"; echo "slice $k first line"; echo
  echo "00:01:00.000 --> 00:01:04.000"; echo "slice $k second line"; echo
  if [ "$k" = 1 ]; then for i in 1 2 3 4; do
    echo "00:02:0$i.000 --> 00:02:0$i.900"; echo "같은 말 반복"; echo; done; fi
} > "$of.vtt"
STUB
chmod +x "$T/bin/"*
touch "$T/model.bin" "$T/lecture.m4a"
PATH="$T/bin:$PATH" bash "$HERE/transcribe-mac.sh" "$T/lecture.m4a" "$T/model.bin" > "$T/run.log" 2> "$T/run.err"
cat "$T/run.log"; cat "$T/lecture.whisper.md"
grep -q '3 slice(s)' "$T/run.log" || fail "slicing"
ls "$T/lecture.whisper/"part-00{0,1,2}.vtt > /dev/null || fail "slice vtt files"
grep -q '^\*\*\[20:05\]\*\* slice 2 first line$' "$T/lecture.whisper.md" || fail "slice offsets"
grep -q 'repeated 4 times at 12:01' "$T/run.err" || fail "repetition warning"
PATH="$T/bin:$PATH" bash "$HERE/transcribe-mac.sh" "$T/lecture.m4a" "$T/model.bin" > "$T/rerun.log" 2>/dev/null
[ "$(grep -c 'done before, skipped' "$T/rerun.log")" = 3 ] || fail "resume"

echo "all recording checks passed"
