#!/usr/bin/env bash
# Fails if the repository holds anything that must never be published: e-mail
# addresses, school or mail domains, keys and tokens, home-directory paths,
# real Pages sites, YouTube links, phone numbers, PDFs, or the real names of the
# people and courses this came from. Run before every push:
#     bash tools/privacy-scan.sh
# Names are never written here (this file is public). Put them in
# tools/private-patterns.txt, which git ignores: one extended regex per line,
# # for comments (see tools/private-patterns.example.txt). Or point
# PRIVATE_PATTERNS at a file.
set -u
cd "$(dirname "$0")/.."
fail=0
files() { git ls-files -co --exclude-standard -z; }
check() { # label, extended regex, [regex a whole match may equal and still be allowed]
  local hits
  hits=$(files | xargs -0 grep -nIE "$2" -- 2>/dev/null | grep -v '^tools/privacy-scan.sh:' || true)
  if [ -n "${3:-}" ] && [ -n "$hits" ]; then
    hits=$(printf '%s\n' "$hits" | while IFS= read -r line; do
      printf '%s\n' "${line#*:*:}" | grep -oE "$2" | grep -qvxE "$3" && printf '%s\n' "$line"; done)
  fi
  if [ -n "$hits" ]; then echo "✗ $1"; echo "$hits" | head -20; fail=1; else echo "✓ $1"; fi
}
check "e-mail addresses"           '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}' \
                                   '[A-Za-z0-9._%+-]+@(example\.(com|org|edu|test)|users\.noreply\.github\.com)|noreply@[a-z.]+'
check "school and mail domains"    '\.ac\.kr|gmail\.com|naver\.com|daum\.net|hanmail\.net|kakao\.com'
check "tokens and keys"            'AIza[0-9A-Za-z_-]{30,}|ghp_[0-9A-Za-z]{30,}|github_pat_|gh[osu]_[0-9A-Za-z]{30,}|xox[bap]-|sk-[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
check "password assignments"       '(PASSWORD|SECRET|TOKEN)[[:space:]]*=[[:space:]]*[^[:space:]<{$"'"'"'#]'
check "home-directory paths"       '/Users/[A-Za-z0-9._-]+|/home/[a-z][a-z0-9_-]*/' \
                                   '/Users/Shared'
check "real Pages sites"           '[A-Za-z0-9-]+\.github\.io' \
                                   '(ACCOUNT|<account>|username|example)\.github\.io'
check "video links"                'youtube\.com/(watch|channel|@|c/|playlist)|youtu\.be/'
check "phone numbers"              '01[016789]-?[0-9]{3,4}-?[0-9]{4}'
names="${PRIVATE_PATTERNS:-tools/private-patterns.txt}"
if [ -f "$names" ]; then
  pat=$(grep -vE '^[[:space:]]*(#|$)' "$names" | paste -sd'|' -)
  if [ -n "$pat" ]; then check "private names ($names)" "$pat"; else echo "• private names: $names is empty"; fi
else
  echo "• private names: skipped (no $names; copy tools/private-patterns.example.txt)"; fail=1
fi
pdfs=$(files | tr '\0' '\n' | grep -iE '\.pdf$' || true)
if [ -n "$pdfs" ]; then echo "✗ PDF files"; echo "$pdfs"; fail=1; else echo "✓ no PDF files"; fi
big=$(files | xargs -0 -I{} find {} -maxdepth 0 -type f -size +1M 2>/dev/null || true)
if [ -n "$big" ]; then echo "✗ files over 1 MB"; echo "$big"; fail=1; else echo "✓ no file over 1 MB"; fi
exit $fail
