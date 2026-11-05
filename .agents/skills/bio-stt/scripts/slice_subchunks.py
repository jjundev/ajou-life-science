#!/usr/bin/env python3
"""
Slice a failing STT audio chunk into smaller subchunks and wrap as 1fps MP4,
or merge transcribed subchunks back into a single part file.

Supports tiered slicing:
  - standard: 150s (default for 10-min chunk recovery)
  - micro: 15s (for high-risk CBRN/biosecurity safety filter bypass)

Usage:
  # 1. Tiered slice
  python3 slice_subchunks.py slice --input "STT/_temp_1013/1013_생명_part03.mp3" --tier standard
  python3 slice_subchunks.py slice --input "STT/_temp_1013/1013_생명_part03_sub04.mp3" --tier micro

  # 2. Recursive merge (handles both _subXX.md and _subXX_sYY.md)
  python3 slice_subchunks.py merge --dir "STT/_temp_1013" --prefix "1013_생명_part03" --out "STT/_temp_1013/1013_생명_part03.md" --clean
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)


def get_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ]
    res = run_cmd(cmd)
    return float(res.stdout.strip())


def slice_chunk(input_path: str, sub_seconds: int = 150, out_dir: str | None = None) -> list[dict[str, str]]:
    in_file = Path(input_path).resolve()
    if not in_file.exists():
        raise FileNotFoundError(f"Input file not found: {in_file}")

    target_dir = Path(out_dir).resolve() if out_dir else in_file.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = in_file.stem
    # If stem already has _temp or similar, strip it
    stem = re.sub(r"_temp$", "", stem)

    # If the input file is already a subchunk (ends with _sub\d+), name children _s%02d
    is_subchunk = bool(re.search(r"_sub\d+$", stem))
    if is_subchunk:
        sub_pattern = str(target_dir / f"{stem}_s%02d.mp3")
        file_regex = re.compile(rf"^{re.escape(stem)}_s(\d+)\.mp3$")
    else:
        sub_pattern = str(target_dir / f"{stem}_sub%02d.mp3")
        file_regex = re.compile(rf"^{re.escape(stem)}_sub(\d+)\.mp3$")

    # 1. Segment audio into subchunks
    split_cmd = [
        "ffmpeg", "-y",
        "-i", str(in_file),
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-f", "segment",
        "-segment_time", str(sub_seconds),
        "-segment_start_number", "1",
        "-reset_timestamps", "1",
        sub_pattern,
    ]
    run_cmd(split_cmd)

    # 2. Find generated subchunks
    sub_files = sorted(
        [f for f in target_dir.iterdir() if file_regex.match(nfc(f.name))],
        key=lambda p: int(file_regex.match(nfc(p.name)).group(1)),
    )

    results = []
    # 3. Wrap each subchunk into 1fps MP4
    for sub in sub_files:
        try:
            dur = get_duration(str(sub))
            if dur < 0.5:
                sub.unlink(missing_ok=True)
                continue
        except Exception:
            sub.unlink(missing_ok=True)
            continue

        mp4_path = sub.with_name(f"{sub.stem}_temp.mp4")
        md_path = sub.with_name(f"{sub.stem}.md")

        wrap_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=320x240:r=1",
            "-i", str(sub),
            "-t", str(dur),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",
            str(mp4_path),
            "-loglevel", "error",
        ]
        run_cmd(wrap_cmd)

        results.append({
            "sub_id": sub.stem,
            "mp3": str(sub),
            "mp4": str(mp4_path),
            "md": str(md_path),
            "duration": f"{dur:.1f}s",
        })

    tier_label = "micro (15s)" if sub_seconds == 15 else f"{sub_seconds}s"
    print(f"Successfully sliced {in_file.name} into {len(results)} subchunks ({tier_label} each):")
    for r in results:
        print(f"  - [{r['duration']}] Video: {r['mp4']} -> Output: {r['md']}")

    return results


def merge_subchunks(target_dir: str, prefix: str, output_path: str, clean: bool = False) -> str:
    """
    Merge subchunks and nested micro-chunks into a target markdown file.
    Supports:
      - {prefix}_subXX.md
      - {prefix}_subXX_sYY.md
      - {prefix}_sYY.md
    """
    dir_path = Path(target_dir).resolve()
    out_file = Path(output_path).resolve()

    pat_sub_s = re.compile(rf"^{re.escape(prefix)}_sub(\d+)_s(\d+)\.md$")
    pat_sub = re.compile(rf"^{re.escape(prefix)}_sub(\d+)\.md$")
    pat_s = re.compile(rf"^{re.escape(prefix)}_s(\d+)\.md$")

    collected: dict[tuple[int, int], Path] = {}
    for f in dir_path.iterdir():
        fname = nfc(f.name)
        m2 = pat_sub_s.match(fname)
        if m2:
            collected[(int(m2.group(1)), int(m2.group(2)))] = f
            continue
        m1 = pat_sub.match(fname)
        if m1:
            collected[(int(m1.group(1)), 0)] = f
            continue
        m0 = pat_s.match(fname)
        if m0:
            collected[(0, int(m0.group(1)))] = f
            continue

    if not collected:
        raise FileNotFoundError(f"No matching subchunk markdown files found for prefix {prefix!r} in {dir_path}")

    # Deduplicate: if a subchunk has child micro-chunks (sub_idx, s_idx > 0), use the children
    sub_indices = set(k[0] for k in collected.keys())
    final_keys: list[tuple[int, int]] = []
    for s_idx in sub_indices:
        children = sorted([k for k in collected.keys() if k[0] == s_idx and k[1] > 0])
        if children:
            final_keys.extend(children)
        else:
            final_keys.append((s_idx, 0))

    final_keys.sort()

    contents = []
    for k in final_keys:
        f = collected[k]
        text = f.read_text(encoding="utf-8").strip()
        # Clean any accidental part headers inside subchunk
        text = re.sub(r"^#+\s*.*?\n", "", text).strip()
        if text:
            contents.append(text)

    merged_text = "\n\n".join(contents).strip() + "\n"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(merged_text, encoding="utf-8")
    print(f"Merged {len(final_keys)} subchunk(s) into {out_file} ({len(merged_text)} chars)")

    if clean:
        deleted = 0
        clean_pat = re.compile(rf"^{re.escape(prefix)}(?:_sub\d+|_s\d+).*$")
        for f in dir_path.iterdir():
            if clean_pat.match(nfc(f.name)) and f != out_file:
                try:
                    f.unlink()
                    deleted += 1
                except OSError:
                    pass
        print(f"Cleaned up {deleted} intermediate subchunk files.")

    return str(out_file)


def main():
    parser = argparse.ArgumentParser(description="Subchunk slicer and merger for bio-stt safety recovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Slice parser
    p_slice = subparsers.add_parser("slice", help="Slice an audio chunk into smaller 1fps MP4 subchunks")
    p_slice.add_argument("--input", required=True, help="Input failing mp3 file")
    p_slice.add_argument("--tier", choices=["standard", "micro"], default=None,
                         help="Preset tier: standard (150s) or micro (15s for CBRN/safety bypass)")
    p_slice.add_argument("--sub-seconds", type=int, default=None,
                         help="Subchunk length in seconds (defaults: 150 for standard, 15 for micro)")
    p_slice.add_argument("--out-dir", default=None, help="Output directory (default: same as input)")

    # Merge parser
    p_merge = subparsers.add_parser("merge", help="Merge transcribed subchunk markdown files into a single part file")
    p_merge.add_argument("--dir", required=True, help="Directory containing subchunk md files")
    p_merge.add_argument("--prefix", required=True, help="Prefix of the subchunks (e.g. 1013_생명_part03)")
    p_merge.add_argument("--out", required=True, help="Final merged part markdown path")
    p_merge.add_argument("--clean", action="store_true", help="Delete intermediate subchunk files after merge")

    args = parser.parse_args()
    if args.command == "slice":
        if args.sub_seconds is not None:
            sub_sec = args.sub_seconds
        elif args.tier == "micro":
            sub_sec = 15
        else:
            sub_sec = 150
        slice_chunk(args.input, sub_sec, args.out_dir)
    elif args.command == "merge":
        merge_subchunks(args.dir, args.prefix, args.out, args.clean)


if __name__ == "__main__":
    main()
