#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


HOME = Path.home()

SOURCE_CONTENT_ROOT = Path(os.environ.get("SOURCE_CONTENT_ROOT", HOME / "content-source"))
SOURCE_MARKDOWN_BLOGS_DIR = Path(
    os.environ.get("SOURCE_MARKDOWN_BLOGS_DIR", SOURCE_CONTENT_ROOT / "Personal/my-contents")
)
TARGET_BLOGS_REPO = Path(os.environ.get("TARGET_BLOGS_REPO", HOME / "Projects/public-blogs"))
TARGET_BLOGS_DIR = Path(os.environ.get("TARGET_BLOGS_DIR", TARGET_BLOGS_REPO / "content"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync markdown blog sources into the target repo.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files.",
    )
    return parser.parse_args()


def parse_frontmatter(content: str) -> tuple[str | None, list[str]]:
    if not content.startswith("---"):
        return None, []

    end = content.find("\n---", 3)
    if end == -1:
        return None, []

    frontmatter = content[3:end]

    draft_match = re.search(r"^draft:\s*(.+)$", frontmatter, re.MULTILINE)
    draft = draft_match.group(1).strip().strip("\"'") if draft_match else None

    tags: list[str] = []
    inline_match = re.search(r"^tags:\s*\[([^\]]*)\]", frontmatter, re.MULTILINE)
    if inline_match:
        tags = [t.strip().strip("\"'") for t in inline_match.group(1).split(",") if t.strip()]
    else:
        block_match = re.search(r"^tags:(.*?)(?=^\S|\Z)", frontmatter, re.MULTILINE | re.DOTALL)
        if block_match:
            tags = [t.strip() for t in re.findall(r"^\s*-\s+(.+)$", block_match.group(1), re.MULTILINE)]

    return draft, tags


def build_exclude_list() -> list[str]:
    excluded: list[str] = []

    for path in sorted(SOURCE_MARKDOWN_BLOGS_DIR.rglob("*.md")):
        rel = path.relative_to(SOURCE_MARKDOWN_BLOGS_DIR)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        draft, tags = parse_frontmatter(content)
        is_draft = draft is not None and draft.lower() == "true"
        is_private = any(tag.lower() in ("private", "hidden") for tag in tags)
        if is_draft or is_private:
            excluded.append(str(rel))

    return excluded


def run_rsync(*, dry_run: bool, exclude_from: Path) -> None:
    args = [
        "rsync",
        "-av",
        "--delete",
        "--delete-excluded",
        "--exclude",
        ".DS_Store",
        "--exclude",
        ".git",
        "--exclude-from",
        str(exclude_from),
    ]
    if dry_run:
        args.append("-n")

    args.extend([f"{SOURCE_MARKDOWN_BLOGS_DIR}/", f"{TARGET_BLOGS_DIR}/"])
    subprocess.run(args, check=True)


def main() -> int:
    args = parse_args()

    if not SOURCE_MARKDOWN_BLOGS_DIR.is_dir():
        raise SystemExit(f"Source markdown blogs directory not found: {SOURCE_MARKDOWN_BLOGS_DIR}")

    TARGET_BLOGS_DIR.mkdir(parents=True, exist_ok=True)
    excluded = build_exclude_list()

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        for item in excluded:
            handle.write(f"{item}\n")
        exclude_path = Path(handle.name)

    try:
        print("=== Excluded .md files ===")
        for item in excluded:
            print(item)
        print("==========================")
        print()
        sys.stdout.flush()

        run_rsync(dry_run=args.dry_run, exclude_from=exclude_path)
    finally:
        exclude_path.unlink(missing_ok=True)

    print()
    print("Synced public blogs")
    print(f"Source: {SOURCE_MARKDOWN_BLOGS_DIR}")
    print(f"Target: {TARGET_BLOGS_DIR}")
    if args.dry_run:
        print("Mode: dry-run")

    return 0


if __name__ == "__main__":
    sys.exit(main())
