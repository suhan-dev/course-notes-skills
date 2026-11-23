#!/bin/bash
# make-sync-bundle.sh — container side of the Mac sync.
#
# Packs the commits the Mac's clone of the notes lacks into one git bundle, so
# that the clone can be brought up to date without network access and without
# deleting anything on the Mac (see ../../references/git-bundle-sync.md).
#
# Usage:  make-sync-bundle.sh <repo dir> <Mac HEAD> [out dir]
#
#   <repo dir>  the container's clone of the notes repository
#   <Mac HEAD>  the commit the Mac's clone is at: on the device,
#               `git -C <notes clone> rev-parse HEAD`
#   [out dir]   where to write the bundle (default: the current directory);
#               in a project thread a folder under /mnt/project-files/, because
#               device_commit_files copies to the device only from there
#
# Writes <out dir>/sync-<short new>.bundle and prints the changed files and the
# one command to run on the device.
set -euo pipefail

REPO="${1:?usage: make-sync-bundle.sh <repo dir> <Mac HEAD> [out dir]}"
OLD_IN="${2:?usage: make-sync-bundle.sh <repo dir> <Mac HEAD> [out dir]}"
OUT="${3:-.}"
OUT="$(cd "$OUT" && pwd)"
cd "$REPO"

# Bring origin/main up to date when a remote is reachable; fine to skip offline.
git fetch -q origin main 2>/dev/null || echo "note: fetch failed, using the local origin/main" >&2
NEW="$(git rev-parse --verify -q refs/remotes/origin/main)" || {
  echo "no origin/main in $REPO" >&2; exit 1; }

OLD="$(git rev-parse --verify -q "$OLD_IN^{commit}")" || {
  echo "the Mac's HEAD $OLD_IN is not in this clone (fetch it, or bundle from an older commit the Mac has)" >&2
  exit 1; }

if [ "$OLD" = "$NEW" ]; then
  echo "the Mac is already at $(git log -1 --format='%h %s' "$NEW")"; exit 0
fi
git merge-base --is-ancestor "$OLD" "$NEW" || {
  echo "$OLD is not an ancestor of origin/main: the Mac has commits the remote lacks; stop and look" >&2
  exit 1; }

B="$OUT/sync-$(git rev-parse --short "$NEW").bundle"
# The bundle carries refs/remotes/origin/main and every object reachable from
# it but not from OLD; OLD is its prerequisite, which the Mac already has.
git bundle create -q "$B" refs/remotes/origin/main "^$OLD"
git bundle verify -q "$B" >/dev/null 2>&1 || { git bundle verify "$B"; exit 1; }

echo "bundle   $B ($(wc -c < "$B" | tr -d ' ') bytes)"
echo "from     $(git log -1 --format='%h %s' "$OLD")"
echo "to       $(git log -1 --format='%h %s' "$NEW")"
echo "commits  $(git rev-list --count "$OLD..$NEW")"
echo "changes:"
git diff --no-renames --name-status "$OLD" "$NEW" | sed 's/^/  /'
cat <<EOF

Next: copy the bundle and apply-bundle-on-mac.sh into the clone's build/
folder on the device (device_commit_files), then in the device shell, from the
clone's root:
  bash build/apply-bundle-on-mac.sh build/$(basename "$B")
EOF
