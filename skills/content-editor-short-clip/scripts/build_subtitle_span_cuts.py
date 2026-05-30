#!/usr/bin/env python3
"""Build cut ranges from selected subtitle spans."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SRT_BLOCK_RE = re.compile(
    r"(?P<index>\d+)\s+"
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<text>.*?)(?=\n{2,}|\Z)",
    re.DOTALL,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subtitles_path", help="Subtitle source in .json from extract_draft_subtitles.py or .srt")
    parser.add_argument("selection_json", help="Selection JSON describing bad subtitle spans")
    parser.add_argument("json_out", help="Output JSON for subtitle-derived cuts")
    parser.add_argument(
        "--default-reason",
        default="mistake",
        help="Fallback reason if a selection entry omits one",
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


def load_subtitles(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        subtitles: list[dict[str, Any]] = []
        spoken_index = 0
        for index, item in enumerate(raw, start=1):
            text = str(item.get("text", "")).strip()
            if text:
                spoken_index += 1
            subtitles.append(
                {
                    "index": index,
                    "spoken_index": spoken_index if text else None,
                    "start_us": int(item["start_us"]),
                    "end_us": int(item["end_us"]),
                    "text": text,
                }
            )
        return subtitles

    text = path.read_text(encoding="utf-8")
    subtitles = []
    spoken_index = 0
    for match in SRT_BLOCK_RE.finditer(text):
        subtitle_text = " ".join(line.strip() for line in match.group("text").splitlines()).strip()
        if subtitle_text:
            spoken_index += 1
        subtitles.append(
            {
                "index": int(match.group("index")),
                "spoken_index": spoken_index if subtitle_text else None,
                "start_us": parse_srt_time(match.group("start")),
                "end_us": parse_srt_time(match.group("end")),
                "text": subtitle_text,
            }
        )
    return subtitles


def subtitle_matches(subtitle: dict[str, Any], rule: dict[str, Any]) -> bool:
    if "index" in rule and int(rule["index"]) != int(subtitle["index"]):
        return False
    if "spoken_index" in rule:
        subtitle_spoken_index = subtitle.get("spoken_index")
        if subtitle_spoken_index is None or int(rule["spoken_index"]) != int(subtitle_spoken_index):
            return False
    if "contains" in rule and str(rule["contains"]).lower() not in str(subtitle["text"]).lower():
        return False
    if "equals" in rule and str(rule["equals"]).strip() != str(subtitle["text"]).strip():
        return False
    if "start_us" in rule and int(rule["start_us"]) != int(subtitle["start_us"]):
        return False
    if "end_us" in rule and int(rule["end_us"]) != int(subtitle["end_us"]):
        return False
    return any(key in rule for key in ("index", "spoken_index", "contains", "equals", "start_us", "end_us"))


def build_cuts(
    subtitles: list[dict[str, Any]],
    selections: list[dict[str, Any]],
    default_reason: str,
) -> list[dict[str, Any]]:
    cuts: list[dict[str, Any]] = []
    for selection in selections:
        if "start_us" in selection and "end_us" in selection:
            start_us = int(selection["start_us"])
            end_us = int(selection["end_us"])
            text = str(selection.get("text", "")).strip()
        else:
            matches = [subtitle for subtitle in subtitles if subtitle_matches(subtitle, selection)]
            if not matches:
                continue
            start_us = min(int(match["start_us"]) for match in matches)
            end_us = max(int(match["end_us"]) for match in matches)
            text = " / ".join(match["text"] for match in matches if match["text"])

        if end_us <= start_us:
            continue

        reason = str(selection.get("reason") or default_reason)
        cuts.append(
            {
                "start_us": start_us,
                "end_us": end_us,
                "duration_us": end_us - start_us,
                "duration_seconds": round((end_us - start_us) / 1_000_000, 3),
                "reason": reason,
                "text": text,
            }
        )
    return cuts


def main() -> int:
    args = parse_args()
    subtitles_path = Path(args.subtitles_path).expanduser()
    selection_path = Path(args.selection_json).expanduser()
    json_out = Path(args.json_out).expanduser()

    subtitles = load_subtitles(subtitles_path)
    selections = json.loads(selection_path.read_text(encoding="utf-8"))
    if not isinstance(selections, list):
        raise SystemExit("selection_json must be a JSON array")

    cuts = build_cuts(subtitles, selections, args.default_reason)
    json_out.write_text(json.dumps(cuts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cuts": len(cuts)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
