#!/usr/bin/env python3
"""
Merge segmented STT markdown files into a master transcript for bio-stt.

Outputs to STT/<NAME>.md with header:
# <NAME> 전체 오디오 전사본
## Part 01
...
"""

import argparse
import os
from pathlib import Path
import re
import sys
import unicodedata


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def merge_transcripts(
    target_dir: str,
    prefix: str = "",
    segment_seconds: int = 600,
    keep_parts: bool = False,
    output_file: str = "",
    out_file: str = "",
    timestamps: bool = False,
) -> str:
    target_dir = os.path.abspath(target_dir)
    output_file = output_file or out_file
    pattern = re.compile(rf"^{re.escape(prefix)}.*part(\d+)\.md$" if prefix else r"^.*part(\d+)\.md$")
    timestamp_pattern = re.compile(r"^(\d{1,2}):(\d{2})$")

    part_files = []
    if not os.path.isdir(target_dir):
        print(f"Error: Target directory does not exist: {target_dir}", file=sys.stderr)
        return ""

    for f in os.listdir(target_dir):
        m = pattern.match(nfc(f))
        if m:
            part_files.append((int(m.group(1)), f))

    if not part_files:
        print(f"Error: No matching part markdown files found in {target_dir}", file=sys.stderr)
        return ""

    part_files.sort(key=lambda x: x[0])

    if output_file:
        output_path = os.path.abspath(output_file)
    elif prefix:
        output_path = os.path.join(target_dir, f"{prefix}.md")
    else:
        output_path = os.path.join(target_dir, "transcript.md")

    # Ensure parent dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    full_content = [
        f"# {prefix or os.path.basename(target_dir)} 전체 오디오 전사본\n\n",
    ]

    for part_num, p_file in part_files:
        offset_seconds = (part_num - 1) * segment_seconds
        part_path = os.path.join(target_dir, p_file)
        if timestamps:
            start_min = (part_num - 1) * (segment_seconds // 60)
            full_content.append(f"## Part {part_num:02d} ({start_min:02d}:00 ~ )\n\n")
        else:
            full_content.append(f"## Part {part_num:02d}\n\n")

        with open(part_path, "r", encoding="utf-8") as pf:
            lines = pf.readlines()

        content_lines = []
        skip_header = True
        for line in lines:
            line_str = line.strip()
            if skip_header and (line_str.startswith("#") or not line_str):
                continue
            skip_header = False

            if timestamps:
                tm = timestamp_pattern.match(line_str)
                if tm:
                    mins = int(tm.group(1))
                    secs = int(tm.group(2))
                    total_secs = offset_seconds + (mins * 60) + secs
                    new_mins = total_secs // 60
                    new_secs = total_secs % 60
                    content_lines.append(f"{new_mins:02d}:{new_secs:02d}\n")
                    continue

            content_lines.append(line)

        body = "".join(content_lines).strip()
        if body:
            full_content.append(body + "\n\n")

    result_text = "".join(full_content).strip() + "\n"

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(result_text)

    print(f"Master transcript successfully created: {output_path}")

    # Auto-cleanup of intermediate files unless keep_parts is specified
    if not keep_parts and os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
        cleaned_count = 0
        for f in os.listdir(target_dir):
            fn = nfc(f)
            is_chunk_md = bool(re.search(r"_part\d+\.md$", fn))
            is_chunk_mp3 = bool(re.search(r"_part\d+\.mp3$", fn))
            is_chunk_mp4 = bool(re.search(r"_part\d+_temp\.mp4$", fn))

            if prefix:
                matches_prefix = fn.startswith(prefix)
            else:
                matches_prefix = True

            if matches_prefix and (is_chunk_md or is_chunk_mp3 or is_chunk_mp4):
                try:
                    os.remove(os.path.join(target_dir, f))
                    cleaned_count += 1
                except OSError as e:
                    print(f"Warning: Failed to delete intermediate file {f}: {e}", file=sys.stderr)

        print(f"Cleaned up {cleaned_count} intermediate chunk files.")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Merge segmented transcripts for bio-stt")
    parser.add_argument("--dir", required=True, help="Directory containing part files")
    parser.add_argument("--prefix", default="", help="Prefix of the part files (e.g. 1006 생명)")
    parser.add_argument("--out", default="", help="Final output file path")
    parser.add_argument("--segment-seconds", type=int, default=600, help="Segment length in seconds (default: 600)")
    parser.add_argument("--keep-parts", action="store_true", help="Preserve intermediate part files")
    parser.add_argument("--timestamps", action="store_true", help="Include continuous MM:SS timestamps")

    args = parser.parse_args()
    merge_transcripts(
        target_dir=args.dir,
        prefix=args.prefix,
        segment_seconds=args.segment_seconds,
        keep_parts=args.keep_parts,
        output_file=args.out,
        timestamps=args.timestamps,
    )


if __name__ == "__main__":
    main()
