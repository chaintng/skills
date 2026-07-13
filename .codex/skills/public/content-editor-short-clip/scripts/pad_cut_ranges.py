#!/usr/bin/env python3
"""Shrink cut ranges to preserve head/tail padding around removed spans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cuts_json", help="Input cut plan JSON")
    parser.add_argument("json_out", help="Output padded cut plan JSON")
    parser.add_argument("--padding-seconds", type=float, default=0.2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cuts_path = Path(args.cuts_json).expanduser()
    json_out = Path(args.json_out).expanduser()
    padding_us = max(0, int(round(args.padding_seconds * 1_000_000)))

    cuts: list[dict[str, Any]] = json.loads(cuts_path.read_text(encoding="utf-8"))
    padded: list[dict[str, Any]] = []

    for cut in cuts:
        start_us = int(cut["start_us"]) + padding_us
        end_us = int(cut["end_us"]) - padding_us
        if end_us <= start_us:
            continue

        next_cut = dict(cut)
        next_cut["start_us"] = start_us
        next_cut["end_us"] = end_us
        next_cut["duration_us"] = end_us - start_us
        next_cut["duration_seconds"] = round((end_us - start_us) / 1_000_000, 3)
        next_cut["padding_seconds"] = args.padding_seconds
        padded.append(next_cut)

    json_out.write_text(json.dumps(padded, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "input_cuts": len(cuts),
                "output_cuts": len(padded),
                "padding_seconds": args.padding_seconds,
                "removed_seconds": round(
                    sum(cut["end_us"] - cut["start_us"] for cut in padded) / 1_000_000,
                    3,
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
