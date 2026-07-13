---
name: content-editor-short-clip
description: Use when editing an existing CapCut short-form draft for A-roll rough cuts, dead-air cleanup, repeated-take removal, readable subtitle chunking, light subtitle fixes, or source-backed visual inserts without rebuilding the video from scratch.
---

# Content Editor - Short Clip

Use this skill only for existing CapCut drafts. Work on the exact draft folder the user names.

## Modes

- Rough cut: remove dead air, false starts, repeated takes, fillers, and obvious mistakes while preserving content order.
- Subtitle cleanup: use AI/LLM judgment to rewrite generated captions into readable chunks without cutting the A-roll.
- Inserts: gather source-backed graphics with `content-creator` and place them on an upper track.

## Parameters

Ask or infer these when relevant. Defaults are conservative for Thai talking-head short clips.

| Parameter | Default | Meaning |
| --- | ---: | --- |
| `backup_suffix` | `-copy` | Required duplicate CapCut project folder before any patch. |
| `min_silence_seconds` | `0.5` | Minimum silence length to cut from source media. Raise to `0.7-0.9` if cuts feel too aggressive. |
| `silence_noise` | `-35dB` | ffmpeg `silencedetect` noise threshold. |
| `cut_padding_seconds` | `0.2` | Keep this much audio/video before and after every merged cut. This prevents clipped word heads/tails. |
| `min_keep_seconds` | `0.2` | Merge adjacent cuts when the kept gap between them is shorter than this. Prevents tiny leftover slivers. |
| `max_removed_ratio` | `0.8` | Stop and ask before patching if the cut plan removes more than this source-duration ratio. |
| `subtitle_min_seconds` | `0.8` | Prefer not to create subtitle chunks shorter than this unless speech is genuinely short. |
| `subtitle_max_seconds` | `3.5` | Preferred maximum readable subtitle chunk duration. |
| `subtitle_max_chars` | `36` | Soft target. Readability and natural phrase boundaries win over exact character count. |

If the user says the edit clipped word heads/tails, restore the pre-cut backup and rebuild the cut plan with larger `cut_padding_seconds`; do not stack a second cut pass onto an already shifted timeline.

## Safety Gate

Before any draft-file change:

1. Warn that this workflow is experimental and can alter CapCut project files.
2. Confirm the target project folder.
3. Confirm a duplicate folder exists at `<PROJECT>-copy`, or create it and confirm it exists.
4. Close the active CapCut project window before patching. Keep CapCut running when possible.
5. Back up every durable draft file with `scripts/backup_capcut_draft.py`.

Never patch a project that is still open in the CapCut editor. Never modify a different draft because it is newer.

## Durable Draft Set

Treat these as one unit:

- `<PROJECT>/draft_info.json`
- every `<PROJECT>/Timelines/**/draft_info.json`

Inspect and patch all matching active timeline files. Root and nested timeline drafts can overwrite each other on CapCut startup.

Compare before editing:

- duration
- track list and first-track segment count
- text/subtitle segment count
- first-track source media path

## Tools And Constraints

- Prefer `computer-use` for live CapCut operations, especially caption generation and reopening the project.
- Use local draft patching only when the needed captions or timeline state already exists on disk.
- Do not use external transcription or ad hoc speech APIs. If captions are needed and missing, generate them in CapCut or ask the user to do it.
- Use `python3` for bundled scripts. `detect_silence_ffmpeg.py` requires `ffmpeg`.

Bundled scripts:

- `backup_capcut_draft.py`
- `extract_draft_subtitles.py`
- `build_subtitle_span_cuts.py`
- `detect_silence_ffmpeg.py`
- `merge_cut_ranges.py`
- `make_caption_gap_cuts.py`
- `pad_cut_ranges.py`
- `apply_capcut_cuts.py`
- `rechunk_srt_subtitles.py`

## Rough-Cut Workflow

1. Extract CapCut captions from the uncut baseline:

```bash
python3 scripts/extract_draft_subtitles.py \
  "<PROJECT>/draft_info.json" \
  --json-out /tmp/<slug>-subtitles.json \
  --srt-out /tmp/<slug>-subtitles.srt
```

2. Analyze captions in-chat and write `/tmp/<slug>-bad-spans.json`.

Use `spoken_index` for ordinal matching. Prefer exact `start_us`/`end_us` for partial-line mistakes. Mark only clear false starts, repeats, wrong takes, unrelated tail content, and obvious fillers.

3. Build subtitle cuts and silence cuts:

```bash
python3 scripts/build_subtitle_span_cuts.py \
  /tmp/<slug>-subtitles.json \
  /tmp/<slug>-bad-spans.json \
  /tmp/<slug>-subtitle-cuts.json

python3 scripts/detect_silence_ffmpeg.py \
  "<PROJECT>/draft_info.json" \
  /tmp/<slug>-silence-cuts.json \
  --min-silence-seconds 0.5 \
  --noise=-35dB

python3 scripts/merge_cut_ranges.py \
  /tmp/<slug>-subtitle-cuts.json \
  /tmp/<slug>-silence-cuts.json \
  /tmp/<slug>-merged-cuts.raw.json \
  --min-keep-seconds 0.2
```

4. Apply cut padding before patching:

```bash
python3 scripts/pad_cut_ranges.py \
  /tmp/<slug>-merged-cuts.raw.json \
  /tmp/<slug>-merged-cuts.json \
  --padding-seconds 0.2
```

Padding shrinks every merged cut by `cut_padding_seconds` on both sides and discards cuts that become empty.

5. Measure before patching:

- source seconds
- removed seconds
- kept seconds
- removed ratio
- cut count
- smallest retained gap

Stop if `removed_ratio > max_removed_ratio`.

6. Close the CapCut project window, back up the durable draft set, and apply the same padded cut plan to every durable draft file:

```bash
python3 scripts/apply_capcut_cuts.py \
  "<DRAFT_JSON>" \
  /tmp/<slug>-merged-cuts.json \
  --backup-label codex.rough-cut \
  --drop-subtitle-cache \
  --min-keep-seconds 0.2
```

Only the first track is the A-roll track. Do not patch overlay or insert tracks with this script.

## Subtitle Workflow

There is one subtitle cleanup mode. If the user says `fix subtitles`, `fix subtitle`, `rechunk subtitles`, or `chunk subtitle`, treat it as the same request: use AI/LLM judgment to produce readable subtitle chunks from the existing CapCut captions.

Do not use a code-only splitter as the main rewriting step. Use scripts only to extract source captions, inspect timing, or write output files. The actual chunking/fixing decision is done by the LLM in-chat.

Good subtitle output:

- readable
- `0.8s-3.5s` per chunk where possible
- one idea per chunk
- no mid-word Thai splits
- punctuation and spacing should match the original written language; for Thai, prefer phrase spacing and do not add full stops by default
- no paraphrase unless explicitly requested
- keep brand names and borrowed words in their original language when natural, e.g. `CapCut`, `Apple`, `IT`, `Platform`, `Internet`

When splitting a caption row, every child chunk must stay within that parent row's original time span. Redistribute only inside the parent span; never let a split chunk cross into the next source caption's timing.

After a rough cut:

1. Retiming must use the same original-timebase padded cut plan used for A-roll.
2. Remove captions whose source span was fully cut.
3. Retain and retime surviving captions.
4. Use LLM judgment to replace surviving rows with readable phrase chunks, while each child chunk stays within its parent span.
5. Write an SRT beside the project, e.g. `<PROJECT>/<slug>-cleaned-chunked.srt`.
6. Return the SRT as a clickable local file link so the user can download/import it.
7. If CapCut does not reflect direct text-track patching, import the SRT manually in CapCut.

## Recovery Loop

If the result is overcut or clipped:

1. Back up the current edited state with a clear label.
2. Restore from the pre-cut `draft_info.json.codex.rough-cut.bak` files, or the latest known uncut backup.
3. Rebuild the cut plan from the original captions and original timebase.
4. Increase `cut_padding_seconds` first; then consider raising `min_silence_seconds`.
5. Reapply to every durable draft file and rebuild subtitles.

Never patch incrementally using timestamps from an already shifted timeline unless it is a fresh second pass with newly extracted captions.

## Inserts

When visuals are requested:

- Use `content-creator` to gather source-backed assets.
- Save assets into the content-local `attachments/` folder when one exists.
- Add visuals on an upper track.
- Do not trim or move the final A-roll unless explicitly asked.

## Verification

Before finishing, report:

- target project path
- backup folder and `.bak` files created
- source duration, edited duration, removed seconds, removed ratio, cut count, and cut padding
- root and nested timeline duration/segment agreement
- subtitle SRT path and caption row count
- whether CapCut was reopened and whether startup rewrote the files
- whether playback was visually checked or only file-verified
