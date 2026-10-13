#!/usr/bin/env python3
"""
Context inference and biology glossary extractor for bio-stt.

- Infers class date (MMDD) from audio filename or explicit argument.
- Infers syllabus chapter from 예습노트/MMDD or recent 복습노트/.
- Extracts key technical terms directly from 강의노트/<N>장 *.pdf.
- Builds domain guidance prompt for STT transcription subagents.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

DATE_PATTERNS = [
    # 20261006, 2026-10-06, 2026.10.06, 2026_1006
    re.compile(r"(?:20\d{2})[-_.]?([01]\d)[-_.]?([0-3]\d)"),
    # 1006 생명, 1006.m4a, 녹음_1006.wav, 0929
    re.compile(r"(?:^|[^\d])([01]\d)([0-3]\d)(?:[^\d]|$)"),
]

COMMON_BIO_ERROR_RULES = [
    ("이수치/이수태", "이수체"),
    ("여기", "역위 (유전학/염색체 구조)"),
    ("비분류", "비분리 (감수분열 비분리)"),
    ("클라인 필터", "클라인펠터 증후군"),
    ("터너", "터너 증후군"),
    ("낭포 섬유증", "낭포성 섬유증"),
    ("텔리케이스", "헬리케이스 (DNA helicase)"),
    ("리가제", "리가아제 (또는 DNA 연결효소)"),
    ("전좌/전자", "전좌 (염색체 구조 이상)"),
]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def parse_date(filename_or_path: str, date_override: str | None = None) -> str:
    """Extract MMDD string from filename or override."""
    if date_override:
        clean = date_override.strip()
        m = re.fullmatch(r"(\d{2})(\d{2})", clean)
        if m and (1 <= int(m.group(1)) <= 12) and (1 <= int(m.group(2)) <= 31):
            return m.group(0)
        raise ValueError(f"유효하지 않은 날짜 형식입니다: {date_override!r} (예: 1006)")

    base = nfc(Path(filename_or_path).name)

    for pat in DATE_PATTERNS:
        match = pat.search(base)
        if match:
            mm, dd = match.group(1), match.group(2)
            if (1 <= int(mm) <= 12) and (1 <= int(dd) <= 31):
                return f"{mm}{dd}"

    raise ValueError(
        f"파일명에서 수업 날짜(MMDD)를 찾을 수 없습니다: {base!r}\n"
        f"--date MMDD 옵션으로 날짜를 직접 지정해 주세요. (예: /bio-stt audio.m4a --date 1006)"
    )


def infer_chapter(repo_root: Path | str, mmdd: str) -> int:
    """Infer lecture chapter number from 예습노트/<MMDD>/ or latest 복습노트/."""
    repo = Path(repo_root)

    # 1순위: 예습노트/<MMDD>/ 안의 파일 검사
    preview_dir = repo / "예습노트" / mmdd
    if preview_dir.is_dir():
        for f in preview_dir.iterdir():
            name = nfc(f.name)
            # 파일 내용 또는 파일명 검사
            if name.endswith(".md"):
                try:
                    content = f.read_text(encoding="utf-8")
                    m = re.search(r"강의노트\s*(\d+)장", content)
                    if m:
                        return int(m.group(1))
                    m2 = re.search(r"(\d+)장\s*p\d+", content)
                    if m2:
                        return int(m2.group(1))
                except Exception:
                    pass

    # 2순위: 복습노트/ 에서 가장 최근 완료된 장 조사
    review_root = repo / "복습노트"
    if review_root.is_dir():
        folders = sorted([d.name for d in review_root.iterdir() if d.is_dir() and re.fullmatch(r"\d{4}", d.name)])
        # mmdd 이전의 가장 최근 복습노트
        past_folders = [d for d in folders if d <= mmdd]
        target_folder = past_folders[-1] if past_folders else (folders[-1] if folders else None)

        if target_folder:
            f_dir = review_root / target_folder
            # 장마감 파일 확인 (예: .assets/장마감_1001_4장.md) — 부속 파일은 .assets 안에만 둔다
            assets_dir = f_dir / ".assets"
            if assets_dir.is_dir():
                for f in assets_dir.iterdir():
                    m_close = re.match(r"장마감_\d{4}_(\d+)장\.md", nfc(f.name))
                    if m_close:
                        closed_ch = int(m_close.group(1))
                        if target_folder == mmdd:
                            return closed_ch
                        return closed_ch + 1

            # 정리노트 내 슬라이드 태그 확인
            for f in f_dir.iterdir():
                if f.name.endswith(".html"):
                    try:
                        html = f.read_text(encoding="utf-8")
                        tags = re.findall(r'class="tag slide">\s*(\d+)장', html)
                        if tags:
                            return int(tags[-1])
                    except Exception:
                        pass

    # 기본 fallback: 5장 (학기 중반 기본값)
    return 5


def get_chapter_title(repo_root: Path | str, chapter: int) -> str:
    """Find chapter title from 강의노트/ directory."""
    repo = Path(repo_root)
    lec_dir = repo / "강의노트"
    if lec_dir.is_dir():
        for f in lec_dir.iterdir():
            name = nfc(f.name)
            m = re.match(rf"^{chapter}장\s*(.+?)\.pdf$", name)
            if m:
                return m.group(1).strip()
    return f"{chapter}장"


# AI 정책 및 CBRN 안전 필터 오탐을 방지하기 위한 제외 키워드
POLICY_EXCLUSIONS = {
    # CBRN / 생물무기 / 유전자 조작 관련 오탐 유발 영어 단어
    "cartagena", "protocol", "protocols", "biosafety", "germ-line", "germline",
    "somatic", "therapy", "therapies", "weapon", "weapons", "bioterror",
    "pathogen", "pathogens", "anthrax", "toxin", "toxins", "engineering",
    "engineer", "engineered", "modified", "organism", "organisms", "transgenic",
    "recombinant", "vector", "vectors", "virus", "viruses", "viral",
    "hazard", "hazards", "clone", "cloning", "cloned", "manipulate",
    "manipulation", "reaction", "reactions", "pharm", "animal", "animals",
    # 일반 영어 불용어 (단순 빈출 단어)
    "and", "the", "for", "with", "from", "that", "this", "page", "figure",
    "table", "chapter", "section", "slide", "study", "human", "cell", "cells",
    "part", "type", "types", "test", "case", "system", "into", "over", "such",
    "than", "their", "them", "then", "there", "these", "they", "which", "would",
    "about", "after", "again", "also", "been", "before", "being", "between",
    "both", "came", "come", "could", "each", "have", "here", "just", "like",
    "make", "many", "more", "most", "much", "must", "only", "other", "same",
    "some", "such", "take", "time", "very", "were", "what", "when", "where",
    "while", "who", "will", "clustered", "regularly", "interspaced", "repeats",
}

# 영문 생명과학 표준 약어 패턴 (대문자 중심, 2~8자)
BIO_ACRONYM_PAT = re.compile(r"\b(?:[A-Z]{2,8}|[A-Z][a-z]{1,3}[A-Z0-9]+)\b")


def extract_chapter_terms(repo_root: Path | str, chapter: int, max_terms: int = 70) -> list[str]:
    """Extract key technical terms from lecture PDF and textbook without policy triggers."""
    repo = Path(repo_root)
    terms: set[str] = set()

    # 1. 강의노트 PDF 텍스트 추출
    lec_dir = repo / "강의노트"
    pdf_path = None
    if lec_dir.is_dir():
        for f in lec_dir.iterdir():
            if re.match(rf"^{chapter}장\s*.+\.pdf$", nfc(f.name)):
                pdf_path = f
                break

    if pdf_path and fitz:
        try:
            doc = fitz.open(pdf_path)
            full_text = "\n".join(page.get_text() for page in doc)

            # (1) 표준 생명과학 영문 약어 및 고유명사 (DNA, PCR, STR, EcoRI 등)
            for m in BIO_ACRONYM_PAT.finditer(full_text):
                word = m.group(0)
                if word.lower() not in POLICY_EXCLUSIONS and len(word) >= 2:
                    terms.add(word)

            # (2) 한글 생물학 전문용어 패턴 (2~7글자 한글)
            bio_suffix_pat = re.compile(
                r"[가-힣]{2,6}(?:효소|중합효소|연결효소|풀림효소|복제|전사|번역|코돈|프라이머|가닥|이수체|염색체|돌연변이|뉴클레오타이드|히스톤|유전자|발현|단백질|아미노산|인산|리보솜|소포체|엽록체|세포|절편)"
            )
            for m in bio_suffix_pat.finditer(full_text):
                terms.add(m.group(0))

            # (3) 괄호 안 병기 단어: 예) 헬리케이스(helicase), 복제분기점(replication fork)
            for m in re.finditer(r"([가-힣]{2,10})\s*\(([A-Za-z\s]+)\)", full_text):
                ko = m.group(1).strip()
                en = re.sub(r"\s+", " ", m.group(2)).strip()
                terms.add(ko)
                # 영문 단어 중 정책 제외 단어가 포함되지 않은 순수 학술 용어만 추가
                if 2 <= len(en) < 25:
                    en_words = re.findall(r"[A-Za-z]+", en.lower())
                    if not any(w in POLICY_EXCLUSIONS for w in en_words):
                        terms.add(en)
        except Exception:
            pass

    # 핵심 필수 공통 어휘 보강 (안전 필터에 무해한 순수 학술 용어)
    common_seed = [
        "DNA", "RNA", "mRNA", "tRNA", "rRNA", "뉴클레오타이드", "아데닌(A)", "구아닌(G)", "티민(T)", "시토신(C)", "우라실(U)",
        "헬리케이스", "프라이메이스", "DNA 폴리머레이스", "DNA 리가아제", "오카자키 절편", "복제분기점", "선도가닥", "지연가닥",
        "텔로미어", "텔로머레이스", "코돈", "안티코돈", "프로모터", "전사", "번역", "스플라이싱", "인트론", "엑손",
        "상동염색체", "자매염색분체", "이수체", "다배수체", "비분리", "결실", "중복", "전좌", "역위",
        "다운 증후군", "터너 증후군", "클라인펠터 증후군", "낭포성 섬유증", "CFTR", "SRY 유전자",
        "플라스미드", "제한효소", "점착성 말단", "젤 전기영동", "PCR", "프라이머", "STR"
    ]
    for w in common_seed:
        terms.add(w)

    # 길이 및 중요도 기준 정렬 후 상위 max_terms 반환
    sorted_terms = sorted(terms, key=lambda x: (-len(x), x))
    return sorted_terms[:max_terms]


def build_stt_prompt(chapter: int, chapter_title: str, terms: list[str]) -> str:
    """Format domain guidance block to inject into the subagent STT prompt."""
    sample_terms = ", ".join(terms[:40])
    homophone_guide = "\n".join(f"  - '{err}'로 들리면 -> '{cor}'" for err, cor in COMMON_BIO_ERROR_RULES)

    return f"""[아주대학교 교양 생명과학 강의 음성 전사 가이드]
- 본 오디오는 아주대학교 1학년 교양 수업(생명과학 기초와 응용)의 교수님 강의 녹음입니다.
- 학술 교양 강의로서, 유전학과 생물학의 기초 개념을 교육하는 표준 학부 강의입니다.
- 단원 범위: {chapter}장 {chapter_title}
- 주요 강의 표준 용어:
  {sample_terms}

- 필수 전사 및 발음 교정 규칙:
  1. 생명과학 표준 용어 최우선: 교수님의 발음이 뭉개지거나 일상 단어와 유사하게 들릴 경우, 문맥상 생명과학 표준 용어로 정확히 전사하세요.
{homophone_guide}
  2. 표기 원칙: 한글 표준 음차를 기본으로 하되, 핵심 약어(DNA, RNA, PCR, STR 등)는 영문 표기를 유지하세요.
  3. 철저한 축어성(Verbatim): 요약이나 어미 생략 없이 실제 발화된 내용을 있는 그대로 기록하세요.
"""


def main():
    parser = argparse.ArgumentParser(description="Infer biology context and terms for bio-stt")
    parser.add_argument("audio", help="Path to audio file (or filename)")
    parser.add_argument("--repo", default=".", help="Repository root path")
    parser.add_argument("--date", help="Class date override (MMDD)")
    parser.add_argument("--chapter", type=int, help="Chapter override (e.g. 5)")
    parser.add_argument("--json", action="store_true", help="Output JSON structure")
    parser.add_argument("--prompt-only", action="store_true", help="Print prompt injection text only")

    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    date = parse_date(args.audio, args.date)
    chapter = args.chapter if args.chapter else infer_chapter(repo, date)
    chapter_title = get_chapter_title(repo, chapter)
    terms = extract_chapter_terms(repo, chapter)
    prompt_guide = build_stt_prompt(chapter, chapter_title, terms)

    if args.prompt_only:
        print(prompt_guide)
        return

    result = {
        "audio": args.audio,
        "date": date,
        "chapter": chapter,
        "chapter_title": chapter_title,
        "output_filename": f"{date} 생명.md",
        "output_path": str(repo / "STT" / f"{date} 생명.md"),
        "terms_count": len(terms),
        "terms": terms,
        "prompt_guide": prompt_guide,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"수업 날짜: {date} (파일명에서 추출)")
        print(f"진도 단원: {chapter}장 ({chapter_title})")
        print(f"추출 용어: {len(terms)}개")
        print(f"최종 저장: STT/{date} 생명.md")


if __name__ == "__main__":
    main()
