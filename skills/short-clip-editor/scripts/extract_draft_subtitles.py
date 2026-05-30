#!/usr/bin/env python3
"""Extract subtitle timing blocks from a CapCut draft into JSON or SRT."""

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


def collect_subtitle_blocks(node: Any, results: list[dict[str, Any]]) -> None:
    if isinstance(node, dict):
        if {
            "start_time",
            "end_time",
            "subtitle_cache_info",
        }.issubset(node.keys()) and isinstance(node["start_time"], int) and isinstance(node["end_time"], int):
            raw = node.get("subtitle_cache_info") or ""
            text = ""
            try:
                payload = json.loads(raw) if raw else {}
                sentences = payload.get("sentence_list") or []
                text = "\n".join(
                    (sentence.get("text") or "").strip()
                    for sentence in sentences
                    if (sentence.get("text") or "").strip()
                ).strip()
            except json.JSONDecodeError:
                text = ""

            results.append(
                {
                    "start_us": node["start_time"],
                    "end_us": node["end_time"],
                    "duration_us": node["end_time"] - node["start_time"],
                    "text": text,
                    "is_empty": not bool(text),
                }
            )

        for value in node.values():
            collect_subtitle_blocks(value, results)
    elif isinstance(node, list):
        for item in node:
            collect_subtitle_blocks(item, results)


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
    blocks: list[dict[str, Any]] = []
    collect_subtitle_blocks(data, blocks)
    blocks = dedupe_blocks(blocks)

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
