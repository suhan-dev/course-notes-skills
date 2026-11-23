#!/bin/bash
# apply-bundle-on-mac.sh — device side of the Mac sync.
#
# Brings the Mac's clone of the notes up to the commit in a bundle made by
# make-sync-bundle.sh, in a shell where git cannot reach GitHub and where
# deleting files is not allowed (the device shell of an agent app, working on a
# folder that also syncs through iCloud Drive). Nothing is deleted: files are
# overwritten in place, removed files are moved aside, and lock files git
# cannot delete are renamed. See ../../references/git-bundle-sync.md.
#
# Usage, from the root of the clone:
#   bash build/apply-bundle-on-mac.sh build/sync-<id>.bundle
#
# Stops without touching the work tree if any file the update changes was
# edited on the Mac since the old commit.
set -euo pipefail

B="${1:?usage: apply-bundle-on-mac.sh <bundle>}"
[ -f "$B" ] || { echo "no such bundle: $B" >&2; exit 1; }
B="$(cd "$(dirname "$B")" && pwd)/$(basename "$B")"

# rename instead of hard link + unlink when git finalises an object or pack;
# no automatic gc or maintenance, which would repack and delete files.
g() { git -c core.createObject=rename -c gc.auto=0 -c maintenance.auto=false "$@"; }

cd "$(g rev-parse --show-toplevel)"
GITDIR="$(g rev-parse --git-dir)"
STAMP="$(date +%Y%m%d-%H%M%S)"

move_lock() {   # a lock git could not delete makes the next git command fail
  if [ -e "$1" ]; then
    mv "$1" "$GITDIR/stale-$(basename "$1")-$STAMP"
    echo "moved leftover lock $1 to $GITDIR/stale-$(basename "$1")-$STAMP"
  fi
}

REF="$(g symbolic-ref -q HEAD)" || { echo "HEAD is detached; stop" >&2; exit 1; }
for l in "$GITDIR/HEAD.lock" "$GITDIR/index.lock" "$GITDIR/$REF.lock"; do move_lock "$l"; done

OLD="$(g rev-parse HEAD)"
g bundle verify -q "$B" >/dev/null 2>&1 || {
  echo "bundle does not apply here (its prerequisite commit is missing):" >&2
  g bundle verify "$B" >&2 || true
  exit 1; }

# 1. Objects and the remote-tracking ref, from the bundle.
g fetch -q --no-write-fetch-head "$B" refs/remotes/origin/main:refs/remotes/origin/main
NEW="$(g rev-parse refs/remotes/origin/main)"
if [ "$NEW" = "$OLD" ]; then echo "already at $(g log -1 --format='%h %s')"; exit 0; fi
g merge-base --is-ancestor "$OLD" "$NEW" || {
  echo "$NEW does not descend from HEAD $OLD; stop (origin/main was updated, nothing else)" >&2; exit 1; }

g --no-optional-locks diff --cached --quiet "$OLD" ||
  echo "warning: the index had staged changes; their content stays in the files"

# 2. Every file the update touches must still be what the old commit has.
conflicts=0
while IFS= read -r -d '' st && IFS= read -r -d '' path; do
  case "$st" in
    A) if [ -e "$path" ] && [ "$(g hash-object "$path")" != "$(g rev-parse "$NEW:$path")" ]; then
         echo "conflict: $path is new in $NEW but already exists on the Mac with other content"; conflicts=1; fi ;;
    M|D) if [ -e "$path" ]; then
           if [ "$(g hash-object "$path")" != "$(g rev-parse "$OLD:$path")" ]; then
             echo "conflict: $path was edited on the Mac"; conflicts=1; fi
         elif [ "$st" = M ]; then
           echo "conflict: $path is missing on the Mac"; conflicts=1; fi ;;
    *) echo "conflict: $path has status $st; handle it by hand"; conflicts=1 ;;
  esac
done < <(g diff -z --no-renames --name-status "$OLD" "$NEW")
if [ "$conflicts" != 0 ]; then
  echo "stopped: work tree untouched; HEAD still $(g rev-parse --short "$OLD"), origin/main $(g rev-parse --short "$NEW")" >&2
  exit 1
fi

# 3. Write the new content in place; move removed files aside.
LEFT="build/sync-leftovers/$(g rev-parse --short "$NEW")"
written=0; moved=0
while IFS= read -r -d '' st && IFS= read -r -d '' path; do
  case "$st" in
    A|M) mkdir -p "$(dirname "$path")"
         g cat-file blob "$NEW:$path" > "$path"
         mode="$(g ls-tree "$NEW" -- "$path" | cut -d' ' -f1)"
         if [ "$mode" = 100755 ]; then chmod +x "$path" 2>/dev/null || echo "warning: chmod +x $path failed"
         else chmod -x "$path" 2>/dev/null || true; fi
         written=$((written + 1)) ;;
    D) if [ -e "$path" ]; then
         mkdir -p "$LEFT/$(dirname "$path")"; mv "$path" "$LEFT/$path"; moved=$((moved + 1)); fi ;;
  esac
done < <(g diff -z --no-renames --name-status "$OLD" "$NEW")
echo "wrote $written file(s); moved $moved removed file(s) to $LEFT"

# 4. Branch, index, stat cache. update-ref takes the old value, so it refuses
# if the branch moved meanwhile.
g update-ref -m "sync: bundle $(basename "$B")" "$REF" "$NEW" "$OLD"
move_lock "$GITDIR/HEAD.lock"          # update-ref locks HEAD too and cannot delete the lock
g read-tree "$NEW"
move_lock "$GITDIR/index.lock"
g update-index -q --refresh >/dev/null 2>&1 || true
move_lock "$GITDIR/index.lock"

# 5. Report.
echo "HEAD     $(g log -1 --format='%h %s')"
dirty="$(g --no-optional-locks status --porcelain --untracked-files=no)"
if [ -z "$dirty" ]; then echo "status   clean"; else echo "status   not clean:"; echo "$dirty" | sed 's/^/  /'; fi
if g fsck --connectivity-only --no-progress >/dev/null 2>&1; then echo "fsck     ok"; else echo "fsck     problems: run git fsck"; fi
echo "leftovers the student may delete:"
ls -d build/sync-*.bundle build/sync-leftovers "$GITDIR"/stale-* "$GITDIR"/objects/pack/tmp_* 2>/dev/null | sed 's/^/  /' || true
