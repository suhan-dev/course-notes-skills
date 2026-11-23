# The course folder on the student's Mac

The agent works in a cloud container; the course lives on the student's Mac.
This file is how the agent reached that folder, what it found there, and where
it put things back. Tool names are the ones the agent app used (a "device"
toolset); other apps name them differently, but the moves are the same.

## The devices

The student had two Macs on one Apple account:

- **the laptop**, which holds the term folders on its Desktop:
  `~/Desktop/<term>/<course>/`, for example `~/Desktop/26-2/<course name>/`;
- **a second Mac**, which was often the one connected to the agent app while
  the laptop was asleep or away.

The laptop's Desktop syncs to iCloud Drive, so from the second Mac the same
tree is at

```
~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/<term>/<course>/
```

The second Mac's own `~/Desktop` held unrelated folders with similar names;
do not confuse the two. Always list the devices first and use whichever is
reachable; when the laptop is offline, use the iCloud path on the other Mac.

## Getting access

1. `list_devices` (or `get_device_info`): which devices are reachable and
   which folders are already approved. Use a path exactly as listed: the
   approval covers that spelling.
2. `device_list_dir` on a parent shows a names-only skeleton even before
   access is granted: enough to find the folder.
3. `device_request_folder_access` **once**, for the smallest folder that
   covers the task: the course folder for one course, the iCloud `Desktop`
   (or the term folder) when several courses are involved; one grant on the
   iCloud `Desktop` covered every course for the rest of the term.
4. If the student declines or does not answer, ask in words instead of asking
   again.

## Reading

| Need | How |
|---|---|
| see what is there | `device_list_dir` (add `recursive` for a subtree; 2000 entries at most) |
| read a PDF, image or text file | `device_stage_files`: copies it into the container under `/mnt/user-data/uploads/<folder>/<relative path>`; read it there |
| search or count on the device | `device_bash`: `grep`, `find`, `wc` in `$HOME/mnt/<folder>/…` |

- **Cloud-only files.** iCloud keeps some files as placeholders;
  `device_list_dir` marks them `cloudOnly`. Staging downloads them, which
  takes time and disk on the Mac; beyond 5 files or 50 MB the tool asks for an
  acknowledgement. Tell the student first ("녹음 파일 3개, 1.2 GB를 맥에
  내려받습니다").
- **A staged copy is a snapshot.** Before building on a file staged a while
  ago, compare its `mtimeMs` with a fresh `device_list_dir` and stage it again
  if it changed.
- **What the folders hold** (handouts, handwriting, recordings, problem sets,
  past years, the notes clone) and how to read each kind of file:
  `bilingual-lecture-notes/references/materials-and-intake.md`.

## Korean names are NFD

macOS stores Korean file names decomposed (NFD). A name typed in a command
(NFC) does not match the folder, even though both look the same. In
`device_bash`:

```sh
cd "$HOME"/mnt/*/                      # when one folder is mounted
ls -d "$HOME"/mnt/Desktop/<term>/*/    # pick from a listing
```

or find a folder by name whatever its normalisation:

```sh
python3 - "$HOME/mnt/Desktop/<term>" "<course name>" <<'PY'
import os, sys, unicodedata as u
base, want = sys.argv[1], u.normalize('NFC', sys.argv[2])
print(*[os.path.join(base, n) for n in os.listdir(base)
        if u.normalize('NFC', n) == want], sep='\n')
PY
```

The folder tools (`device_list_dir`, `device_stage_files`,
`device_commit_files`) take the device's own path; `device_bash` sees the same
folder at `$HOME/mnt/<folder name>/…`. A path built in one form must be
translated to the other.

## The device shell

`device_bash` is a Linux VM on the student's machine with the approved folders
mounted at `$HOME/mnt/<folder name>`. In the setup used here:

- **No network.** It cannot reach GitHub, YouTube or a package index.
- **No deleting.** `rm`, `rmdir` and `unlink` in a connected folder fail with
  "Operation not permitted" until the student allows deletion for that folder
  (`device_request_delete_permission`, once, with a reason). `mv` within the
  folder works. If deletion is declined, move files into a `_to_delete/`
  folder and tell the student.
- **git is crippled by the same rule.** git deletes its own lock files and
  replaces files by deleting them, so `commit`, `pull`, `stash` leave `.lock`
  files behind and `checkout`, `merge`, `reset` fail. Bring the notes clone up
  to date with a bundle instead: `git-bundle-sync.md`.
- Each call is a fresh `bash -c` with a 2-minute default timeout (3 minutes at
  most): split long jobs, keep intermediate files in the folder.

## Running things on the Mac itself

Anything that needs the network, Homebrew, or the Mac's own tools (yt-dlp,
whisper.cpp, `afconvert`) runs in a **Remote Control** session: a session on
the Mac with the student's tools. Start it on the course folder with plain
instructions; the student may see an approval prompt. While it runs, the
thread's folder access is off; stop it when it reports back, and the folder
tools return. See `recordings.md` for the two jobs it was used for.

## Writing back

The student expects every deliverable on the Mac as well as in the project
folder ("맥에 없는데" once; since then, always). After **every** rebuild:

1. Write the file into the project folder (`/mnt/project-files/<course>/…`):
   `device_commit_files` copies to the device only from there.
2. `device_commit_files` with the device path. For a file that already exists,
   pass the `expectedMtimeMs` from the last staging, so a version the student
   edited is not overwritten; a refusal means: stage again, look, decide.
3. Mention it in the report ("맥 `치팅시트/`에도 넣었습니다").

Where things went in the course folder:

| Deliverable | Place |
|---|---|
| the notes PDFs and sources | `notes/`, the git clone: sync it with a bundle (`git-bundle-sync.md`), never by copying files over it |
| homework answer sheet | `HW<n>/PS<n>-solutions.tex` and `.pdf`, next to the problem set |
| cheat sheet (both editions) | `치팅시트/` |
| derivation summary for one area | a folder named after the area, e.g. `열화학/` |
| textbook problem collection | `<textbook>_연습문제/` |
| keys for past exams | a folder next to the past-years zip, e.g. `예년도_풀이/` |
| mock exams | `모의고사/` |
| recordings and captions | `수업녹음/` (audio stays on the Mac; transcripts live in the project folder) |

Replace the old PDF in place rather than adding `-v2` copies; the student
opens the same file again.

## What not to touch

- The student's own files: handwriting, recordings, problem sets, anything the
  agent did not write. Read them; never edit, rename or move them.
- Anything outside the course folder, even inside an approved parent.
- Leftovers from earlier syncs (`build/sync-*.bundle`, `.git/stale-*`): list
  them in the report for the student to delete; do not try to remove them.
