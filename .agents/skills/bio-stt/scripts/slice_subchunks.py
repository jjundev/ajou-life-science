#!/usr/bin/env python3
"""
Slice a failing STT audio chunk into smaller subchunks and wrap as 1fps MP4,
or merge transcribed subchunks back into a single part file.

Usage:
  # 1. Slice a failing 10-min chunk into 150s subchunks
  python3 slice_subchunks.py slice --input "STT/_temp_1013/1013_생명_part03.mp3" --sub-seconds 150

  # 2. Merge transcribed subchunk markdown files back into part03.md
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

    # 1. Segment audio into subchunks
    sub_pattern = str(target_dir / f"{stem}_sub%02d.mp3")
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
        [f for f in target_dir.iterdir() if re.match(rf"^{re.escape(stem)}_sub\d+\.mp3$", nfc(f.name))],
        key=lambda p: p.name,
    )

    results = []
    # 3. Wrap each subchunk into 1fps MP4
    for sub in sub_files:
        dur = get_duration(str(sub))
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

    print(f"Successfully sliced {in_file.name} into {len(results)} subchunks ({sub_seconds}s each):")
    for r in results:
        print(f"  - [{r['duration']}] Video: {r['mp4']} -> Output: {r['md']}")

    return results


def merge_subchunks(target_dir: str, prefix: str, output_path: str, clean: bool = False) -> str:
    dir_path = Path(target_dir).resolve()
    out_file = Path(output_path).resolve()

    pattern = re.compile(rf"^{re.escape(prefix)}_sub(\d+)\.md$")
    sub_mds = []
    for f in dir_path.iterdir():
        m = pattern.match(nfc(f.name))
        if m:
            sub_mds.append((int(m.group(1)), f))

    if not sub_mds:
        raise FileNotFoundError(f"No matching subchunk markdown files found for prefix {prefix!r} in {dir_path}")

    sub_mds.sort(key=lambda x: x[0])

    contents = []
    for idx, f in sub_mds:
        text = f.read_text(encoding="utf-8").strip()
        # Clean any accidental part headers inside subchunk
        text = re.sub(r"^#+\s*.*?\n", "", text).strip()
        if text:
            contents.append(text)

    merged_text = "\n\n".join(contents).strip() + "\n"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(merged_text, encoding="utf-8")
    print(f"Merged {len(sub_mds)} subchunks into {out_file} ({len(merged_text)} chars)")

    if clean:
        deleted = 0
        clean_pat = re.compile(rf"^{re.escape(prefix)}_sub\d+.*$")
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
    p_slice.add_argument("--sub-seconds", type=int, default=150, help="Subchunk length in seconds (default: 150)")
    p_slice.add_argument("--out-dir", default=None, help="Output directory (default: same as input)")

    # Merge parser
    p_merge = subparsers.add_parser("merge", help="Merge transcribed subchunk markdown files into a single part file")
    p_merge.add_argument("--dir", required=True, help="Directory containing subchunk md files")
    p_merge.add_argument("--prefix", required=True, help="Prefix of the subchunks (e.g. 1013_생명_part03)")
    p_merge.add_argument("--out", required=True, help="Final merged part markdown path")
    p_merge.add_argument("--clean", action="store_true", help="Delete intermediate subchunk files after merge")

    args = parser.parse_args()
    if args.command == "slice":
        slice_chunk(args.input, args.sub_seconds, args.out_dir)
    elif args.command == "merge":
        merge_subchunks(args.dir, args.prefix, args.out, args.clean)


if __name__ == "__main__":
    main()
