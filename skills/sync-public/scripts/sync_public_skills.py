#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


HOME = Path.home()

SOURCE_SKILLS_DIR = Path(os.environ.get("SOURCE_SKILLS_DIR", HOME / ".codex/skills/chaintng"))
TARGET_SKILLS_REPO = Path(os.environ.get("TARGET_SKILLS_REPO", HOME / "Projects/public-skills"))
TARGET_SKILLS_DIR = Path(os.environ.get("TARGET_SKILLS_DIR", TARGET_SKILLS_REPO / "skills"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync public skills into the target repo.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files.",
    )
    return parser.parse_args()


def run_rsync(*, dry_run: bool) -> None:
    args = [
        "rsync",
        "-av",
        "--delete",
        "--exclude",
        ".DS_Store",
        "--exclude",
        ".git",
    ]
    if dry_run:
        args.append("-n")

    args.extend([f"{SOURCE_SKILLS_DIR}/", f"{TARGET_SKILLS_DIR}/"])
    subprocess.run(args, check=True)


def main() -> int:
    args = parse_args()

    if not SOURCE_SKILLS_DIR.is_dir():
        raise SystemExit(f"Source skills directory not found: {SOURCE_SKILLS_DIR}")

    TARGET_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    run_rsync(dry_run=args.dry_run)

    print()
    print("Synced public skills")
    print(f"Source: {SOURCE_SKILLS_DIR}")
    print(f"Target: {TARGET_SKILLS_DIR}")
    if args.dry_run:
        print("Mode: dry-run")

    return 0


if __name__ == "__main__":
    sys.exit(main())
