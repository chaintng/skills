# chaintng/skills

Public Codex skills maintained under the `chaintng` namespace.

## Layout

```text
skills/
  create-content/
  sync-public/
```

Each skill folder is a self-contained Codex skill with its own:

- `SKILL.md`
- `agents/openai.yaml` when UI metadata is needed
- optional `scripts/`, `references/`, or `assets/`

## Current Skills

### `create-content`

Create researched content using the `Personal/my-contents/{YYYY}/{CONTENT-TITLE}/index.md` pattern with local `attachments/` for transcript and graphics.

### `sync-public`

Sync public-facing local artifacts into publish repos.

- `sync_public_skills.py`: mirror local `chaintng` skills into a public skills repo
- `sync_public_blogs.py`: sync markdown blog sources into a blog/content repo

## Publishing Flow

The live local source of truth can stay in `~/.codex/skills/chaintng/`.

This repo is the public mirror. Sync into `skills/` first, then review, commit, and push.
