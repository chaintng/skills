#!/usr/bin/env python3
"""Extract original subtitle rows from a CapCut draft into JSON or SRT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft_info", help="Path to draft_info.json")
    parser.add_argument("--json-out", help="Write extracted subtitles to JSON")
    parser.add_argument("--srt-out", help="Write extracted subtitles to SRT")
    return parser.parse_args()


def format_srt_time(value_us: int) -> str:
    total_ms = max(0, value_us // 1000)
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def extract_text_payload_text(raw: Any) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    text = payload.get("text")
    return text.strip() if isinstance(text, str) else ""


def collect_original_subtitle_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    materials = data.get("materials")
    tracks = data.get("tracks")
    if not isinstance(materials, dict) or not isinstance(tracks, list):
        return []

    text_materials = materials.get("texts")
    if not isinstance(text_materials, list):
        return []

    subtitle_materials: dict[str, dict[str, Any]] = {}
    for item in text_materials:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "subtitle":
            continue
        material_id = item.get("id")
        if not isinstance(material_id, str) or not material_id:
            continue
        text = (item.get("recognize_text") or "").strip()
        if not text:
            text = extract_text_payload_text(item.get("content"))
        if not text:
            text = extract_text_payload_text(item.get("base_content"))
        subtitle_materials[material_id] = {
            "text": text,
            "recognize_task_id": item.get("recognize_task_id"),
        }

    if not subtitle_materials:
        return []

    rows: list[dict[str, Any]] = []
    for track in tracks:
        if not isinstance(track, dict) or track.get("type") != "text":
            continue
        segments = track.get("segments")
        if not isinstance(segments, list):
            continue
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            material_id = segment.get("material_id")
            material = subtitle_materials.get(material_id)
            if material is None:
                continue
            target_timerange = segment.get("target_timerange")
            if not isinstance(target_timerange, dict):
                continue
            start_us = target_timerange.get("start")
            duration_us = target_timerange.get("duration")
            if not isinstance(start_us, int) or not isinstance(duration_us, int):
                continue
            text = material["text"]
            rows.append(
                {
                    "start_us": start_us,
                    "end_us": start_us + duration_us,
                    "duration_us": duration_us,
                    "text": text,
                    "is_empty": not bool(text),
                    "recognize_task_id": material.get("recognize_task_id") or "",
                }
            )

    return dedupe_blocks(rows)


def dedupe_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[int, int, str]] = set()
    deduped: list[dict[str, Any]] = []
    for block in sorted(blocks, key=lambda item: (item["start_us"], item["end_us"], item["text"])):
        key = (block["start_us"], block["end_us"], block["text"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(block)
    return deduped


def write_srt(blocks: list[dict[str, Any]], path: Path) -> None:
    lines: list[str] = []
    visible_blocks = [block for block in blocks if block["text"]]
    for index, block in enumerate(visible_blocks, start=1):
        lines.extend(
            [
                str(index),
                f"{format_srt_time(block['start_us'])} --> {format_srt_time(block['end_us'])}",
                block["text"],
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    draft_info_path = Path(args.draft_info).expanduser()
    data = json.loads(draft_info_path.read_text(encoding="utf-8"))
    blocks = collect_original_subtitle_rows(data)
    if not blocks:
        raise SystemExit(
            "No original subtitle materials found in materials.texts with matching text-track segments"
        )

    if args.json_out:
        Path(args.json_out).expanduser().write_text(
            json.dumps(blocks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.srt_out:
        write_srt(blocks, Path(args.srt_out).expanduser())

    print(json.dumps({"subtitle_blocks": len(blocks)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
