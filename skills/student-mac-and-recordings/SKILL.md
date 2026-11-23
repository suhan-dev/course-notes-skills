---
name: student-mac-and-recordings
description: Work with a student's course folder on their Mac from a cloud agent - find it across two Macs and iCloud Drive, read and deliver files, bring the Mac's git clone of the notes up to date with a bundle when the device shell has no network and cannot delete, and turn class recordings (YouTube or m4a) into timestamped transcripts.
---

# The student's Mac and class recordings

The notes are written in a cloud container, but the course lives on the
student's Mac: handouts, handwriting, recordings, problem sets, and a git
clone of the notes the student reads from. This skill covers reaching that
folder, putting deliverables back, keeping the clone at the published commit,
and getting a usable transcript out of a class recording.

## When to use

| Situation | Do |
|---|---|
| the material for a request is only on the Mac ("강의노트 업데이트해" with new handouts in the folder) | find and stage it (`references/mac-folders.md`) |
| a PDF or answer sheet was (re)built | copy it to its place in the course folder, every time |
| the notes were published | sync the Mac's `notes/` clone with a bundle (`references/git-bundle-sync.md`) |
| "녹음 있어" + a link, or m4a files in `수업녹음/` | fetch and transcribe it (`references/recordings.md`) |
| a folder call fails, a name does not match, a git command says "File exists" | read the matching reference before retrying |

## What you get

- `assets/sync/make-sync-bundle.sh`: container side; a bundle of what the Mac
  lacks, with the list of changed files.
- `assets/sync/apply-bundle-on-mac.sh`: device side; fetch, check, write in
  place, move refs and index, rename stuck locks, report. Deletes nothing.
- `assets/sync/test-sync.sh`: runs both on throwaway repositories, under
  `strace` when available.
- `assets/recordings/fetch-youtube.sh`: yt-dlp on the Mac (audio + Korean
  auto captions).
- `assets/recordings/transcribe-mac.sh` and `slice-wav.py`: whisper.cpp on the
  Mac, ten-minute slices, `-mc 0`.
- `assets/recordings/vtt-to-text.py`: captions or slices to timestamped
  paragraphs, with warnings for gaps and repetition loops.
- `assets/recordings/transcript-template.md` and `test-recordings.sh`.

## Steps: reaching the folder

1. List the devices; take a path exactly as listed. If the laptop holding the
   Desktop is offline, use the other Mac's iCloud path
   `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/<term>/<course>/`.
2. Request access once, for the smallest folder that covers the task.
3. Read with `device_list_dir` and `device_stage_files`; tell the student
   before staging many or large cloud-only files.
4. In the device shell, find Korean names by glob or by NFC comparison: the
   Mac stores them as NFD.

## Steps: delivering a rebuilt file

1. Write it to the project folder first (the commit tool copies only from
   there).
2. `device_commit_files` to its place (`references/mac-folders.md` has the
   table), with `expectedMtimeMs` for a file that already exists.
3. Say in the report where it went.

## Steps: syncing the notes clone after a publish

1. Device shell: `git -C <notes clone> rev-parse HEAD`.
2. Container: `make-sync-bundle.sh <repo> <that commit> /mnt/project-files/<course>/mac-sync/`.
3. `device_commit_files` the bundle (and the apply script, once) into the
   clone's `build/`.
4. Device shell, from the clone's root:
   `bash build/apply-bundle-on-mac.sh build/sync-<id>.bundle`.
5. Expect `status clean` and `fsck ok`. A "conflict" line means the student
   edited that file on the Mac: nothing was written; ask before going on.
6. Report the commit the Mac is now at.

## Steps: a recording

1. YouTube: Remote Control session on the course folder →
   `fetch-youtube.sh <URL>` → stop the session → stage the `.ko.vtt`.
   Audio files: Remote Control → `transcribe-mac.sh <file.m4a>` → stage the
   `.whisper.md`.
2. `vtt-to-text.py --start <where class starts> …` for captions.
3. Clean it with the class's handout or handwriting open; fill in the
   template; save it as `lectures/YYYY-MM-DD-transcript.md` in the project
   folder.
4. Use it: where the class stopped, the order of topics, what was said but
   not written, announcements.

## Rules

- **Never `pull`, `checkout`, `merge` or `reset` in the device shell**, and
  run every git command there with `-c core.createObject=rename -c gc.auto=0
  -c maintenance.auto=false`. Without the first, git hard-links new packs and
  cannot unlink the temporary names; iCloud then dropped the real names and
  the clone pointed at missing objects.
- **Overwrite a Mac file only when it is exactly the version you expect**
  (the old commit's blob, or the `mtimeMs` you staged). Otherwise stop and ask.
- **Delete nothing on the Mac.** Move aside (`build/sync-leftovers/`,
  `_to_delete/`, `.git/stale-*`) and list the leftovers for the student once.
- **The student's own files are read-only**: handwriting, recordings, problem
  sets.
- **Deliverables go to the Mac after every rebuild**, replacing the old file,
  and the report says so.
- **Recordings: start with the route that works.** The container cannot reach
  YouTube and the device shell has no network; CPU Whisper in the container
  was worse than YouTube's captions. Use Remote Control on the Mac.
- **whisper.cpp: `-l ko -mc 0`, ten-minute slices.** The default context
  carry-over loops and drops the rest of the lecture.
- **Transcripts: fix only what the context makes certain**; `[불명확]` for the
  rest, `(판서)` for board pauses, equation numbers instead of invented
  formulas; check numbers and dates against the handout.
- **Recordings, captions and transcripts are class material**: Mac and
  private project folder only, never a public repository.
- Ask before a large download on the student's Mac (a 1.6 GB model, many
  cloud-only files).

## Self-check

- [ ] The path used is the one the device listed; the request for access was
      made once.
- [ ] Every rebuilt deliverable is on the Mac, in its folder, and the report
      says where.
- [ ] After a sync: `git log -1` on the Mac shows the published commit,
      `status` is clean, `fsck` passes, no `.lock` file is left under `.git`.
- [ ] A transcript has its start time, progress, timeline, the "not in the
      notes" list, and timestamps every paragraph; no `[불명확]` was replaced
      by a guess.
- [ ] Nothing from the course (audio, captions, transcripts, handouts) went
      anywhere public.
- [ ] After changing a script: `bash assets/sync/test-sync.sh` and
      `bash assets/recordings/test-recordings.sh` pass.

## References

- `references/mac-folders.md`: the two Macs and iCloud, access, reading,
  NFD names, the device shell's limits, Remote Control, where deliverables go.
- `references/git-bundle-sync.md`: the sync procedure step by step, why each
  option is there, the repair of a broken clone, leftovers.
- `references/recordings.md`: sources, the routes that failed, YouTube via
  yt-dlp, whisper.cpp, cleaning, the transcript file, using it.
- `bilingual-lecture-notes/references/materials-and-intake.md`: what the
  course folder holds and how to read each kind of file.
