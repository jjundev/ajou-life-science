"""생명과학 교재(522쪽)를 장별/부록별 23개 PDF로 무손실 분할하는 엔진."""

import os
import argparse
import fitz

CHAPTERS = [
    {"id": "00", "title": "앞부속", "start": 1, "end": 9, "filename": "00_앞부속_표지_차례.pdf"},
    {"id": "01", "title": "생물분자와 세포", "start": 10, "end": 37, "filename": "01장_생물분자와_세포.pdf"},
    {"id": "02", "title": "세포호흡과 광합성", "start": 38, "end": 61, "filename": "02장_세포호흡과_광합성.pdf"},
    {"id": "03", "title": "세포분열", "start": 62, "end": 79, "filename": "03장_세포분열.pdf"},
    {"id": "04", "title": "유전", "start": 80, "end": 99, "filename": "04장_유전.pdf"},
    {"id": "05", "title": "DNA 복제와 유전자의 발현", "start": 100, "end": 125, "filename": "05장_DNA_복제와_유전자의_발현.pdf"},
    {"id": "06", "title": "DNA 기술과 유전체학", "start": 126, "end": 145, "filename": "06장_DNA_기술과_유전체학.pdf"},
    {"id": "07", "title": "진화 사상과 소진화", "start": 146, "end": 163, "filename": "07장_진화_사상과_소진화.pdf"},
    {"id": "08", "title": "종분화와 대진화", "start": 164, "end": 183, "filename": "08장_종분화와_대진화.pdf"},
    {"id": "09", "title": "생물다양성: 원핵생물과 진핵생물", "start": 184, "end": 215, "filename": "09장_생물다양성_원핵생물과_진핵생물.pdf"},
    {"id": "10", "title": "식물체의 구조, 수송 및 영양", "start": 216, "end": 245, "filename": "10장_식물체의_구조_수송_및_영양.pdf"},
    {"id": "11", "title": "식물의 생식 및 발달", "start": 246, "end": 267, "filename": "11장_식물의_생식_및_발달.pdf"},
    {"id": "12", "title": "신경계, 감각계, 근육계", "start": 268, "end": 295, "filename": "12장_신경계_감각계_근육계.pdf"},
    {"id": "13", "title": "호흡계와 순환계", "start": 296, "end": 317, "filename": "13장_호흡계와_순환계.pdf"},
    {"id": "14", "title": "면역체계", "start": 318, "end": 337, "filename": "14장_면역체계.pdf"},
    {"id": "15", "title": "동물 영양, 배설, 내분비", "start": 338, "end": 367, "filename": "15장_동물_영양_배설_내분비.pdf"},
    {"id": "16", "title": "동물의 생식과 발생", "start": 368, "end": 387, "filename": "16장_동물의_생식과_발생.pdf"},
    {"id": "17", "title": "개체군과 군집", "start": 388, "end": 419, "filename": "17장_개체군과_군집.pdf"},
    {"id": "18", "title": "생태계와 기후 변화", "start": 420, "end": 447, "filename": "18장_생태계와_기후_변화.pdf"},
    {"id": "19", "title": "동물행동", "start": 448, "end": 471, "filename": "19장_동물행동.pdf"},
    {"id": "A1", "title": "해답", "start": 472, "end": 477, "filename": "부록_해답.pdf"},
    {"id": "A2", "title": "용어풀이", "start": 478, "end": 506, "filename": "부록_용어풀이.pdf"},
    {"id": "A3", "title": "찾아보기", "start": 507, "end": 522, "filename": "부록_찾아보기.pdf"},
]

def validate_metadata(chapters: list[dict], total_pages: int = 522) -> bool:
    """메타데이터가 1쪽부터 total_pages쪽까지 누락 및 겹침 없이 연속되는지 검증."""
    if not chapters:
        return False
    if chapters[0].get("start") != 1:
        return False
    for i in range(len(chapters)):
        start = chapters[i].get("start")
        end = chapters[i].get("end")
        if start is None or end is None or start > end:
            return False
        if i < len(chapters) - 1:
            next_start = chapters[i + 1].get("start")
            if end + 1 != next_start:
                return False
    if chapters[-1].get("end") != total_pages:
        return False
    return True

def split_pdf(src_path: str, out_dir: str, chapters: list[dict]) -> list[str]:
    """PyMuPDF(fitz)를 사용하여 원본 PDF를 메타데이터 범위에 따라 분할 저장."""
    os.makedirs(out_dir, exist_ok=True)
    src_doc = fitz.open(src_path)
    output_paths = []
    try:
        for item in chapters:
            start_idx = item["start"] - 1
            end_idx = item["end"] - 1
            out_path = os.path.join(out_dir, item["filename"])
            
            new_doc = fitz.open()
            new_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx)
            new_doc.save(out_path, garbage=3, deflate=True)
            new_doc.close()
            output_paths.append(out_path)
    finally:
        src_doc.close()
    return output_paths

def main():
    """CLI 진입점."""
    parser = argparse.ArgumentParser(description="생명과학 교재 PDF 장별 분할")
    parser.add_argument("--src", default="교과서/생명과학_기초와_응용_2판.pdf", help="원본 PDF 경로")
    parser.add_argument("--out", default="교과서/장별", help="출력 디렉토리")
    args = parser.parse_args()

    if not os.path.exists(args.src):
        raise FileNotFoundError(f"원본 교재를 찾을 수 없습니다: {args.src}")

    if not validate_metadata(CHAPTERS, 522):
        raise ValueError("메타데이터 검증 실패: 522쪽 연속성 및 일관성 오류")

    print(f"분할 시작: {args.src} -> {args.out}")
    paths = split_pdf(args.src, args.out, CHAPTERS)
    print(f"성공적으로 {len(paths)}개 파일 분할 완료.")

if __name__ == "__main__":
    main()
