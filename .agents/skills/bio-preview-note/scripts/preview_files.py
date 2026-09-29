#!/usr/bin/env python3
"""
예습노트 대상 수업일·시작 쪽 고르기와 기존 예습노트 백업 (표준 라이브러리만 사용).

- 대상 수업일: --date MMDD. 없으면 오늘(포함) 이후 STT가 없는 가장 가까운 화·목(강의계획서 "화D 목C").
- 대상 날짜의 STT가 이미 있으면(끝난 수업) 멈추고 bio-review-pack을 안내한다.
- 날짜 없이 골랐는데 그 날짜 예습노트가 이미 있으면 멈춘다(날짜를 주면 다시 만든다).
- 시작 쪽: 가장 최근 정리노트(범위의 끝 날짜 기준) HTML의 .tag.slide 중 가장 큰 (장, 쪽). 그 쪽을 포함한다.
  정리노트 끝의 "다음 시간 예고" 토픽(id가 -next로 끝남)은 아직 안 배운 쪽이라 뺀다.
- 정리노트보다 뒤의 STT가 있으면(끝난 수업의 복습팩이 아직 없음) 멈추고 bio-review-pack을 먼저 안내한다.
- macOS NFD 폴더·파일명도 NFC로 비교해 찾는다.
CLI:
  preview_files.py pick --repo REPO [--date 0929]   → "0929<TAB>4<TAB>2<TAB>강의노트 PDF 절대 경로"
  preview_files.py backup --repo REPO --date 0929 --run RUN
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import unicodedata

LECTURES_DIR = "강의노트"
NOTES_DIR = "예습노트"
REVIEW_DIR = "복습노트"
STT_DIR = "STT"
CLASS_WEEKDAYS = {1, 3}  # 화(1)·목(3)
DATE_RE = re.compile(r"(\d{2})(\d{2})")
STT_RE = re.compile(r"(\d{4})[ _]생명\.md")
REVIEW_NOTE_RE = re.compile(r"정리노트_(?:\d{4}-)?(\d{4})_.+\.html")
TAG_RE = re.compile(r'class="tag slide">\s*(\d+)장 p(\d+)(?:–p?(\d+))?\s*<')
CHAPTER_PDF_RE = re.compile(r"(\d+)장 .+\.pdf")
ARTICLE_RE = re.compile(r'<article\b[^>]*\bid="([^"]+)"')
NEXT_TOPIC_SUFFIX = "-next"  # bio-review-pack의 "다음 시간 예고" 토픽


class PickError(RuntimeError):
    pass


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def entries(d: Path | None) -> dict[str, Path]:
    """d 안의 항목을 NFC 이름 → 실제 경로로(NFD 이름 포함). d가 폴더가 아니면 빈 dict."""
    if d is None or not d.is_dir():
        return {}
    return {nfc(n): d / n for n in os.listdir(d)}


def child(parent: Path | None, name: str) -> Path | None:
    return entries(parent).get(name)


def normalize_date(arg: str) -> str:
    m = DATE_RE.fullmatch(arg.strip())
    if not m or not (1 <= int(m.group(1)) <= 12 and 1 <= int(m.group(2)) <= 31):
        raise PickError(f"날짜 형식이 아님: {arg!r} (예: 0929)")
    return m.group(0)


def stt_dates(repo) -> set[str]:
    return {m.group(1) for n in entries(child(Path(repo), STT_DIR)) if (m := STT_RE.fullmatch(n))}


def next_class_date(today: dt.date, done: set[str]) -> str:
    d = today
    for _ in range(366):
        mmdd = d.strftime("%m%d")
        if d.weekday() in CLASS_WEEKDAYS and mmdd not in done:
            return mmdd
        d += dt.timedelta(days=1)
    raise PickError("다음 수업일을 찾지 못했어요. --date로 날짜를 주세요.")


def latest_review_note(repo) -> tuple[str, Path]:
    best: tuple[str, Path] | None = None
    for folder in entries(child(Path(repo), REVIEW_DIR)).values():
        for name, path in entries(folder).items():
            m = REVIEW_NOTE_RE.fullmatch(name)
            if m and (best is None or m.group(1) > best[0]):
                best = (m.group(1), path)
    if best is None:
        raise PickError(f"{REVIEW_DIR}/에 정리노트가 없어요. 강의계획서 진도로 장과 쪽을 직접 고르세요.")
    return best


def last_page(note: Path) -> tuple[int, int]:
    text = note.read_text(encoding="utf-8")
    bounds = [("", 0)] + [(m.group(1), m.start()) for m in ARTICLE_RE.finditer(text)] + [("", len(text))]
    found = []
    for (topic, a), (_, b) in zip(bounds, bounds[1:]):
        if topic.endswith(NEXT_TOPIC_SUFFIX):
            continue
        found += [(int(ch), int(end or start)) for ch, start, end in TAG_RE.findall(text[a:b])]
    if not found:
        raise PickError(f"정리노트에 쪽 태그(예: '4장 p2')가 없어요: {nfc(note.name)}. 장과 쪽을 직접 고르세요.")
    return max(found)


def chapter_pdf(repo, chapter: int) -> Path:
    for name, path in entries(child(Path(repo), LECTURES_DIR)).items():
        m = CHAPTER_PDF_RE.fullmatch(name)
        if m and int(m.group(1)) == chapter:
            return path
    raise PickError(f"{LECTURES_DIR}/에 {chapter}장 PDF가 없어요. 새 강의노트가 올라왔는지 ajou-bb로 확인하세요.")


def has_note(repo, date: str) -> bool:
    notes = entries(child(child(Path(repo), NOTES_DIR), date))
    return any(n.startswith(f"예습노트_{date}_") and n.endswith(".html") for n in notes)


def pick(repo, date: str | None = None, today: dt.date | None = None) -> tuple[str, int, int, Path]:
    repo = Path(repo)
    done = stt_dates(repo)
    if date is not None:
        date = normalize_date(date)
    else:
        date = next_class_date(today or dt.date.today(), done)
        if has_note(repo, date):
            raise PickError(f"{date} 수업의 예습노트가 이미 있어요. 다시 만들려면 날짜를 인자로 주세요.")
    if date in done:
        raise PickError(f"{date} 수업은 이미 STT가 있어요(수업이 끝났어요). 복습은 /bio-review-pack {date}을 쓰세요.")
    reviewed, note = latest_review_note(repo)
    behind = sorted(d for d in done if reviewed < d < date)
    if behind:
        span = behind[0] if len(behind) == 1 else f"{behind[0]}-{behind[-1]}"
        raise PickError(f"{', '.join(behind)} 수업은 STT가 있는데 정리노트가 아직 없어요. "
                        f"시작 쪽을 정확히 잡으려면 먼저 /bio-review-pack {span}을 돌리세요.")
    chapter, page = last_page(note)
    return date, chapter, page, chapter_pdf(repo, chapter)


def _count(p: Path) -> int:
    return sum(len(files) for _, _, files in os.walk(p)) if p.is_dir() else 1


def backup(repo, date: str, run) -> Path | None:
    run = Path(run)
    try:
        date = normalize_date(date)
    except PickError as e:
        raise PickError(f"백업 중단: {e}") from e
    if not run.is_dir():
        raise PickError(f"백업 중단: run 폴더 없음: {run}")
    src = child(child(Path(repo), NOTES_DIR), date)
    hits = sorted((n, p) for n, p in entries(src).items() if n.startswith(f"예습노트_{date}_") or n == f"figures_{date}")
    if not hits:
        return None
    dst = Path(tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run))  # 항상 새 폴더
    for name, path in hits:
        if path.is_dir():
            shutil.copytree(path, dst / name)
        else:
            shutil.copy2(path, dst / name)
    want, got = sum(_count(p) for _, p in hits), _count(dst)
    if got != want:
        raise PickError(f"백업 실패: 파일 {want}개 중 {got}개만 복사됨 → {dst}")
    return dst


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pick")
    p.add_argument("--repo", required=True)
    p.add_argument("--date")
    b = sub.add_parser("backup")
    b.add_argument("--repo", required=True)
    b.add_argument("--date", required=True)
    b.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "pick":
            date, chapter, page, pdf = pick(args.repo, args.date)
            print(f"{date}\t{chapter}\t{page}\t{pdf}")
        else:
            dst = backup(args.repo, args.date, args.run)
            print(f"백업: {dst}" if dst else "백업할 기존 예습노트 없음")
    except PickError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
