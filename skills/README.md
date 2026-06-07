# chaintng/skills

> ⚠️ CAUTION 
> 
> This skill is experimental. 
> 
> DO BACKUP your CapCut project before use.
> 
> Use it at your own RISK.

## Layout

```text
skills/
  content-creator/
  content-editor-short-clip/
  content-publisher/
```

Each skill folder is a self-contained Codex skill with its own:

- `SKILL.md`
- `agents/openai.yaml` when UI metadata is needed
- optional `scripts/`, `references/`, or `assets/`

## Current Skills

### `content-creator`

Create researched content using the `Personal/my-contents/{YYYY}/{CONTENT-TITLE}/index.md` pattern with local `attachments/` for transcript and graphics.

### `content-editor-short-clip`

Edit an existing CapCut short-form project by rough-cutting A-roll cleanup, tightening captions into readable subtitle chunks, and coordinating with `content-creator` for insert graphics or attachments.

### `content-publisher`

Sync public-facing local artifacts into publish repos.

- `sync_skills.py`: mirror local `chaintng` skills into a public skills repo
- `content-publisher-blogs.py`: sync markdown blog sources into a blog/content repo

## Publishing Flow

The live local source of truth can stay in `~/.codex/skills/chaintng/`.

This repo is the public mirror. Sync into `skills/` first, then review, commit, and push.
