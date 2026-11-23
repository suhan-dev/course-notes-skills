# Keeping the Mac's clone of the notes current

The course folder on the Mac holds `notes/`, a git clone of the notes
repository: the student opens the PDFs and sources there. After each publish
the clone should be at the published commit, with a clean `git status`.

## Why not `git pull`

Three things stand in the way, all from the device shell the agent app gives
(see `mac-folders.md`):

1. **No network.** The device shell cannot reach GitHub.
2. **No deleting.** git deletes its lock files and replaces tracked files by
   unlinking them. In the connected folder unlinking fails, so `pull`,
   `merge`, `checkout` and `reset` fail or leave `.lock` files that make the
   next git command fail with "File exists".
3. **iCloud Drive.** The folder syncs to iCloud, `.git` included. Whatever git
   leaves half-done is replicated to the student's other Mac.

So the commits travel as a **git bundle** (a file holding the missing objects
and a ref), and the work tree is updated by writing files in place.

## The procedure

It has run unchanged for every sync since the fix described below, twice in
one day when the notes changed often. The two scripts in `assets/sync/` do
exactly these steps and stop at the first surprise.

**In the container** (`make-sync-bundle.sh <repo> <Mac HEAD> <out dir>`):

1. Read the Mac's HEAD: in the device shell,
   `git -C <notes clone> rev-parse HEAD`.
2. `git bundle create sync-<new>.bundle refs/remotes/origin/main ^<Mac HEAD>`:
   everything reachable from the published commit and not from the Mac's.
3. Put the bundle (and the apply script, the first time) into the clone's
   ignored `build/` folder on the Mac: write them under
   `/mnt/project-files/…/mac-sync/`, then `device_commit_files`.

**On the device** (`bash build/apply-bundle-on-mac.sh build/sync-<new>.bundle`,
from the clone's root). Every git command runs with
`-c core.createObject=rename -c gc.auto=0 -c maintenance.auto=false`:

4. Fetch the bundle into the tracking ref, without writing `FETCH_HEAD`:
   ```sh
   git fetch --no-write-fetch-head build/sync-<new>.bundle \
       refs/remotes/origin/main:refs/remotes/origin/main
   ```
5. Check that the new commit descends from HEAD, and that every file the
   update touches is still exactly what the old commit has
   (`git hash-object <file>` against `git rev-parse <old>:<file>`). A file
   that differs was edited on the Mac: stop, touch nothing, ask the student.
6. Write each added or changed file in place:
   `git cat-file blob <new>:<file> > <file>` (create directories with
   `mkdir -p` first; set the executable bit from the tree). Move each removed
   file to `build/sync-leftovers/<new>/` instead of deleting it.
7. Move the branch, then the index:
   ```sh
   git update-ref refs/heads/main <new> <old>   # refuses if main moved meanwhile
   git read-tree <new>                          # index := the new tree
   git update-index -q --refresh                # stat cache, so status is clean
   ```
8. `update-ref` also locks `HEAD` (it writes HEAD's reflog) and cannot delete
   that lock: rename `.git/HEAD.lock` to `.git/stale-HEAD.lock-<date>`, or the
   next git command fails.
9. Check: `git status` clean, `git log -1` shows the published commit,
   `git fsck --connectivity-only` passes. Report the commit and the leftovers
   the student may delete.

## Why `core.createObject=rename`

When git receives a pack, it writes `tmp_pack_*`, `tmp_idx_*` and `tmp_rev_*`
and then finalises each one. By default that is a **hard link** to the final
name (`pack-<hash>.pack`) followed by an **unlink** of the temporary name
(seen with `strace`: `link(tmp_pack_…, pack-….pack)`, `unlink(tmp_pack_…)`).
On the device the unlink fails, so both names stay, pointing at one file.
iCloud Drive does not keep hard links: after two early syncs it dropped the
final names, and `origin/main` pointed at objects that no longer existed
(`fatal: bad object`). With `core.createObject=rename` git renames the
temporary file onto the final name instead: one call, nothing to delete.

`gc.auto=0` and `maintenance.auto=false` stop git from repacking after the
fetch, which would delete loose objects and old packs.

`assets/sync/test-sync.sh` runs the whole procedure on throwaway repositories
under `strace`: the only deletion the apply step attempts is `.git/HEAD.lock`,
which the script then moves aside.

## Why files are written by hand

`checkout` and `merge` replace a file by unlinking it and creating a new one.
Redirecting `git cat-file blob` into the existing file truncates and rewrites
it in place, which the device allows. The check in step 5 makes this safe: a
file is only overwritten when it is byte-for-byte the old commit's version.

## Repairing a clone that points at missing objects

Symptom: `git status` or `git log origin/main` fails with "bad object", or
`.git/objects/pack/` holds `tmp_pack_*` files and an `.idx` without its
`.pack`. That is the state the early syncs left.

1. Find a commit the Mac really has: `git cat-file -e <commit>` for HEAD, then
   older commits from `git log` in the container.
2. Make a bundle from that commit (`make-sync-bundle.sh` with it as the Mac
   HEAD), or a full bundle of `refs/remotes/origin/main` when nothing usable
   is left.
3. Fetch it with the options above (`apply-bundle-on-mac.sh` does), then
   `git fsck --connectivity-only`.
4. Leave the broken temporary files where they are and list them for the
   student; truncating or deleting them was refused as destructive.

## Leftovers

After a sync these are harmless and the student may delete them on the Mac:
`build/sync-*.bundle`, `build/sync-leftovers/`, `.git/stale-*`, and from the
early syncs `.git/objects/pack/tmp_*` and a lone `pack-*.idx`. Name them once
in the report; do not repeat the list every time.

## When this is not needed

- If the student allows deletion for the notes folder
  (`device_request_delete_permission`), git can delete its locks; the network
  is still missing, so the bundle is still the way in, but steps 6–8 could be
  replaced by `git merge --ff-only origin/main`. The procedure above was the
  one used and tested; prefer it.
- A Remote Control session runs on the Mac itself, with its network, so
  `git pull` would work there (not tried). The folder still syncs through
  iCloud, so keep `-c core.createObject=rename` there too.
