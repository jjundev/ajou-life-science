import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "웹과제예상/커닝페이퍼/2장/cheatsheet_2장.html"
PDF = HTML.with_suffix(".pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

LABELS = [
    "① 시험장 체크", "② 용어 바꿔 부르기", "③ ATP", "④ 효소", "⑤ 세포호흡 지도",
    "⑥ ATP 32", "⑦ 전자전달·화학삼투", "⑧ 발효", "⑨ 미토콘드리아↔엽록체",
    "⑩ 광합성 반응식", "⑪ 색소·스펙트럼", "⑫ 광의존반응", "⑬ 캘빈 회로",
    "⑭ 광호흡·C3/C4/CAM", "⑮ 호흡 vs 광합성",
]
PLACEHOLDERS = ["키워드 A", "구역 제목", "견본", "박스 A", "오답 문장 예시", "쪽 제목"]


def raw() -> str:
    return HTML.read_text(encoding="utf-8")


def body() -> str:
    return re.sub(r"<!--.*?-->", "", raw().split("<body", 1)[1], flags=re.S)


def text(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sections() -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r'<section class="sec">(.*?)</section>', body(), re.S):
        label = re.search(r'<span class="sec-label">(.*?)</span>', m.group(1)).group(1).strip()
        out.append((label, m.group(1)))
    return out


def section(label: str) -> str:
    found = dict(sections())
    if label not in found:
        raise AssertionError(f"구역 없음: {label}")
    return found[label]


def pages() -> list[str]:
    return body().split('<section class="page"')[1:]


class Base(unittest.TestCase):
    def assertHas(self, label, *terms):
        t = text(section(label))
        for term in terms:
            self.assertIn(term, t, f"{label}에 '{term}' 없음")


class TestStructure(Base):
    def test_header_comment_unlimited_pages(self):
        head = raw().split("<html", 1)[0]
        self.assertIn("쪽 수 제한 없음", head)
        self.assertNotIn("최대 2쪽", head)
        self.assertIn("cheatsheet_2장.pdf", head)

    def test_labels_in_spec_order(self):
        labels = [l for l, _ in sections()]
        self.assertTrue(labels, "구역이 하나도 없음")
        self.assertEqual(labels, LABELS[: len(labels)])

    def test_toc_matches_labels_per_page(self):
        for i, p in enumerate(pages(), 1):
            toc = text(re.search(r'<p class="page-toc">(.*?)</p>', p, re.S).group(1))
            labels = [re.search(r'<span class="sec-label">(.*?)</span>', s).group(1).strip()
                      for s in re.findall(r'<section class="sec">.*?</section>', p, re.S)]
            self.assertEqual(toc, " · ".join(labels), f"{i}쪽 목차 줄 불일치")

    def test_page_numbers(self):
        ps = pages()
        nos = [text(re.search(r'<span class="page-no">(.*?)</span>', p).group(1)) for p in ps]
        self.assertEqual(nos, [f"{i} / {len(ps)}" for i in range(1, len(ps) + 1)])

    def test_no_template_placeholders(self):
        t = text(body())
        for ph in PLACEHOLDERS:
            self.assertNotIn(ph, t)

    def test_no_answer_numbers(self):
        t = text(body())
        self.assertNotIn("정답", t)
        self.assertIsNone(re.search(r"\([1-5]\)", t))

    def test_traps_have_source_comment(self):
        b = raw().split("<body", 1)[1]
        total = b.count('<div class="trap">')
        sourced = len(re.findall(r"<!-- 출처: [^>]+? -->\s*<div class=\"trap\">", b))
        self.assertEqual(total, sourced)

    def test_trap_count_per_section(self):
        for label, html in sections():
            n = html.count('class="trap-x"')
            if label in LABELS[:2]:
                self.assertEqual(n, 0, label)
            else:
                self.assertTrue(1 <= n <= 3, f"{label}: 함정 {n}개")

    def test_later_block_is_last(self):
        for label, html in sections():
            if "교수님: 몰라도 됨" in html:
                later = html.find('class="later"')
                self.assertNotEqual(later, -1, label)
                self.assertGreater(later, html.rfind('class="trap'), label)
                self.assertIn('<span class="badge prof">교수님: 몰라도 됨</span>', html[later:], label)

    def test_unicode_formula_only(self):
        t = text(body())
        self.assertIsNone(re.search(r"\b(CO2|H2O|O2|FADH2)\b|NADP?\+|H\+", t))

    def test_svg_no_hardcoded_color(self):
        self.assertIsNone(re.search(r'(fill|stroke)="#', body()))

    def test_svg_viewbox_width(self):
        for w in re.findall(r'viewBox="0 0 (\d+) \d+"', body()):
            if int(w) > 8:  # marker viewBox(8×8)는 제외
                self.assertLessEqual(int(w), 360)

    @unittest.skipUnless(Path(CHROME).exists(), "Chrome 없음")
    def test_no_overflow(self):
        out = subprocess.run([CHROME, "--headless=new", "--virtual-time-budget=15000",
                              "--dump-dom", HTML.as_uri()], capture_output=True, text=True, timeout=120).stdout
        self.assertIn("</body>", out, "dump-dom 실패")
        self.assertNotIn("data-overflow", out, re.findall(r'data-overflow="[^"]*"', out))

    @unittest.skipUnless(shutil.which("pdfinfo") and shutil.which("pdffonts"), "poppler 없음")
    def test_pdf_fresh_and_fonts(self):
        self.assertTrue(PDF.exists(), "PDF 없음")
        self.assertGreaterEqual(PDF.stat().st_mtime, HTML.stat().st_mtime, "PDF가 HTML보다 오래됨 — 다시 출력")
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        self.assertEqual(int(re.search(r"Pages:\s+(\d+)", info).group(1)), len(pages()))
        fonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True).stdout
        self.assertIn("Pretendard", fonts)


class TestSections(Base):
    def test_s01_check(self):
        self.assertHas("① 시험장 체크", "1장", "보기 순서", "옳지 않은 것", "그림", "조건", "거꾸로", "결정 단서", "39초")

    def test_s02_synonyms(self):
        self.assertHas("② 용어 바꿔 부르기", "명반응", "광의존반응", "암반응", "광독립반응", "크렙스 회로",
                       "TCA 회로", "전자전달사슬", "막간 공간", "ATP 생성효소", "화학삼투설", "뉴클레오티드")

    def test_s03_atp(self):
        self.assertHas("③ ATP", "아데닌", "리보스", "인산기", "ADP", "능동수송", "확산")
        self.assertIn("<svg", section("③ ATP"))

    def test_s04_enzyme(self):
        self.assertHas("④ 효소", "활성화 에너지", "활성 부위", "특이성", "보조인자", "조효소", "변성", "최적 온도", "펩신", "트립신", "젖당")
    def test_s05_respiration_map(self):
        self.assertHas("⑤ 세포호흡 지도", "해당과정", "세포질", "피루브산 산화", "아세틸-CoA", "시트르산 회로",
                       "기질", "내막", "기질 수준 인산화", "산화적 인산화", "FADH₂")
        self.assertEqual(section("⑤ 세포호흡 지도").count('<table class="cmp">'), 2)

    def test_s06_atp32(self):
        self.assertHas("⑥ ATP 32", "28", "4", "32", "NADH 10", "30", "34%", "66%")

    def test_s07_etc(self):
        self.assertHas("⑦ 전자전달·화학삼투", "막 사이 공간", "ATP 합성효소", "최종 전자수용체", "H⁺ 농도 기울기", "환원", "미첼")
        self.assertIn("<svg", section("⑦ 전자전달·화학삼투"))
    def test_s08_fermentation(self):
        self.assertHas("⑧ 발효", "젖산", "알코올", "아세트알데하이드", "에탄올", "NAD⁺", "해당과정", "효모", "요구르트", "중간 대사산물")

    def test_s09_organelles(self):
        self.assertHas("⑨ 미토콘드리아↔엽록체", "크리스테", "틸라코이드", "스트로마", "그라나", "막 사이 공간", "기질", "내막계")
        self.assertIn("<svg", section("⑨ 미토콘드리아↔엽록체"))
    def test_s10_equation(self):
        self.assertHas("⑩ 광합성 반응식", "6CO₂ + 6H₂O", "C₆H₁₂O₆ + 6O₂", "물", "NADPH", "광독립영양", "종속영양")

    def test_s11_spectrum(self):
        self.assertHas("⑪ 색소·스펙트럼", "흡수 스펙트럼", "작용 스펙트럼", "흡광도", "반사", "카로티노이드", "틸라코이드 막")
        self.assertIn("<svg", section("⑪ 색소·스펙트럼"))

    def test_s12_light_reactions(self):
        self.assertHas("⑫ 광의존반응", "광계 2", "광계 1", "P680", "P700", "NADP⁺", "물의 광분해", "안테나", "반응 중심")
        self.assertIn("<svg", section("⑫ 광의존반응"))
    def test_s13_calvin(self):
        self.assertHas("⑬ 캘빈 회로", "RuBP", "루비스코", "PGA", "G3P", "스트로마", "6바퀴", "투입물", "18", "12")

    def test_s14_photorespiration(self):
        self.assertHas("⑭ 광호흡·C3/C4/CAM", "광호흡", "기공", "첫 번째로 안정한 분자", "옥수수", "사탕수수", "선인장", "밤")

    def test_s15_compare(self):
        self.assertHas("⑮ 호흡 vs 광합성", "NADH", "NADPH", "미토콘드리아", "엽록체", "식물세포", "동물세포", "물 → 산소")

    def test_all_sections_present(self):
        self.assertEqual([l for l, _ in sections()], LABELS)

    def test_required_terms_from_chapter_close(self):
        t = text(body())
        for term in ["기질 수준 인산화", "산화적 인산화", "화학삼투설", "최종 전자수용체", "NAD⁺ 재생", "중간 대사산물",
                     "광계 1", "광계 2", "P680", "P700", "NADP⁺", "RuBP", "PGA", "G3P", "루비스코", "CAM"]:
            self.assertIn(term, t, term)
    def test_s09_grana_is_thylakoid_stack(self):
        self.assertHas("⑨ 미토콘드리아↔엽록체", "그라나 = 틸라코이드 더미")

    def test_s13_no_stage_claim_above_counts(self):
        self.assertNotIn("환원 단계에서", text(section("⑬ 캘빈 회로")))

    def test_s01_chapter1_numbers_are_labelled(self):
        for li in re.findall(r"<li>(.*?)</li>", section("① 시험장 체크"), re.S):
            if "/17" in li or "17문항" in li:
                self.assertIn("1장", text(li), text(li))

    def test_svg_height_fits_fig_max(self):
        # 단 너비 약 357px에서 --fig-max 35mm(≈132px)에 걸리면 그림이 축소돼 글자가 7.5pt 아래로 떨어진다
        for w, h in re.findall(r'viewBox="0 0 (\d+) (\d+)"', body()):
            if int(w) > 8:
                self.assertLessEqual(int(h) * 357 / int(w), 132, f"viewBox {w}x{h}")

if __name__ == "__main__":
    unittest.main()
