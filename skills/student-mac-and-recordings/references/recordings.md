# Class recordings: getting them, transcribing them, using them

A recording is the only record of what was **said** but not written: why a
step is taken, caveats, the instructor's own doubts about an argument,
students' questions, where the class stopped, and announcements such as the
exam range. The notes use it to settle those things; they are not a
transcript of it.

## Where recordings come from

| Source | Seen as | Route |
|---|---|---|
| a course YouTube channel (unlisted, one video per class, titled by date such as `1015`) | a link in chat ("녹음 있어" + URL) | A: yt-dlp on the Mac, Korean auto captions |
| the student's own audio recordings | `.m4a` files in `수업녹음/` | B: whisper.cpp on the Mac |
| a transcript someone else made | text or PDF | read it; treat it as unofficial |

## What did not work, so do not start there

- **The cloud container cannot reach YouTube.** The proxy answers 403 for
  `youtube.com` and `googlevideo.com`. (If the student adds those hosts to the
  environment's allowed domains, route A's command runs in the container.)
- **The device shell has no network.** yt-dlp cannot run there either.
- **Whisper on the container's CPU** (sherpa-onnx int8 builds of large-v3 and
  turbo, from GitHub releases; Hugging Face was blocked) was slow and worse
  than YouTube's captions: it hallucinated repeated phrases and dropped
  syllables. The first attempt spent its time on these routes.

## Route A: a YouTube class video

1. Start a **Remote Control** session on the course folder with instructions
   to run `assets/recordings/fetch-youtube.sh <URL>` (or the same commands
   pasted into the instructions). The script:
   - makes a throwaway virtual environment in the temporary folder and installs
     yt-dlp and certifi there, so nothing stays installed on the Mac;
   - sets `SSL_CERT_FILE` to certifi's bundle (a python.org Python on macOS has
     no root certificates until its "Install Certificates" step is run, and
     yt-dlp fails with `CERTIFICATE_VERIFY_FAILED`);
   - saves the best m4a audio and the Korean auto captions:
     `-f 'bestaudio[ext=m4a]/bestaudio' --write-auto-subs --sub-langs ko`,
     named `<upload date>_<video id>.m4a` / `.ko.vtt`.
2. Stop the Remote Control session when it reports back; the folder tools come
   back.
3. Stage the `.ko.vtt` (the audio stays on the Mac unless something needs it).
4. `vtt-to-text.py --start <class start> file.ko.vtt > raw.md`, then clean it
   (below).

YouTube's Korean auto captions, cleaned with the lecture in hand, were the best
transcript available: better than any local model tried.

## Route B: audio files on the Mac

whisper.cpp runs well on a Mac (it uses the GPU). In a Remote Control session:

1. Once: `brew install whisper-cpp`, and a ggml model. `ggml-large-v3-turbo.bin`
   (about 1.6 GB, from the whisper.cpp model page on Hugging Face) is a good
   balance; ask the student before downloading it.
2. `bash transcribe-mac.sh 수업녹음/<file>.m4a [model]`. The script:
   - converts to 16 kHz mono 16-bit WAV with the built-in `afconvert` (no
     ffmpeg needed);
   - cuts the WAV into **ten-minute slices** (`slice-wav.py`);
   - runs `whisper-cli -l ko -mc 0 -ovtt` on each slice;
   - joins the slices with the right offsets (`vtt-to-text.py --slice 600`)
     into `<file>.whisper.md`.
3. Stage `<file>.whisper.md` and clean it (below).

**`-mc 0` matters.** By default whisper feeds the previous text back in as a
prompt. On a long lecture the decoder then falls into a loop, repeats one
phrase, and silently drops the rest of the audio. `-mc 0` (no context carried
over) prevents it; the slices bound the damage if it happens anyway, make
progress visible, and let a rerun skip finished slices. `vtt-to-text.py` warns
when a line repeats three or more times in a row, or when two minutes or more
have no text: rerun that slice.

## Cleaning a transcript

`vtt-to-text.py` gives paragraphs that start with a timestamp
(`**[12:40]** …`). Then read it **with the handout or handwriting of that class
open**, and:

- fix only misrecognitions the context makes certain: technical terms
  (엔트로피, 르장드르 변환, 깁스–뒤엠), names, symbols read aloud;
- leave what cannot be made out as `[불명확]`; never guess content;
- mark pauses where the instructor writes on the board as `(판서)`. What was
  written is not in the audio: refer to the notes' equation numbers instead of
  inventing it;
- **check numbers and dates** against the handout: captions mishear them,
  and the lecture date matters for the notes;
- find where the class actually starts (the first minutes are often set-up,
  silence or chatter) and pass it as `--start`;
- keep the speaker's words; do not polish them into prose. The summary at the
  top is where the agent's own words go.

## The transcript file

One file per class, `lectures/YYYY-MM-DD-transcript.md` in the project folder
(not in the notes repository, not public). Template:
`assets/recordings/transcript-template.md`. Sections:

1. **Header**: the source (video title and length, or the file name), where
   the class starts in it, how the transcript was made, where the original
   audio and captions are on the Mac.
2. **진도 (progress)**: which handout and which sections of the notes the class
   covered, whether the notes already include it, and announcements (exam
   range, what comes next).
3. **흐름 (timeline)**: a table, time → what was discussed → section or
   equation in the notes ("노트에 없음" where it is not in them).
4. **노트에 없거나 다르게 설명한 부분**: numbered, each with its time: what the
   class said that the notes lack or explain differently. This list is what
   the notes update and exam preparation use.
5. **전사본**: the cleaned transcript, paragraphs with timestamps.

## Using a transcript

- **Where the class stopped.** The notes never run ahead of the class; the
  recording settles where it ended, even when the handout goes further.
- **The order of topics**, when the handwriting is ambiguous.
- **What was said but not written** becomes `remark` or `caution` boxes, or a
  short paragraph, in the notes, in the notes' own words.
- **Gaps.** A class with no handwriting may still have a recording; a class
  with neither is reconstructed from the neighbours (a recap in the past tense
  at the start of the next class is evidence of what came before). See
  `bilingual-lecture-notes/references/materials-and-intake.md`.
- **Exam hints** ("이건 시험에 나와요", "중간고사 범위는 여기까지") go into the
  progress section and into the project memory.

## Privacy

Recordings, captions and transcripts are class material: they stay on the Mac
and in the private project folder. They never go into a public repository,
and the notes repository does not carry them either.
