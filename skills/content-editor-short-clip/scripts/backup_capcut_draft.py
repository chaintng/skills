#!/usr/bin/env python3
"""Create labeled backups for the durable draft set of a CapCut project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def iter_draft_files(draft_dir: Path) -> list[Path]:
    draft_files = [draft_dir / "draft_info.json"]
    draft_files.extend(sorted(draft_dir.glob("Timelines/**/draft_info.json")))
    return [path for path in draft_files if path.is_file()]


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
    draft_files = iter_draft_files(draft_dir)
    if not draft_files:
        raise SystemExit(f"No draft_info.json files found under: {draft_dir}")

    for draft_info in draft_files:
        backup_path = draft_info.with_name(f"{draft_info.name}.{args.label}.bak")
        if backup_path.exists() and not args.force:
            print(str(backup_path))
            continue
        shutil.copy2(draft_info, backup_path)
        print(str(backup_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
