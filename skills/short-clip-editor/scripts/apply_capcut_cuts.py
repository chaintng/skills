#!/usr/bin/env python3
"""Apply timeline cuts to a CapCut draft_info.json file."""

from __future__ import annotations

import argparse
import copy
import json
import uuid
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft_info", help="Path to draft_info.json")
    parser.add_argument("cuts_json", help="Path to cut plan JSON")
    parser.add_argument(
        "--backup-label",
        default="codex.cuts",
        help="Backup label written before modifying the draft",
    )
    parser.add_argument(
        "--drop-subtitle-cache",
        action="store_true",
        help="Clear generated subtitle caches after retiming to avoid misaligned captions",
    )
    return parser.parse_args()


def merge_cuts(cuts: list[dict[str, Any]]) -> list[tuple[int, int]]:
    pairs = sorted((int(cut["start_us"]), int(cut["end_us"])) for cut in cuts)
    merged: list[tuple[int, int]] = []
    for start, end in pairs:
        if end <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def removed_before(time_us: int, cuts: list[tuple[int, int]]) -> int:
    removed = 0
    for start, end in cuts:
        if end <= time_us:
            removed += end - start
        elif start < time_us:
            removed += time_us - start
            break
        else:
            break
    return removed


def retime_range(start_us: int, end_us: int, cuts: list[tuple[int, int]]) -> tuple[int, int] | None:
    kept_ranges: list[tuple[int, int]] = [(start_us, end_us)]
    for cut_start, cut_end in cuts:
        next_ranges: list[tuple[int, int]] = []
        for part_start, part_end in kept_ranges:
            if cut_end <= part_start or cut_start >= part_end:
                next_ranges.append((part_start, part_end))
                continue
            if part_start < cut_start:
                next_ranges.append((part_start, cut_start))
            if cut_end < part_end:
                next_ranges.append((cut_end, part_end))
        kept_ranges = next_ranges
        if not kept_ranges:
            return None

    new_start = kept_ranges[0][0] - removed_before(kept_ranges[0][0], cuts)
    new_end = kept_ranges[-1][1] - removed_before(kept_ranges[-1][1], cuts)
    if new_end <= new_start:
        return None
    return (new_start, new_end)


def clone_segment(segment: dict[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(segment)
    cloned["id"] = str(uuid.uuid4()).upper()
    return cloned


def split_segment_against_cuts(segment: dict[str, Any], cuts: list[tuple[int, int]]) -> list[dict[str, Any]]:
    target = segment.get("target_timerange") or {}
    start_us = int(target.get("start", 0))
    duration_us = int(target.get("duration", 0))
    end_us = start_us + duration_us

    kept_ranges: list[tuple[int, int]] = [(start_us, end_us)]
    for cut_start, cut_end in cuts:
        next_ranges: list[tuple[int, int]] = []
        for part_start, part_end in kept_ranges:
            if cut_end <= part_start or cut_start >= part_end:
                next_ranges.append((part_start, part_end))
                continue
            if part_start < cut_start:
                next_ranges.append((part_start, cut_start))
            if cut_end < part_end:
                next_ranges.append((cut_end, part_end))
        kept_ranges = next_ranges
        if not kept_ranges:
            return []

    source = segment.get("source_timerange") or {}
    source_start = int(source.get("start", 0))
    speed = float(segment.get("speed", 1.0) or 1.0)
    adjusted: list[dict[str, Any]] = []

    for part_start, part_end in kept_ranges:
        part = segment if len(kept_ranges) == 1 else clone_segment(segment)
        part_duration = part_end - part_start
        new_start = part_start - removed_before(part_start, cuts)
        part["target_timerange"]["start"] = new_start
        part["target_timerange"]["duration"] = part_duration

        if source:
            consumed_before = int(round((part_start - start_us) * speed))
            source_duration = int(round(part_duration * speed))
            part["source_timerange"]["start"] = source_start + consumed_before
            part["source_timerange"]["duration"] = source_duration

        adjusted.append(part)

    return adjusted


def adjust_track_segments(track: dict[str, Any], cuts: list[tuple[int, int]]) -> None:
    segments = track.get("segments")
    if not isinstance(segments, list):
        return

    new_segments: list[dict[str, Any]] = []
    for segment in segments:
        new_segments.extend(split_segment_against_cuts(segment, cuts))
    new_segments.sort(key=lambda item: int(item["target_timerange"]["start"]))
    track["segments"] = new_segments


def strip_subtitle_cache(node: Any, cuts: list[tuple[int, int]]) -> Any:
    if isinstance(node, dict):
        if {
            "start_time",
            "end_time",
            "subtitle_cache_info",
        }.issubset(node.keys()) and isinstance(node["start_time"], int) and isinstance(node["end_time"], int):
            retimed = retime_range(int(node["start_time"]), int(node["end_time"]), cuts)
            if retimed is None:
                return None
            node["start_time"], node["end_time"] = retimed
            node["subtitle_cache_info"] = ""

        cleaned: dict[str, Any] = {}
        for key, value in node.items():
            transformed = strip_subtitle_cache(value, cuts)
            if transformed is None and isinstance(value, dict):
                continue
            if transformed is None and isinstance(value, list):
                cleaned[key] = []
                continue
            cleaned[key] = transformed
        return cleaned

    if isinstance(node, list):
        transformed_list = []
        for item in node:
            transformed = strip_subtitle_cache(item, cuts)
            if transformed is None:
                continue
            transformed_list.append(transformed)
        return transformed_list

    return node


def main() -> int:
    args = parse_args()
    draft_info_path = Path(args.draft_info).expanduser()
    cuts_path = Path(args.cuts_json).expanduser()

    backup_path = draft_info_path.parent / f"draft_info.json.{args.backup_label}.bak"
    if not backup_path.exists():
        backup_path.write_bytes(draft_info_path.read_bytes())

    data = json.loads(draft_info_path.read_text(encoding="utf-8"))
    cuts = merge_cuts(json.loads(cuts_path.read_text(encoding="utf-8")))
    total_removed = sum(end - start for start, end in cuts)

    for track in data.get("tracks", []):
        adjust_track_segments(track, cuts)

    if isinstance(data.get("duration"), int):
        data["duration"] = max(0, data["duration"] - total_removed)

    if args.drop_subtitle_cache:
        data = strip_subtitle_cache(data, cuts)
        config = data.get("config") or {}
        if isinstance(config, dict):
            config["subtitle_sync"] = False

    draft_info_path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cuts_applied": len(cuts),
                "removed_seconds": round(total_removed / 1_000_000, 3),
                "backup": str(backup_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
