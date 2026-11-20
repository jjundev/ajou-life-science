#!/usr/bin/env python3
"""Create and publish a verified web quiz PDF from reviewed screenshot crops."""

import argparse
import hashlib
import io
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path

import fitz
from PIL import Image, ImageCms


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_manifest(path):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    chapter = manifest["chapter"]
    count = manifest["expected_questions"]
    if type(chapter) is not int or chapter < 1:
        raise ValueError("chapter must be a positive integer")
    if type(count) is not int or count < 1:
        raise ValueError("expected_questions must be a positive integer")
    raw_day = manifest["date"]
    try:
        day = date.fromisoformat(raw_day).isoformat()
    except (ValueError, TypeError) as error:
        raise ValueError("date must be a valid YYYY-MM-DD date") from error
    if day != raw_day:
        raise ValueError("date must use YYYY-MM-DD")

    records = {}
    for record in manifest["pages"]:
        number = record["question"]
        if type(number) is not int or not 1 <= number <= count:
            raise ValueError(f"question number outside 1–{count}: {number}")
        if number in records:
            raise ValueError(f"duplicate question: {number}")
        records[number] = record
    missing = sorted(set(range(1, count + 1)) - records.keys())
    if missing:
        raise ValueError(f"missing questions: {', '.join(map(str, missing))}")
    return chapter, day, [load_crop(records[n]) for n in range(1, count + 1)]


def load_crop(record):
    source = Path(record["source"]).expanduser()
    if not source.is_absolute():
        raise ValueError(f"source path must be absolute: {source}")
    data = source.read_bytes()
    number = record["question"]
    if sha256(data) != record["sha256"]:
        raise ValueError(f"source SHA-256 mismatch for question {number}: {source}")
    box = record["crop"]
    if len(box) != 4 or any(type(coord) is not int for coord in box):
        raise ValueError(f"crop for question {number} must contain four integers")
    with Image.open(io.BytesIO(data)) as image:
        left, top, right, bottom = box
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ValueError(f"crop for question {number} is outside the source image")
        cropped = image.crop(box).convert("RGB")
        profile = image.info.get("icc_profile")
        if profile:
            cropped = ImageCms.profileToProfile(
                cropped, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                ImageCms.createProfile("sRGB"),
            )
        return cropped


def render_pdf(title, crops):
    with fitz.open() as pdf:
        pdf.set_metadata({"title": title})
        for crop in crops:
            page = pdf.new_page(width=crop.width / 2, height=crop.height / 2)
            buffer = io.BytesIO()
            crop.save(buffer, format="PNG")
            page.insert_image(page.rect, stream=buffer.getvalue())
        return pdf.tobytes(deflate=True)


def verify_pdf(data, title, crops):
    with fitz.open(stream=data, filetype="pdf") as pdf:
        if len(pdf) != len(crops) or pdf.metadata["title"] != title:
            raise ValueError("PDF title or page count does not match the manifest")
        for page, crop in zip(pdf, crops, strict=True):
            pixmap = page.get_pixmap(dpi=144, colorspace=fitz.csRGB, alpha=False)
            if ((pixmap.width, pixmap.height) != crop.size
                    or pixmap.samples != crop.tobytes()):
                raise ValueError(f"PDF page {page.number + 1} does not match the reviewed crop")


def write_new(path, data):
    with tempfile.TemporaryDirectory(prefix=".webquiz-", dir=path.parent) as temp:
        staged = Path(temp) / "candidate.pdf"
        staged.write_bytes(data)
        os.link(staged, path)


def publish(args, chapter, day, title, crops):
    data = args.candidate.read_bytes()
    if not re.fullmatch(r"[a-f0-9]{64}", args.reviewed_sha256) or sha256(data) != args.reviewed_sha256:
        raise ValueError("candidate SHA-256 does not match the reviewed SHA-256")
    verify_pdf(data, title, crops)

    quiz_root = args.repo.resolve(strict=True) / "웹과제"
    if not quiz_root.is_dir() or quiz_root.is_symlink():
        raise ValueError(f"web quiz directory not found or is a symlink: {quiz_root}")
    directory = quiz_root / f"{chapter}장" / "raw"
    if not directory.resolve().is_relative_to(quiz_root):
        raise ValueError(f"output directory resolves outside the web quiz directory: {directory}")
    target = directory / f"웹과제_{chapter}장_{day}.pdf"
    directory.mkdir(parents=True, exist_ok=True)
    try:
        write_new(target, data)
    except FileExistsError:
        try:
            if target.is_symlink() or not target.is_file():
                raise ValueError("destination is not a regular PDF file")
            verify_pdf(target.read_bytes(), title, crops)
        except (ValueError, RuntimeError, OSError) as error:
            raise ValueError(f"existing PDF conflicts with candidate: {target} ({error})") from error
        print(f"Reused {target} ({len(crops)} pages)")
    else:
        print(f"Saved {target} ({len(crops)} pages)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="render a candidate PDF for visual review")
    build.add_argument("manifest", type=Path)
    build.add_argument("--output", required=True, type=Path)
    save = commands.add_parser("publish", help="save a visually reviewed candidate to the project")
    save.add_argument("manifest", type=Path)
    save.add_argument("--repo", required=True, type=Path)
    save.add_argument("--candidate", required=True, type=Path)
    save.add_argument("--reviewed-sha256", required=True)
    args = parser.parse_args()

    try:
        chapter, day, crops = read_manifest(args.manifest)
        title = f"생명과학 {chapter}장 웹과제 · {day}"
        if args.command == "build":
            data = render_pdf(title, crops)
            verify_pdf(data, title, crops)
            write_new(args.output, data)
            print(f"{args.output} ({len(crops)} pages) SHA-256 {sha256(data)}")
        else:
            publish(args, chapter, day, title, crops)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, ImageCms.PyCMSError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
