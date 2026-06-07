#!/usr/bin/env python3
"""Split long subtitle entries into shorter, more readable chunks."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

THAI_CHAR_RE = re.compile(r"[\u0E00-\u0E7F]")
SRT_BLOCK_RE = re.compile(
    r"(?P<index>\d+)\s+\r?\n"
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2},\d{3})\s+\r?\n"
    r"(?P<text>.*?)(?=\n{2,}|\Z)",
    re.DOTALL,
)

PREFERRED_BREAKS = ["\n", "。", ".", "?", "!", "…", ",", "،", ";", ":"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_subtitles", help="Input subtitle path (.srt or .json)")
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
                "text": "\n".join(line.strip() for line in match.group("text").splitlines()).strip(),
            }
        )
    return entries


def parse_json(path: Path) -> list[dict[str, int | str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("input_subtitles must be .srt or .json subtitle array")

    entries: list[dict[str, int | str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        entries.append(
            {
                "start_us": int(item["start_us"]),
                "end_us": int(item["end_us"]),
                "text": str(item.get("text", "")).strip(),
            }
        )
    return entries


def load_subtitles(path: Path) -> list[dict[str, int | str]]:
    if path.suffix.lower() == ".json":
        return parse_json(path)
    if path.suffix.lower() == ".srt":
        return parse_srt(path)
    raise SystemExit("input_subtitles must be .srt or .json")


def contains_thai(text: str) -> bool:
    return bool(THAI_CHAR_RE.search(text))


def estimate_chunk_count(text: str, duration_us: int, max_part_us: int, max_chars: int) -> int:
    text_len = len(text)
    if text_len <= 0 or duration_us <= 0:
        return 1

    char_parts = max(1, math.ceil(text_len / max_chars))
    if char_parts <= 1:
        return 1

    time_parts = max(1, math.ceil(duration_us / max_part_us))
    # Split long lines by time only when they have enough text to remain readable.
    # This keeps short lines (including Thai text) from breaking into characters.
    return max(char_parts, min(time_parts, char_parts * 2))


def find_breakpoint(candidate: str, max_chars: int) -> int:
    best = -1
    for marker in PREFERRED_BREAKS:
        idx = candidate.rfind(marker)
        if idx > best:
            best = idx + len(marker)
    if best > 0:
        return best

    best = candidate.rfind(" ")
    if best > 0:
        return best + 1

    if contains_thai(candidate):
        return -1

    return min(len(candidate), max_chars)


def split_text(text: str, max_chars: int, target_parts: int) -> list[str]:
    text = text.strip()
    if not text:
        return [""]
    if target_parts <= 1:
        return [text]

    chunks: list[str] = []
    remaining = text
    remaining_parts = max(1, target_parts)

    while remaining and len(chunks) < remaining_parts - 1:
        target_len = max(1, math.ceil(len(remaining) / remaining_parts))
        split_at = min(len(remaining), max_chars, target_len + max_chars // 3)

        candidate = remaining[:split_at]
        best = find_breakpoint(candidate, max_chars)
        if best <= 0:
            break

        chunk = candidate[:best].strip()
        if not chunk:
            chunk = candidate.strip()
            best = len(candidate)

        chunks.append(chunk)
        remaining = remaining[best:].strip()
        remaining_parts -= 1

    if remaining:
        chunks.append(remaining)

    chunks = [chunk for chunk in chunks if chunk]
    if not chunks:
        return [""]

    # Expand if still too few chunks for caller-requested time slicing.
    # For Thai-heavy text, prefer fewer chunks over blind mid-word splits.
    while len(chunks) < target_parts:
        largest_index = max(range(len(chunks)), key=lambda idx: len(chunks[idx]))
        piece = chunks[largest_index]
        if contains_thai(piece):
            break
        split_mid = max(1, len(piece) // 2)
        if split_mid >= len(piece):
            chunks.append("")
            break
        chunks[largest_index : largest_index + 1] = [piece[:split_mid].strip(), piece[split_mid:].strip()]

    while len(chunks) > target_parts:
        last = chunks.pop()
        if not chunks:
            chunks = [last]
            break
        chunks[-1] = (chunks[-1] + " " + last).strip()

    return chunks


def rechunk_entry(entry: dict[str, int | str], max_seconds: float, max_chars: int) -> list[dict[str, int | str]]:
    start_us = int(entry["start_us"])
    end_us = int(entry["end_us"])
    text = str(entry["text"]).strip()
    duration_us = end_us - start_us

    if duration_us <= 0:
        return [entry]

    if not text:
        return [entry]

    max_part_us = max(1, int(max_seconds * 1_000_000))
    target_parts = estimate_chunk_count(text, duration_us, max_part_us, max_chars)

    pieces = split_text(text, max_chars=max_chars, target_parts=target_parts)
    if len(pieces) <= 1:
        return [entry]

    parts = len(pieces)
    base_us = duration_us // parts
    extra_us = duration_us % parts

    results: list[dict[str, int | str]] = []
    cursor = start_us

    for index, piece in enumerate(pieces):
        is_last = index == parts - 1
        if is_last:
            piece_end = end_us
        else:
            piece_us = base_us + (1 if index < extra_us else 0)
            piece_end = cursor + piece_us
            if piece_end > end_us - (parts - index - 1):
                piece_end = end_us - (parts - index - 1)
            if piece_end - cursor > max_part_us:
                piece_end = cursor + max_part_us
            if piece_end > end_us - (parts - index - 1):
                piece_end = end_us - (parts - index - 1)
            if piece_end <= cursor:
                piece_end = cursor + 1

        results.append(
            {
                "start_us": cursor,
                "end_us": piece_end,
                "text": piece,
            }
        )
        cursor = piece_end

    # Keep all pieces inside the source row boundary.
    for row in results:
        row_start = max(start_us, int(row["start_us"]))
        row_end = min(end_us, int(row["end_us"]))
        if row_end <= row_start:
            row_end = min(end_us, row_start + 1)
        row["start_us"] = row_start
        row["end_us"] = row_end

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
    entries = load_subtitles(Path(args.input_subtitles).expanduser())
    rechunked: list[dict[str, int | str]] = []

    for entry in entries:
        rechunked.extend(rechunk_entry(entry, max_seconds=args.max_seconds, max_chars=args.max_chars))

    write_srt(rechunked, Path(args.output_srt).expanduser())
    print(f"wrote {len(rechunked)} subtitle rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
