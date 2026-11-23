#!/bin/bash
# fetch-youtube.sh — save a class video's audio and its Korean auto captions
# into the course folder. Run it on the student's Mac in a Remote Control
# session, from the course folder: the cloud container's proxy refuses YouTube
# and the device shell of the agent app has no network.
#
# Usage:  bash fetch-youtube.sh <video URL> [out dir, default 수업녹음]
#
# Writes <out>/<upload date>_<video id>.m4a and .ko.vtt. yt-dlp runs from a
# throwaway virtual environment under the temporary folder, so nothing is
# installed on the Mac for good.
set -euo pipefail
URL="${1:?usage: fetch-youtube.sh <video URL> [out dir]}"
OUT="${2:-수업녹음}"
VENV="${TMPDIR:-/tmp}/ytdlp-venv"

if [ ! -x "$VENV/bin/yt-dlp" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip yt-dlp certifi
fi
# A python.org Python on macOS has no root certificates until its "Install
# Certificates" step is run; point it at certifi's bundle instead.
export SSL_CERT_FILE="$("$VENV/bin/python" -m certifi)"

mkdir -p "$OUT"
"$VENV/bin/yt-dlp" --no-playlist \
  -f 'bestaudio[ext=m4a]/bestaudio' \
  --write-auto-subs --sub-langs ko --sub-format vtt \
  -o "$OUT/%(upload_date)s_%(id)s.%(ext)s" \
  "$URL"
ls -l "$OUT"
