#!/usr/bin/env python3
"""Merge overlapping cut ranges into one original-timebase cut plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subtitle_cuts_json", help="Subtitle-derived cuts JSON")
    parser.add_argument("silence_cuts_json", help="Silence-derived cuts JSON")
    parser.add_argument("json_out", help="Merged cut JSON output")
    parser.add_argument(
        "--min-keep-seconds",
        type=float,
        default=0.2,
        help="Collapse adjacent cuts when the retained gap between them is shorter than this threshold",
    )
    return parser.parse_args()


def load_cuts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"cut file must contain a JSON array: {path}")
    normalized: list[dict[str, Any]] = []
    for item in data:
        start_us = int(item["start_us"])
        end_us = int(item["end_us"])
        if end_us <= start_us:
            continue
        normalized.append(
            {
                "start_us": start_us,
                "end_us": end_us,
                "reasons": [str(item.get("reason", "cut"))],
            }
        )
    return normalized


def merge_cuts(cuts: list[dict[str, Any]], min_keep_us: int) -> list[dict[str, Any]]:
    cuts = sorted(cuts, key=lambda item: (item["start_us"], item["end_us"]))
    merged: list[dict[str, Any]] = []
    for cut in cuts:
        if not merged:
            merged.append(cut)
            continue
        gap_us = cut["start_us"] - merged[-1]["end_us"]
        if gap_us > min_keep_us:
            merged.append(cut)
            continue
        merged[-1]["end_us"] = max(merged[-1]["end_us"], cut["end_us"])
        merged[-1]["reasons"].extend(cut["reasons"])

    for item in merged:
        item["duration_us"] = item["end_us"] - item["start_us"]
        item["duration_seconds"] = round(item["duration_us"] / 1_000_000, 3)
        unique_reasons = sorted(set(item["reasons"]))
        item["reasons"] = unique_reasons
        item["reason"] = "+".join(unique_reasons)
    return merged


def main() -> int:
    args = parse_args()
    subtitle_path = Path(args.subtitle_cuts_json).expanduser()
    silence_path = Path(args.silence_cuts_json).expanduser()
    json_out = Path(args.json_out).expanduser()

    cuts = load_cuts(subtitle_path) + load_cuts(silence_path)
    merged = merge_cuts(cuts, max(0, int(round(args.min_keep_seconds * 1_000_000))))
    json_out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "cuts": len(merged),
                "min_keep_seconds": args.min_keep_seconds,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
