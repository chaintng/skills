---
name: content-editor-short-clip
description: Use when editing an existing CapCut short-form draft that needs rough-cut A-roll cleanup, subtitle rechunking or light subtitle normalization, or source-backed insert assets without rebuilding the video from scratch.
---

# Content Editor - Short Clip

Use this skill when the user wants Codex to work on a specific CapCut project for short-form content editing.

This skill is for **existing CapCut drafts**, not for creating a video from scratch.

## Scope

This skill covers three modes:

1. Rough-cut cleanup: remove dead air, filler, false starts, repeated takes, and obvious spoken mistakes without reordering the surviving content.
2. Subtitle-only cleanup: rechunk oversized subtitle rows, or do a conservative subtitle-fix pass when the user explicitly asks for typo or spacing correction.
3. Graphics and inserts: coordinate with `content-creator` to gather graphics, charts, illustrations, or attachments from the content source folder and place them on a separate track above the main A-roll.

## Project Rules

- Work on the **exact CapCut project the user names**.
- Do **not** change the user's final A-roll once they say it is final.
- Prefer adding visuals on a separate upper track instead of touching the main track.
- Before any destructive timeline rewrite, create a local backup of the draft JSON.
- Before any draft-file patch, close only the active CapCut project window first if it is open, keep CapCut itself running when possible, patch the files, and then reopen the same project.
- Quit CapCut only as a fallback if closing the working project window is not enough to stop in-memory overwrite behavior.
- At the start of each session, warn the user that this skill is an experimental workflow and can alter CapCut project files.
- Ask the user to confirm they understand the risk before proceeding.
- Ask the user whether they have already created a duplicate backup of the selected project with a `-copy` suffix.

### 0. Mandatory Backup Gate

Before any draft-file change, enforce this order:

1. duplicate the target project folder to a backup project with suffix `-copy`
2. confirm the duplicate path exists before any patch
3. confirm with the user that the `-copy` backup is ready to use

Example:

```text
/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>-copy
```

Only continue after this backup exists and user confirmation is received.

## Primary Tools

Use these in order of preference:

1. `computer-use` for inspecting and operating the live CapCut UI, especially for opening the named draft, generating CapCut captions, checking timeline state, and reopening the project after any patch.
2. Codex in-chat subtitle analysis for semantic false starts, repeated takes, filler, and spoken corrections after the captions already exist on disk.
3. Local draft-file patching when precise repetitive edits are safer than manual UI clicking after the needed caption or cut state already exists on disk.
4. `content-creator` when the user wants source-backed graphics, blog attachments, charts, or insert assets.

If `computer-use` is unavailable, unstable, not actually callable in the current session, or cannot reach the needed CapCut controls, do not silently switch to cloud or external transcription. Fail fast and ask the user to either:

1. generate the captions by hand in CapCut and then resume, or
2. allow or restore the `computer-use` path so the agent can do it in CapCut.

Only continue with file-backed patching when the required caption or timeline state already exists on disk.

## Hard Constraint

- Do not use external transcription services or ad hoc API transcription as a fallback for missing CapCut captions.
- Do not improvise a transcript route just because `computer-use` is awkward.
- If captions are required for the requested cleanup and they do not already exist in the draft, the default action is to use CapCut via `computer-use`.
- If that CapCut path is not available, stop and ask the user to do that caption-generation step manually or to enable the CapCut UI path.
- Do not add a separate project-side API call just to semantically detect false starts when Codex can analyze the extracted subtitles in-chat.

## Bundled Scripts

This skill now includes the repeatable helpers used in the CapCut workflow:

- `scripts/backup_capcut_draft.py`: create labeled `draft_info.json.*.bak` backups for the full durable draft set before any patch.
- `scripts/extract_draft_subtitles.py`: pull generated subtitle timing blocks out of `draft_info.json` into JSON or SRT for inspection.
- `scripts/build_subtitle_span_cuts.py`: turn Codex-selected or user-selected subtitle spans into cut ranges for false starts, filler, repeated takes, and spoken mistakes.
- `scripts/detect_silence_ffmpeg.py`: resolve the first track raw MP4 from `draft_info.json` and detect dead-air ranges from that original media with `ffmpeg` `silencedetect`.
- `scripts/merge_cut_ranges.py`: merge subtitle-derived cuts and silence-derived cuts into one original-timebase cut plan.
- `scripts/make_caption_gap_cuts.py`: derive gap-based cuts from subtitle gaps as a fallback heuristic when direct silence detection is unavailable.
- `scripts/apply_capcut_cuts.py`: apply a cut plan directly to the first CapCut track in the timeline JSON and optionally clear subtitle cache.
- `scripts/rechunk_srt_subtitles.py`: split long subtitle rows into shorter readable chunks before reimport or manual paste-back.

Use `python3` for all of them. `detect_silence_ffmpeg.py` also requires `ffmpeg` on `PATH`.

## First Step

Identify the target project first:

- confirm the exact draft folder name under CapCut projects
- verify whether the user means the original project or a copy
- inspect the current draft structure before editing
- confirm whether `computer-use` is available for CapCut in the current session before promising caption generation or timeline interaction

Typical draft root:

```text
/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/
```

Read at minimum:

- `draft_info.json`
- `draft_info.json.bak` if present
- every `Timelines/**/draft_info.json` if present

Treat the root `draft_info.json` plus any nested `Timelines/**/draft_info.json` files as the draft's **durable draft set**.
Do not assume the root file is the only source of truth.
Some CapCut projects reopen by regenerating the root draft from a nested timeline draft on startup.

First inspect with:

```bash
python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/extract_draft_subtitles.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json" \
  --json-out /tmp/<project>-subtitles.json \
  --srt-out /tmp/<project>-subtitles.srt
```

Create the duplicate backup before touching any file:

```bash
cp -R "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>-copy"
```

Before any draft-file patch, after closing the active project window if needed, back up the durable draft set with:

```bash
python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/backup_capcut_draft.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>" \
  --label codex
```

## Editing Workflow

### 1. Stabilize the source of truth

- Inspect the current project duration, track list, and material list.
- Identify the full durable draft set before editing: the root `draft_info.json` plus every nested `Timelines/**/draft_info.json`.
- Compare duration, first-track segment count, subtitle/text track presence, and primary media path across that durable draft set.
- Confirm whether captions already exist in the draft.
- If captions do not exist and the requested edit needs semantic cleanup, use CapCut through `computer-use` to generate them before attempting any rough-cut plan.
- If `computer-use` cannot actually perform that step, stop there and ask the user to generate captions manually or allow the CapCut UI path. Do not substitute an external transcription service.
- Before any file-backed patch, make sure the target project is not open in the CapCut editor. CapCut can keep an in-memory timeline and overwrite patched `draft_info.json` files on autosave.
- Prefer closing only the active project window. Reopen the same project immediately after patching.
- Quit CapCut only if closing the project window is not enough to make the patch durable.
- If the live UI and the durable draft set disagree, close the working project first, then treat the saved draft files as the durable source of truth and reload the same project after patching.
- If the root draft and a nested timeline draft disagree, assume CapCut may rewrite one from the other on startup. Patch and verify the whole durable draft set before reopening the project.
- The rough-cut patcher only edits the first track, which is treated as the main A-roll track.

### 2. Dead air and false starts

Remove:

- silence longer than `0.5s` by default
- obvious false starts
- filler words and restart phrases that do not add meaning
- repeated restart phrases
- obvious spoken mistakes and wrong takes that are clearly represented in subtitle spans

Keep:

- intentional comedic pauses unless the user asks for aggressive pacing
- slang, tone, and punchlines
- the original content order

Cut-budget rule:

- Treat the first merged cut plan as a draft to be measured, not blindly applied.
- Estimate the total removed duration before patching.
- By default, allow the merged plan to remove up to about `80%` of the source duration, as long as the surviving content still preserves the intended order and meaning.
- If the merged plan would remove more than about `80%`, stop and ask the user before patching.

Preferred method:

1. Generate CapCut captions if they do not already exist.
2. Export or derive SRT and JSON subtitle timing from CapCut before any rough cut.
3. Let Codex analyze the extracted subtitle sequence in-chat and produce a structured bad-span selection JSON for false starts, filler, repeated takes, and spoken mistakes.
4. Convert that structured bad-span selection into subtitle-derived cuts with `build_subtitle_span_cuts.py`.
5. Use `ffmpeg` silence detection on the original media for dead air. Resolve that media from the first track material in `draft_info.json`, not from a manually guessed file path.
6. Merge all cut ranges into one original-timebase cut plan.
7. Apply that cut plan once without reordering.

Failure rule:

- If step 1 cannot be completed inside CapCut with `computer-use`, stop and ask the user to do the caption-generation step manually or to allow the CapCut UI path.
- Do not replace step 1 with a transcription API, cloud speech tool, or improvised non-CapCut transcript path unless the user explicitly changes the workflow.
- When subtitles already exist on disk, prefer Codex in-chat semantic analysis over adding a new project-side API call.

Codex subtitle-analysis rule:

- After subtitle extraction, Codex may analyze the subtitle JSON or SRT directly in the session.
- That analysis should emit a structured selection JSON, usually `/tmp/<project>-bad-spans.json`, not freeform timeline edits.
- Prefer exact `start_us` and `end_us` selections when possible.
- Prefer `spoken_index` over raw `index` when you want ordinal matching from extractor output. `extract_draft_subtitles.py` JSON may include empty timing rows, so `spoken_index` counts only non-empty subtitle lines while raw `index` still counts every row.
- Include a short `reason` such as `false-start`, `repeat`, `filler`, or `mistake`.
- Use the existing scripts only after that structured selection file exists.
- Keep the execution boundary deterministic: Codex chooses spans, scripts turn them into cuts, and the patcher applies the cuts.

If patching draft JSON:

- close the project in the CapCut editor first
- keep CapCut itself open if closing only the project window is enough
- back up every file in the durable draft set, not just the root draft
- split the video segments at the cut boundaries
- remove the merged cut spans
- collapse any retained sliver gap shorter than about `0.2s` before patching so the first track does not fill with microscopic keep-clips
- recompute target timeline durations
- keep source order intact
- patch the same merged cut plan into every timeline JSON in the durable draft set that represents the active timeline
- patch only the first track within each patched file, treated as the main A-roll track
- confirm the patched root draft and patched nested timeline drafts now agree on duration and first-track segment count
- reopen the same project after patching
- after reopening, re-check that CapCut did not regenerate the root draft back to its pre-patch shape
- if another cleanup pass is needed, regenerate or re-extract captions and treat that new draft state as a fresh baseline

Timebase rule:

- subtitle-derived cuts and silence-derived cuts must both reference the original uncut timeline for the current pass
- `apply_capcut_cuts.py` must receive the full merged cut list for that pass
- never patch incrementally using already-shifted timestamps from earlier partial cuts

Preferred CLI sequence for rough-cut cleanup:

```bash
timeline_drafts=(
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json"
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/Timelines/<TIMELINE ID>/draft_info.json"
)

# Codex analyzes /tmp/<project>-subtitles.json or .srt in-chat and writes:
# /tmp/<project>-bad-spans.json

python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/build_subtitle_span_cuts.py" \
  /tmp/<project>-subtitles.json \
  /tmp/<project>-bad-spans.json \
  /tmp/<project>-subtitle-cuts.json

python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/detect_silence_ffmpeg.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json" \
  /tmp/<project>-silence-cuts.json \
  --min-silence-seconds 0.5 \
  --noise=-35dB

python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/merge_cut_ranges.py" \
  /tmp/<project>-subtitle-cuts.json \
  /tmp/<project>-silence-cuts.json \
  /tmp/<project>-merged-cuts.json \
  --min-keep-seconds 0.2

python3 - <<'PY'
import json
from pathlib import Path

draft = json.loads(Path("/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json").read_text())
cuts = json.loads(Path("/tmp/<project>-merged-cuts.json").read_text())
source_duration_us = draft["duration"]
removed_us = sum(item["end_us"] - item["start_us"] for item in cuts)
removed_ratio = removed_us / source_duration_us if source_duration_us else 0
print({
    "source_seconds": round(source_duration_us / 1_000_000, 3),
    "removed_seconds": round(removed_us / 1_000_000, 3),
    "removed_ratio": round(removed_ratio, 4),
})
PY

for draft_json in "${timeline_drafts[@]}"; do
  python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/apply_capcut_cuts.py" \
    "$draft_json" \
    /tmp/<project>-merged-cuts.json \
    --backup-label codex.rough-cut \
    --drop-subtitle-cache \
    --min-keep-seconds 0.2
done
```

Start with `--min-silence-seconds 0.5` as the default probe for silence detection.
If that trims breaths, intentional pauses, or otherwise overcuts the draft, raise `--min-silence-seconds` and rebuild the merged cut plan.
If the user wants a tighter pass, lower `--min-silence-seconds` below `0.5`.
Before patching, check the merged cut ratio. By default, the workflow may remove up to about `80%` of the source duration. If it would remove more than about `80%`, stop and ask the user first.

Selection file example for `build_subtitle_span_cuts.py`:

```json
[
  {"spoken_index": 3, "reason": "false-start"},
  {"contains": "เอ่อ", "reason": "filler"},
  {"start_us": 12400000, "end_us": 15100000, "reason": "mistake"}
]
```

Codex analysis guidance for building that selection file:

- Review subtitles in short sequential windows, not isolated lines.
- If you need ordinal matching, use `spoken_index` first and raw `index` only when you intentionally mean the extractor row number.
- When emitting JSON by hand, prefer explicit `start_us` and `end_us` over `index`.
- Mark short restart fragments that are immediately replaced by a fuller phrase.
- Mark repeated openings and partial-then-complete phrases.
- Preserve emphasis, jokes, and intentional repetition unless they are clearly broken takes.
- Prefer conservative cuts when the transcript is ambiguous.
- Emit JSON only for the selection file, not prose mixed with the data.

### 3. Subtitle rebuilding

Use the session's final expected subtitle style:

- chunk by **phrase and meaning**, not arbitrary fixed lengths
- avoid giant subtitle blocks
- avoid splitting in the middle of a Thai word or obvious phrase
- preserve literal subtitle text during chunking; do not paraphrase or reorder words
- preserve spoken tone and punchy wording

Readable defaults:

- target roughly `0.8s` to `3.5s` per subtitle chunk
- one main idea per chunk
- if a sentence is long, split it into adjacent chunks at natural phrase boundaries
- do not cram two unrelated ideas into one subtitle
- keep slang and voice unless the user explicitly asks to normalize language
- when the user requests subtitle fixing, only correct clearly incomplete words or misspellings in-place, never rewrite vocabulary or tone

Use CapCut-generated captions as the raw input. In subtitle-only mode, `scripts/rechunk_srt_subtitles.py` is the mechanical splitter and timing redistributor. Any typo or spacing normalization is a second pass done conservatively in-chat, not by the script.

Choose one subtitle-only mode:

- `rechunk subtitles`: split long rows into shorter phrase-based rows, preserve source text exactly, and redistribute timing across the new rows
- `fix subtitles`: do the same split pass, then apply only conservative surface fixes such as spacing, obvious `AI` token normalization, and clear misspelling or truncated-word repair

If the user asks to **fix subtitle**, **fix subtitles**, or **rechunk subtitles**, do only the subtitle pass:

- extract current subtitle rows from the current draft or use the latest user-provided subtitle source
- run `scripts/rechunk_srt_subtitles.py` first when the rows are oversized
- return a clickable local link to the written SRT file, not only a plain output path
- include a preview of about the first `30` subtitle rows from the fixed SRT in-chat when the subtitle-fix pass completes
- if the SRT has fewer than `30` rows, include the whole fixed subtitle preview
- do not dump the full SRT in-chat when it is much longer than `30` rows unless the user explicitly asks for all rows
- skip `build_subtitle_span_cuts.py`, `detect_silence_ffmpeg.py`, and `merge_cut_ranges.py`
- do not generate any timeline cut plan
- if CapCut UI does not reflect the result, tell the user to download the SRT and add it manually in CapCut

Rules for `rechunk subtitles`:

- preserve the source text exactly
- do not change spelling, casing, spacing, slang, or vocabulary
- split only at natural phrase boundaries

Rules for `fix subtitles`:

- preserve the speaker's vocabulary, tone, and meaning
- allow only light normalization: split or rechunk, insert missing spacing, standardize obvious terms such as `AI`, and fix clear misspellings or incomplete words
- do not paraphrase, summarize, sanitize, or upgrade the language into more formal Thai
- do not invent words that are not supported by the surrounding subtitle context

Allowed subtitle-fix changes:

- split one oversized row into multiple adjacent rows
- move timing boundaries so each row holds one short phrase or idea
- insert spaces that improve readability around obvious phrase breaks
- normalize obvious token forms such as `AI`
- fix clear mistakes such as `สติภาพ` -> `สันติภาพ` or `หุ่นยน` -> `หุ่นยนต์` when the intended word is unambiguous

Disallowed subtitle-fix changes:

- paraphrasing the sentence into cleaner prose
- replacing slang with formal wording
- changing the joke, punchline, or emotional force
- adding new information not already implied by the source subtitles
- rewriting vocabulary just because a different phrasing reads better

Example subtitle-fix transformation:

FROM

```text
77
00:00:00,000 --> 00:00:07,300
ถ้าจับเอไอแต่ละตัวมาอยู่ด้วยกันจะเป็นยังไงวะมันจะเกิดสติภาพเพราะหัวใจไม่มีในหุ่นยนหรือแม่งจะฉิบหา
```

TO

```text
77
00:00:00,000 --> 00:00:03,133
ถ้าจับ AI แต่ละตัวมาอยู่ด้วยกัน จะเป็นยังไงวะ

78
00:00:03,133 --> 00:00:06,066
มันจะเกิดสันติภาพ เพราะหัวใจ ไม่มีในหุ่นยนต์

79
00:00:06,066 --> 00:00:07,300
หรือแม่งจะฉิบหาย
```

What changed:

- split one overloaded row into short phrase-based chunks
- inserted spacing for readability
- preserved the speaker's vocabulary and aggressive tone
- corrected only obvious transcription mistakes and incomplete words

For cleanup passes, always generate the captions before cutting, not after. The subtitle timing is the semantic guide for spoken mistakes and false starts.
For semantic false-start cleanup, the default detector is Codex analyzing those extracted subtitle timings in-chat, not a new API call embedded into the local scripts.

When the generated captions are structurally correct but too long, rechunk them with:

```bash
python3 "$HOME/.codex/skills/chaintng/content-editor-short-clip/scripts/rechunk_srt_subtitles.py" \
  /tmp/<project>-subtitles.srt \
  /tmp/<project>-subtitles.readable.srt \
  --max-seconds 2.0 \
  --max-chars 36
```

Then either reimport the SRT into CapCut or use the output as the text source when rewriting caption rows in the draft.

If a second rough-cut pass is needed after patching:

1. reopen the project
2. regenerate or re-extract subtitles from the newly patched draft
3. build a new merged cut plan from that new baseline
4. patch once again

### 4. Graphics and inserts

When visuals are requested:

- use `content-creator` to research and collect source-backed graphics
- prefer official charts, figures, screenshots, or illustrations from the primary source
- save them into the content-local `attachments/` folder when working inside a content project
- if the user only needs the graphics delivered, place them in the requested attachment folder and stop there

When inserting into CapCut:

- add them on a separate track above the main video
- align them to the matching spoken section using the caption timing
- avoid moving or trimming the main A-roll unless explicitly asked

## Integration with `content-creator`

Use `content-creator` when the user also wants:

- a researched note
- a content-local `attachments/` folder
- charts and illustrations from a source article
- transcript files stored beside the note
- graphics prepared for manual import into CapCut

Expected handoff:

1. `content-creator` builds or updates the content folder.
2. `content-creator` downloads graphics into `attachments/`.
3. `content-editor-short-clip` uses those exact assets as insert material for CapCut or hands them back to the user if manual import is preferred.

Do not scatter assets across unrelated folders when a content-local attachment folder exists.

## Safety Rules

- Never modify a different CapCut draft just because it is newer.
- Do not switch to a `copy` draft except the user-confirmed `-copy` backup workflow from the mandatory session gate.
- Never overwrite the user's final edit decisions after they say a section is final.
- Always create a backup before patching draft JSON.
- Never patch a draft that is still open in the CapCut editor.
- Prefer closing only the active project window instead of quitting CapCut.
- Quit CapCut only if the project window close is not enough to stop overwrite behavior.
- Never assume the root `draft_info.json` is sufficient when `Timelines/**/draft_info.json` exists for the active project.
- Never let the rough-cut patcher rewrite overlay or graphics tracks; patch only the first track.
- If a UI action becomes unreliable, stop clicking and switch to file-backed editing.
- If the missing prerequisite is CapCut-generated captions and `computer-use` cannot complete that step, do not keep pushing forward with unrelated transcription tooling; stop and ask the user for the manual step or permission to restore the UI path.
- After timeline cuts with `apply_capcut_cuts.py --drop-subtitle-cache`, expect to regenerate or reimport subtitles instead of trusting stale auto-caption data.

## Verification

Before finishing:

- confirm the target project path
- confirm backup files exist for every patched member of the durable draft set
- confirm the project was reloaded after patching if CapCut had been open earlier
- confirm the final draft duration looks plausible after edits
- confirm the root draft and any patched `Timelines/**/draft_info.json` agree after the edit
- confirm CapCut startup did not revert the root draft from an unpatched nested timeline draft
- confirm the merged cut plan was built before patching
- confirm the estimated removed-duration ratio was checked before patching
- confirm the merged cut plan does not leave microscopic retained gaps such as sub-`0.2s` slivers between adjacent cuts
- confirm the first track media path was resolved from the draft for silence detection
- confirm subtitle files exist if they were generated
- if the agent stopped because CapCut caption generation was unavailable, say that explicitly instead of claiming partial semantic cleanup
- confirm every inserted asset path exists
- confirm overlays are on a separate upper track when that was requested

## Example Usage

### Tighten a CapCut draft

User intent:

```text
Work on the CapCut project "Dummy" and remove dead air and false starts.
```

Expected behavior:

- inspect the named draft
- use CapCut captions as the primary semantic guide
- export or derive SRT before cutting
- use subtitle spans for false starts and spoken mistakes
- use `ffmpeg` silence detection for dead air starting from the default `0.5s` threshold
- merge all cuts and patch once
- preserve order

### Rebuild readable subtitles

User intent:

```text
Rewrite the generated captions into readable Thai subtitle chunks.
```

Expected behavior:

- derive chunks from the generated captions
- split by phrase
- avoid massive blocks
- preserve tone

### Fix subtitle only

User intent:

```text
Fix subtitle.
```

Expected behavior:

- do not edit the A-roll timeline
- treat current subtitle timing rows as source input, not fixed output boundaries
- split oversized subtitle rows into smaller chunks
- rebalance timings across the new chunks
- if the user said `rechunk`, preserve source text exactly
- if the user said `fix subtitle`, allow only conservative spacing or typo repair without changing vocabulary
- provide a clickable local link to the written SRT file
- show about the first `30` rows of the fixed subtitles in-session as a preview
- keep each source word or phrase intact except explicit typo or incomplete-word correction in `fix subtitle` mode
- if CapCut UI does not reflect the result, guide the user to manually import/download the SRT

### Add source-backed visuals

User intent:

```text
Use content-creator to gather graphics for this reel and put them on a separate track.
```

Expected behavior:

- call `content-creator`
- use assets from the content source `attachments/`
- align inserts to the spoken sections
- do not alter the final A-roll
