#!/bin/bash
# transcribe-mac.sh — transcribe one class recording on the student's Mac with
# whisper.cpp, in ten-minute slices, with no text carried from one segment to
# the next (-mc 0). Run it in a Remote Control session: it needs the Mac's own
# tools, and the device shell of the agent app has no network or Homebrew.
#
# Usage:  bash transcribe-mac.sh <recording.m4a> [model.bin]
#
# Needs:  brew install whisper-cpp
#         a ggml model, default ~/.cache/whisper/ggml-large-v3-turbo.bin
#         (about 1.6 GB: ask the student before downloading it)
#         afconvert (part of macOS) and python3
#
# Writes <recording>.whisper/part-NNN.vtt, one per slice (a rerun skips the
# slices already done; delete one to redo it), and <recording>.whisper.md:
# timestamped paragraphs made by vtt-to-text.py, read next to this script.
# Set SLICE=<seconds> to change the slice length.
set -euo pipefail
IN="${1:?usage: transcribe-mac.sh <recording.m4a> [model.bin]}"
MODEL="${2:-$HOME/.cache/whisper/ggml-large-v3-turbo.bin}"
SLICE="${SLICE:-600}"
HERE="$(cd "$(dirname "$0")" && pwd)"

command -v whisper-cli >/dev/null || { echo "whisper-cli not found: brew install whisper-cpp" >&2; exit 1; }
command -v afconvert >/dev/null || { echo "afconvert not found (it ships with macOS)" >&2; exit 1; }
[ -f "$MODEL" ] || { echo "model not found: $MODEL" >&2; exit 1; }
[ -f "$IN" ] || { echo "no such recording: $IN" >&2; exit 1; }

BASE="${IN%.*}"
OUT="$BASE.whisper"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$OUT"

# 16 kHz mono 16-bit PCM is what whisper.cpp reads; afconvert does it without ffmpeg.
afconvert -f WAVE -d LEI16@16000 -c 1 "$IN" "$TMP/all.wav"
n="$(python3 "$HERE/slice-wav.py" "$TMP/all.wav" "$TMP" "$SLICE")"
echo "$n slice(s) of $SLICE s"

for wav in "$TMP"/part-*.wav; do
  name="$(basename "$wav" .wav)"
  if [ -s "$OUT/$name.vtt" ]; then echo "$name: done before, skipped"; continue; fi
  echo "$name: transcribing"
  # -mc 0: no previous text as prompt. With the default the decoder can fall
  # into a loop, repeat one phrase, and silently drop the rest of the audio.
  whisper-cli -m "$MODEL" -f "$wav" -l ko -mc 0 -np -ovtt -of "$OUT/$name"
done

python3 "$HERE/vtt-to-text.py" --slice "$SLICE" "$OUT"/part-*.vtt > "$BASE.whisper.md"
echo "wrote $BASE.whisper.md"
