#!/usr/bin/env python3
"""Create a labeled backup of a CapCut draft_info.json file."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft_dir", help="CapCut project draft directory")
    parser.add_argument(
        "--label",
        default="codex",
        help="Backup label, for example codex, codex.silence-pass, codex.subtitle-split",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the labeled backup if it already exists",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    draft_dir = Path(args.draft_dir).expanduser()
    draft_info = draft_dir / "draft_info.json"
    if not draft_info.is_file():
        raise SystemExit(f"draft_info.json not found: {draft_info}")

    backup_path = draft_dir / f"draft_info.json.{args.label}.bak"
    if backup_path.exists() and not args.force:
        print(str(backup_path))
        return 0

    shutil.copy2(draft_info, backup_path)
    print(str(backup_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
