#!/usr/bin/env python3
"""Build a timeline cut plan from subtitle gaps in an SRT file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SRT_BLOCK_RE = re.compile(
    r"(?P<index>\d+)\s+"
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<text>.*?)(?=\n{2,}|\Z)",
    re.DOTALL,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("srt_path", help="Input SRT path")
    parser.add_argument("json_out", help="Output cut plan JSON path")
    parser.add_argument(
        "--min-gap-seconds",
        type=float,
        default=1.0,
        help="Only emit cuts for gaps larger than this threshold",
    )
    parser.add_argument(
        "--pad-seconds",
        type=float,
        default=0.0,
        help="Shrink each cut by padding the left and right edges",
    )
    return parser.parse_args()


def parse_srt_time(value: str) -> int:
    hours, minutes, seconds_ms = value.split(":")
    seconds, ms = seconds_ms.split(",")
    total_ms = (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1000
        + int(ms)
    )
    return total_ms * 1000


def parse_srt(path: Path) -> list[dict[str, int | str]]:
    text = path.read_text(encoding="utf-8")
    items: list[dict[str, int | str]] = []
    for match in SRT_BLOCK_RE.finditer(text):
        items.append(
            {
                "start_us": parse_srt_time(match.group("start")),
                "end_us": parse_srt_time(match.group("end")),
                "text": match.group("text").strip(),
            }
        )
    return items


def main() -> int:
    args = parse_args()
    srt_path = Path(args.srt_path).expanduser()
    entries = parse_srt(srt_path)
    min_gap_us = int(args.min_gap_seconds * 1_000_000)
    pad_us = int(args.pad_seconds * 1_000_000)

    cuts: list[dict[str, int | float]] = []
    for prev, cur in zip(entries, entries[1:]):
        gap_start = int(prev["end_us"]) + pad_us
        gap_end = int(cur["start_us"]) - pad_us
        gap_duration = gap_end - gap_start
        if gap_duration < min_gap_us:
            continue
        cuts.append(
            {
                "start_us": gap_start,
                "end_us": gap_end,
                "duration_us": gap_duration,
                "duration_seconds": round(gap_duration / 1_000_000, 3),
                "reason": "caption-gap",
                "before_text": prev["text"],
                "after_text": cur["text"],
            }
        )

    out_path = Path(args.json_out).expanduser()
    out_path.write_text(json.dumps(cuts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cuts": len(cuts)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
