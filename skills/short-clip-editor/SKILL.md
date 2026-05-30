---
name: short-clip-editor
description: Edit a user-specified CapCut short-form project by removing dead air, false starts, and filler; rewriting generated captions into readable subtitle chunks; and coordinating with the create-content skill for graphics, attachments, and insert tracks.
---

# short-clip-editor

Use this skill when the user wants Codex to work on a specific CapCut project for short-form content editing.

This skill is for **existing CapCut drafts**, not for creating a video from scratch.

## Scope

This skill covers three jobs:

1. Remove dead air, false starts, and filler from a CapCut project.
2. Rebuild or refine captions into readable subtitle chunks.
3. Coordinate with `create-content` to gather graphics, charts, illustrations, or attachments from the content source folder and place them on a separate track above the main A-roll.

## Project Rules

- Work on the **exact CapCut project the user names**.
- Do **not** change the user's final A-roll once they say it is final.
- Prefer adding visuals on a separate upper track instead of touching the main track.
- Before any destructive timeline rewrite, create a local backup of the draft JSON.

## Primary Tools

Use these in order of preference:

1. `computer-use` for inspecting the live CapCut UI when the runtime works.
2. Local draft-file patching when precise repetitive edits are safer than manual UI clicking.
3. `create-content` when the user wants source-backed graphics, blog attachments, charts, or insert assets.

If `computer-use` is unavailable or unstable, do not block. Patch the CapCut draft files directly and then reload CapCut.

## Bundled Scripts

This skill now includes the repeatable helpers used in the CapCut workflow:

- `scripts/backup_capcut_draft.py`: create a labeled `draft_info.json.*.bak` backup before any patch.
- `scripts/extract_draft_subtitles.py`: pull generated subtitle timing blocks out of `draft_info.json` into JSON or SRT for inspection.
- `scripts/make_caption_gap_cuts.py`: derive silence cut ranges from subtitle gaps in an SRT file.
- `scripts/apply_capcut_cuts.py`: apply a cut plan directly to the CapCut timeline JSON and optionally clear subtitle cache.
- `scripts/rechunk_srt_subtitles.py`: split long subtitle rows into shorter readable chunks before reimport or manual paste-back.

Use `python3` for all of them. They only rely on the Python standard library.

## First Step

Identify the target project first:

- confirm the exact draft folder name under CapCut projects
- verify whether the user means the original project or a copy
- inspect the current draft structure before editing

Typical draft root:

```text
/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/
```

Read at minimum:

- `draft_info.json`
- `draft_info.json.bak` if present
- `Timelines/**/draft_info.json` if present

First inspect or back up with:

```bash
python3 "$HOME/.codex/skills/chaintng/short-clip-editor/scripts/backup_capcut_draft.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>" \
  --label codex

python3 "$HOME/.codex/skills/chaintng/short-clip-editor/scripts/extract_draft_subtitles.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json" \
  --json-out /tmp/<project>-subtitles.json \
  --srt-out /tmp/<project>-subtitles.srt
```

## Editing Workflow

### 1. Stabilize the source of truth

- Inspect the current project duration, track list, and material list.
- Confirm whether captions already exist in the draft.
- If the live UI and the draft JSON disagree, treat the saved draft files as the durable source of truth and reload CapCut after patching.

### 2. Dead air and false starts

Remove:

- silence longer than `1.0s`
- obvious false starts
- repeated restart phrases
- filler that does not add meaning when the user asks for tightening

Keep:

- intentional comedic pauses unless the user asks for aggressive pacing
- slang, tone, and punchlines
- the original content order

Preferred method:

1. Generate CapCut captions if they do not already exist.
2. Use caption timing and phrase repetition to find false starts and repeated takes.
3. Use silence detection for internal dead air.
4. Apply cuts without reordering.

If patching draft JSON:

- split the video segments at the cut boundaries
- remove the silent or false-start spans
- recompute target timeline durations
- keep source order intact

Preferred CLI sequence for silence cleanup from captions:

```bash
python3 "$HOME/.codex/skills/chaintng/short-clip-editor/scripts/make_caption_gap_cuts.py" \
  /tmp/<project>-subtitles.srt \
  /tmp/<project>-cuts.json \
  --min-gap-seconds 1.0

python3 "$HOME/.codex/skills/chaintng/short-clip-editor/scripts/apply_capcut_cuts.py" \
  "/Users/<user>/Movies/CapCut/User Data/Projects/com.lveditor.draft/<PROJECT NAME>/draft_info.json" \
  /tmp/<project>-cuts.json \
  --backup-label codex.silence-pass \
  --drop-subtitle-cache
```

For a tighter pass, lower `--min-gap-seconds` to `0.5` or `0.35`, but that risks trimming breaths and intentional pauses.

### 3. Subtitle rebuilding

Use the session's final expected subtitle style:

- chunk by **phrase and meaning**, not arbitrary fixed lengths
- avoid giant subtitle blocks
- avoid splitting in the middle of a Thai word or obvious phrase
- prefer short readable chunks over literal raw transcripts
- preserve spoken tone and punchy wording

Readable defaults:

- target roughly `0.8s` to `3.5s` per subtitle chunk
- one main idea per chunk
- if a sentence is long, split it into adjacent chunks at natural phrase boundaries
- do not cram two unrelated ideas into one subtitle
- keep slang and voice unless the user explicitly asks to normalize language

When two output styles are useful, prefer:

- a `readable` version
- a `readable-phrased` version with tighter semantic phrase grouping

Use CapCut-generated captions as the raw input, then rewrite timing/text into the cleaner output.

When the generated captions are structurally correct but too long, rechunk them with:

```bash
python3 "$HOME/.codex/skills/chaintng/short-clip-editor/scripts/rechunk_srt_subtitles.py" \
  /tmp/<project>-subtitles.srt \
  /tmp/<project>-subtitles.readable.srt \
  --max-seconds 2.0 \
  --max-chars 36
```

Then either reimport the SRT into CapCut or use the output as the text source when rewriting caption rows in the draft.

### 4. Graphics and inserts

When visuals are requested:

- use `create-content` to research and collect source-backed graphics
- prefer official charts, figures, screenshots, or illustrations from the primary source
- save them into the content-local `attachments/` folder when working inside a content project
- if the user only needs the graphics delivered, place them in the requested attachment folder and stop there

When inserting into CapCut:

- add them on a separate track above the main video
- align them to the matching spoken section using the caption timing
- avoid moving or trimming the main A-roll unless explicitly asked

## Integration with `create-content`

Use `create-content` when the user also wants:

- a researched note
- a content-local `attachments/` folder
- charts and illustrations from a source article
- transcript files stored beside the note
- graphics prepared for manual import into CapCut

Expected handoff:

1. `create-content` builds or updates the content folder.
2. `create-content` downloads graphics into `attachments/`.
3. `short-clip-editor` uses those exact assets as insert material for CapCut or hands them back to the user if manual import is preferred.

Do not scatter assets across unrelated folders when a content-local attachment folder exists.

## Safety Rules

- Never modify a different CapCut draft just because it is newer.
- Never switch to a `copy` draft without explicit user instruction.
- Never overwrite the user's final edit decisions after they say a section is final.
- Always create a backup before patching draft JSON.
- If a UI action becomes unreliable, stop clicking and switch to file-backed editing.
- After timeline cuts with `apply_capcut_cuts.py --drop-subtitle-cache`, expect to regenerate or reimport subtitles instead of trusting stale auto-caption data.

## Verification

Before finishing:

- confirm the target project path
- confirm the backup file exists if draft JSON was patched
- confirm the final draft duration looks plausible after edits
- confirm subtitle files exist if they were generated
- confirm every inserted asset path exists
- confirm overlays are on a separate upper track when that was requested

## Example Usage

### Tighten a CapCut draft

User intent:

```text
Work on the CapCut project "Emergence World" and remove dead air and false starts.
```

Expected behavior:

- inspect the named draft
- use CapCut captions as the primary guide
- cut silence over `1s`
- remove repeated starts
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

### Add source-backed visuals

User intent:

```text
Use create-content to gather graphics for this reel and put them on a separate track.
```

Expected behavior:

- call `create-content`
- use assets from the content source `attachments/`
- align inserts to the spoken sections
- do not alter the final A-roll
