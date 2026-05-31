---
name: content-publisher
description: Sync public-facing artifacts from local Codex and markdown-content sources into publishable repositories. Use when the user wants to mirror personal Codex skills under ~/.codex/skills/chaintng into a public skills repo, sync markdown blog content into a blog repo, or preview those syncs with dry runs before committing and pushing manually.
---

# Content Publisher

Sync the user's public outputs from their live local sources into the publish repos.

## What This Skill Covers

Use the bundled Python scripts to run these sync flows:

- `sync_skills.py`: sync `~/.codex/skills/chaintng/` into `$TARGET_SKILLS_REPO/skills/`
- `sync_blogs.py`: sync markdown blog sources into `$TARGET_BLOGS_REPO/content/` while excluding drafts and private or hidden notes

## Commands

Run from anywhere:

```bash
python3 "$HOME/.codex/skills/chaintng/content-publisher/scripts/sync_skills.py"
python3 "$HOME/.codex/skills/chaintng/content-publisher/scripts/sync_blogs.py"
```

Preview with:

```bash
python3 "$HOME/.codex/skills/chaintng/content-publisher/scripts/sync_skills.py" --dry-run
python3 "$HOME/.codex/skills/chaintng/content-publisher/scripts/sync_blogs.py" --dry-run
```

## Workflow

1. Run `--dry-run` first if the user wants to inspect changes.
2. Run the requested sync script.
3. Check `git status` in the target repo after the sync.
4. Let the user review before commit and push unless they explicitly ask you to publish.

## Skills Sync Contract

Source:

```text
$HOME/.codex/skills/chaintng
```

Target:

```text
$TARGET_SKILLS_REPO/skills
```

This sync mirrors only the `chaintng` namespace, not every local skill.

## Blogs Sync Contract

Source:

```text
$SOURCE_MARKDOWN_BLOGS_DIR
```

Target:

```text
$TARGET_BLOGS_REPO/content
```

The blogs sync excludes markdown notes when:

- `draft: true`
- tags include `private`
- tags include `hidden`

Non-markdown assets are still synced.

Example source setup:
- Obsidian can be one source for `SOURCE_CONTENT_ROOT`
- but the script only requires a markdown-content directory layout, not Obsidian specifically

## Local Config

Keep machine-specific paths out of git.

If the publish project already has a local `.env` file, load that project-local `.env` into the current shell before running the sync scripts.
Do not use `.env-template`, `.env.example`, or any template file as the runtime source of truth.

Use environment variables such as:

- `SOURCE_SKILLS_DIR`
- `TARGET_SKILLS_REPO`
- `TARGET_SKILLS_DIR`
- `SOURCE_CONTENT_ROOT`
- `SOURCE_MARKDOWN_BLOGS_DIR`
- `TARGET_BLOGS_REPO`
- `TARGET_BLOGS_DIR`

Example load flow:

```bash
set -a
source /path/to/project/.env
set +a
python3 "$HOME/.codex/skills/chaintng/content-publisher/scripts/sync_skills.py" --dry-run
```

## Safety Notes

- Do not auto-commit or auto-push unless the user explicitly asks.
- Prefer `--dry-run` before destructive syncs because the script uses `rsync --delete`.
- If the user has changed the repo layout, inspect the target repo paths before running the sync.
