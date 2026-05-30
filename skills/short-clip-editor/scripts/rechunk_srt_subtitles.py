#!/usr/bin/env python3
"""Split long subtitle entries into shorter, more readable chunks."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

SRT_BLOCK_RE = re.compile(
    r"(?P<index>\d+)\s+"
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<text>.*?)(?=\n{2,}|\Z)",
    re.DOTALL,
)

PREFERRED_BREAKS = ["\n", "。", ".", "?", "!", "…", ",", "،", ";", ":"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_srt", help="Input SRT path")
    parser.add_argument("output_srt", help="Output SRT path")
    parser.add_argument("--max-seconds", type=float, default=2.0)
    parser.add_argument("--max-chars", type=int, default=36)
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


def format_srt_time(value_us: int) -> str:
    total_ms = max(0, value_us // 1000)
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def parse_srt(path: Path) -> list[dict[str, int | str]]:
    text = path.read_text(encoding="utf-8")
    entries: list[dict[str, int | str]] = []
    for match in SRT_BLOCK_RE.finditer(text):
        entries.append(
            {
                "start_us": parse_srt_time(match.group("start")),
                "end_us": parse_srt_time(match.group("end")),
                "text": " ".join(line.strip() for line in match.group("text").splitlines()).strip(),
            }
        )
    return entries


def split_text(text: str, max_chars: int, parts: int) -> list[str]:
    text = text.strip()
    if not text:
        return [""]
    if parts <= 1 and len(text) <= max_chars:
        return [text]

    target_parts = max(parts, math.ceil(len(text) / max_chars))
    chunks: list[str] = []
    remaining = text
    remaining_parts = target_parts

    while remaining and remaining_parts > 1:
        target_len = max(1, round(len(remaining) / remaining_parts))
        split_at = min(len(remaining), max_chars, target_len + max_chars // 3)
        candidate = remaining[:split_at]

        best = -1
        for marker in PREFERRED_BREAKS:
            idx = candidate.rfind(marker)
            if idx > best:
                best = idx + len(marker)
        if best <= 0:
            best = candidate.rfind(" ")
            if best > 0:
                best += 1
        if best <= 0:
            best = split_at

        chunk = remaining[:best].strip()
        if not chunk:
            chunk = remaining[:split_at].strip()
            best = len(chunk)
        chunks.append(chunk)
        remaining = remaining[best:].strip()
        remaining_parts -= 1

    if remaining:
        chunks.append(remaining)
    return [chunk for chunk in chunks if chunk]


def rechunk_entry(entry: dict[str, int | str], max_seconds: float, max_chars: int) -> list[dict[str, int | str]]:
    start_us = int(entry["start_us"])
    end_us = int(entry["end_us"])
    text = str(entry["text"]).strip()
    duration_us = end_us - start_us
    target_parts = max(1, math.ceil(duration_us / int(max_seconds * 1_000_000)))
    pieces = split_text(text, max_chars=max_chars, parts=target_parts)
    if len(pieces) == 1:
        return [entry]

    total_chars = sum(max(1, len(piece)) for piece in pieces)
    cursor = start_us
    results: list[dict[str, int | str]] = []
    for index, piece in enumerate(pieces):
        weight = max(1, len(piece)) / total_chars
        if index == len(pieces) - 1:
            piece_end = end_us
        else:
            piece_end = cursor + int(duration_us * weight)
        results.append({"start_us": cursor, "end_us": piece_end, "text": piece})
        cursor = piece_end
    return results


def write_srt(entries: list[dict[str, int | str]], path: Path) -> None:
    lines: list[str] = []
    for index, entry in enumerate(entries, start=1):
        lines.extend(
            [
                str(index),
                f"{format_srt_time(int(entry['start_us']))} --> {format_srt_time(int(entry['end_us']))}",
                str(entry["text"]),
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    entries = parse_srt(Path(args.input_srt).expanduser())
    rechunked: list[dict[str, int | str]] = []
    for entry in entries:
        rechunked.extend(rechunk_entry(entry, max_seconds=args.max_seconds, max_chars=args.max_chars))
    write_srt(rechunked, Path(args.output_srt).expanduser())
    print(f"wrote {len(rechunked)} subtitle rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
