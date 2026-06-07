#!/usr/bin/env python3
"""Detect silence ranges for the first CapCut track source media with ffmpeg."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9]+(?:\.[0-9]+)?)")
SILENCE_END_RE = re.compile(
    r"silence_end:\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*silence_duration:\s*([0-9]+(?:\.[0-9]+)?)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "draft_info",
        help="Path to CapCut draft_info.json. The script resolves the first track source media automatically.",
    )
    parser.add_argument("json_out", help="Output JSON file for silence cut ranges")
    parser.add_argument("--min-silence-seconds", type=float, default=0.5)
    parser.add_argument("--noise", default="-35dB", help="ffmpeg silencedetect noise threshold")
    parser.add_argument(
        "--pad-seconds",
        type=float,
        default=0.0,
        help="Trim detected silence ranges inward by this amount on both sides",
    )
    return parser.parse_args()


def seconds_to_us(value: float) -> int:
    return int(round(value * 1_000_000))


def resolve_first_track_media_file(draft_info: Path) -> Path:
    data = json.loads(draft_info.read_text(encoding="utf-8"))
    tracks = data.get("tracks") or []
    if not isinstance(tracks, list) or not tracks:
        raise SystemExit("No tracks found in draft_info.json")

    first_track = tracks[0]
    segments = first_track.get("segments") or []
    if not isinstance(segments, list) or not segments:
        raise SystemExit("First track has no segments")

    first_segment = segments[0]
    material_id = first_segment.get("material_id")
    if not material_id:
        raise SystemExit("First track first segment has no material_id")

    materials = data.get("materials") or {}
    videos = materials.get("videos") or []
    if not isinstance(videos, list):
        raise SystemExit("materials.videos missing from draft_info.json")

    for item in videos:
        if not isinstance(item, dict):
            continue
        if item.get("id") != material_id:
            continue
        media_path = item.get("path") or item.get("media_path")
        if not media_path:
            raise SystemExit(f"Video material {material_id} has no path")
        resolved = Path(media_path).expanduser()
        if not resolved.exists():
            raise SystemExit(f"Resolved media file does not exist: {resolved}")
        return resolved

    raise SystemExit(f"Could not find first track material in materials.videos: {material_id}")


def detect_silence(media_file: Path, min_silence_seconds: float, noise: str) -> list[dict[str, float]]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        str(media_file),
        "-af",
        f"silencedetect=noise={noise}:d={min_silence_seconds}",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in (0, 255):
        raise SystemExit(completed.stderr.strip() or "ffmpeg silencedetect failed")

    silence_ranges: list[dict[str, float]] = []
    current_start: float | None = None
    for line in completed.stderr.splitlines():
        start_match = SILENCE_START_RE.search(line)
        if start_match:
            current_start = float(start_match.group(1))
            continue
        end_match = SILENCE_END_RE.search(line)
        if end_match and current_start is not None:
            end_seconds = float(end_match.group(1))
            duration_seconds = float(end_match.group(2))
            silence_ranges.append(
                {
                    "start_seconds": current_start,
                    "end_seconds": end_seconds,
                    "duration_seconds": duration_seconds,
                }
            )
            current_start = None
    return silence_ranges


def main() -> int:
    args = parse_args()
    draft_info = Path(args.draft_info).expanduser()
    json_out = Path(args.json_out).expanduser()
    media_file = resolve_first_track_media_file(draft_info)
    silence_ranges = detect_silence(media_file, args.min_silence_seconds, args.noise)
    pad_seconds = max(0.0, args.pad_seconds)

    cuts: list[dict[str, int | float | str]] = []
    for item in silence_ranges:
        start_seconds = item["start_seconds"] + pad_seconds
        end_seconds = item["end_seconds"] - pad_seconds
        if end_seconds <= start_seconds:
            continue
        duration_seconds = end_seconds - start_seconds
        cuts.append(
            {
                "start_us": seconds_to_us(start_seconds),
                "end_us": seconds_to_us(end_seconds),
                "duration_us": seconds_to_us(duration_seconds),
                "duration_seconds": round(duration_seconds, 3),
                "reason": "silence",
            }
        )

    json_out.write_text(json.dumps(cuts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cuts": len(cuts), "media_file": str(media_file)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
