#!/bin/bash
# test-sync.sh — exercises make-sync-bundle.sh and apply-bundle-on-mac.sh on
# throwaway repositories: a normal update (modified, added in a new directory,
# removed, made executable, a Korean file name), the "already up to date" case,
# and a file edited on the "Mac", which must stop the update untouched.
# With strace installed it also lists every file the apply step tried to
# delete: on the device those deletions fail, so each one must be a lock the
# script then moves aside.
#
# Usage: bash test-sync.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com
fail() { echo "FAIL: $*"; exit 1; }

git init -q --bare -b main "$T/origin.git"
git clone -q "$T/origin.git" "$T/box" 2>/dev/null
cd "$T/box"
printf 'build/\n' > .gitignore
echo one > notes.tex; mkdir -p docs; echo v1 > docs/manifest.json
echo old > old.txt; echo 가 > 한글.txt; echo 'echo hi' > tool.sh
git add -A; git commit -qm c1; git push -q origin main 2>/dev/null
C1="$(git rev-parse HEAD)"

git clone -q "$T/origin.git" "$T/mac" 2>/dev/null   # the Mac's clone, at C1

echo two > notes.tex; echo v2 > docs/manifest.json; git rm -q old.txt
mkdir -p problems/en; echo p > problems/en/ch1.tex; echo 나 > 한글.txt
chmod +x tool.sh
git add -A; git commit -qm c2
echo three > notes.tex; git commit -qam c3; git push -q origin main 2>/dev/null
C3="$(git rev-parse HEAD)"

# container side
mkdir -p "$T/out"
bash "$HERE/make-sync-bundle.sh" "$T/box" "$C1" "$T/out" > "$T/make.log"
B="$(ls "$T/out"/sync-*.bundle)"
grep -q "commits  2" "$T/make.log" || fail "expected 2 commits in the bundle"

# device side
mkdir -p "$T/mac/build"; cp "$B" "$HERE/apply-bundle-on-mac.sh" "$T/mac/build/"
cd "$T/mac"
RUN=(bash build/apply-bundle-on-mac.sh "build/$(basename "$B")")
if command -v strace >/dev/null; then
  strace -f -qq -e trace=unlink,unlinkat -o "$T/strace.log" "${RUN[@]}" > "$T/apply.log"
else
  "${RUN[@]}" > "$T/apply.log"
fi
cat "$T/apply.log"
[ "$(git rev-parse HEAD)" = "$C3" ] || fail "HEAD is not c3"
[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "status not clean"
[ "$(cat notes.tex)" = three ] && [ "$(cat 한글.txt)" = 나 ] && [ -f problems/en/ch1.tex ] || fail "content"
[ ! -e old.txt ] && [ -f build/sync-leftovers/*/old.txt ] || fail "old.txt not moved aside"
[ -x tool.sh ] || fail "tool.sh not executable"
grep -q "status   clean" "$T/apply.log" && grep -q "fsck     ok" "$T/apply.log" || fail "report"

if [ -f "$T/strace.log" ]; then
  echo "deletions attempted (each would fail on the device):"
  grep -o 'unlink[a-z]*([^"]*"[^"]*"' "$T/strace.log" | sed 's/.*"\(.*\)"/  \1/' | sort | uniq -c
  if grep -o 'unlink[a-z]*([^"]*"[^"]*"' "$T/strace.log" | sed 's/.*"\(.*\)"/\1/' |
     grep -F "$T/mac" | grep -v '\.lock$'; then
    fail "the apply step deleted something other than a lock file"
  fi
fi

# already up to date
bash build/apply-bundle-on-mac.sh "build/$(basename "$B")" | grep -q "already at" || fail "rerun"

# a file edited on the Mac stops the update before anything is written
cd "$T/box"; echo four > notes.tex; git commit -qam c4; git push -q origin main 2>/dev/null
bash "$HERE/make-sync-bundle.sh" "$T/box" "$C3" "$T/out" > /dev/null
B2="$(ls -t "$T/out"/sync-*.bundle | head -1)"
cd "$T/mac"; cp "$B2" build/; echo "edited on the Mac" > notes.tex
if bash build/apply-bundle-on-mac.sh "build/$(basename "$B2")" > "$T/conflict.log" 2>&1; then
  fail "an edited file did not stop the update"
fi
grep -q "conflict: notes.tex was edited on the Mac" "$T/conflict.log" || fail "conflict message"
[ "$(cat notes.tex)" = "edited on the Mac" ] && [ "$(git rev-parse HEAD)" = "$C3" ] || fail "work tree or HEAD touched"

echo "all sync checks passed"
