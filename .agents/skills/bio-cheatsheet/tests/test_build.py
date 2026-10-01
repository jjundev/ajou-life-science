import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from _util import HAS_CHROME, MINI, TEMPLATE

import build


def frag(label: str, filler: int = 0) -> str:
    body = "".join(f"<li>줄 {i}</li>" for i in range(filler))
    return f'<section class="sec">\n  <span class="sec-label">{label}</span>\n  <ul class="pts">{body}</ul>\n</section>'


class TestRender(unittest.TestCase):
    def setUp(self):
        self.tpl = build.load_template(TEMPLATE)

    def test_template_parts(self):
        self.assertIn("<body>", self.tpl.head)
        self.assertIn('id="theme-light"', self.tpl.head)
        self.assertNotIn('<section class="page"', self.tpl.head.split("<body", 1)[1])
        self.assertTrue(self.tpl.tail.startswith("<!-- 넘침 경고: 각 쪽"))
        self.assertIn('class="theme-btn"', self.tpl.theme_btn)

    def test_template_comment_is_for_skill(self):
        head = TEMPLATE.read_text(encoding="utf-8").split("<html", 1)[0]
        self.assertNotIn("최대 2쪽", head)
        self.assertIn("build.py", head)
        self.assertIn(".later", TEMPLATE.read_text(encoding="utf-8"))

    def test_render_pages(self):
        html = build.render(self.tpl, "9장 미니", "cheatsheet_9장",
                            [[frag("① 가"), frag("② 나")], [frag("③ 다")]])
        pages = html.split("<body", 1)[1].split('<section class="page"')[1:]
        self.assertEqual(len(pages), 2)
        self.assertIn('<span class="page-no">1 / 2</span>', pages[0])
        self.assertIn('<span class="page-no">2 / 2</span>', pages[1])
        self.assertIn('<p class="page-toc">① 가 · ② 나</p>', pages[0])
        self.assertIn('<p class="page-toc">③ 다</p>', pages[1])
        self.assertIn('class="theme-btn"', pages[0])
        self.assertNotIn('class="theme-btn"', pages[1])
        self.assertEqual(html.count('<h1 class="page-title">9장 미니</h1>'), 2)
        self.assertIn("<title>9장 미니 커닝페이퍼</title>", html)

    def test_head_comment_names_output_and_has_no_nested_comment(self):
        html = build.render(self.tpl, "9장 미니", "cheatsheet_9장", [[frag("① 가")]])
        head = html.split("<html", 1)[0]
        self.assertIn("cheatsheet_9장.pdf", head)
        self.assertIn("cheatsheet_9장.html", head)
        self.assertNotIn("cheatsheet-template", head)
        inner = head.split("<!--", 2)[2] if head.count("<!--") > 1 else ""
        self.assertEqual(inner, "", "head 주석 안에 <!-- 가 있으면 주석이 일찍 닫힌다")

    def test_no_template_samples(self):
        html = build.render(self.tpl, "9장 미니", "cheatsheet_9장", [[frag("① 가")]])
        body = re.sub(r"<!--.*?-->", "", html.split("<body", 1)[1], flags=re.S)
        for word in ("키워드 A", "견본", "쪽 제목"):
            self.assertNotIn(word, body)


class TestOrder(unittest.TestCase):
    def test_order_by_spec(self):
        spec = json.loads((MINI / "spec.json").read_text(encoding="utf-8"))
        frags = build.load_fragments(spec, MINI / "sections")
        self.assertEqual([build.label_of(f) for f in frags],
                         ["① 시험장 체크", "② 용어 바꿔 부르기", "③ 미니 구역"])
        self.assertTrue(frags[2].startswith("<!-- 출처:"), "앞 출처 주석이 조각과 함께 간다")

    def test_missing_and_extra_fragments_fail(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(MINI / "sections", tmp / "s")
            (tmp / "s" / "03.html").unlink()
            (tmp / "s" / "09.html").write_text(frag("⑨ 남는 구역"), encoding="utf-8")
            spec = json.loads((MINI / "spec.json").read_text(encoding="utf-8"))
            with self.assertRaises(build.BuildError) as cm:
                build.load_fragments(spec, tmp / "s")
            self.assertIn("③ 미니 구역", str(cm.exception))
            self.assertIn("⑨ 남는 구역", str(cm.exception))
        finally:
            shutil.rmtree(tmp)


class TestPaginate(unittest.TestCase):
    """probe는 (쪽 번호, 라벨) 목록을 돌려준다. 쪽당 구역 3개까지만 들어간다고 흉내 낸다."""

    @staticmethod
    def fake_probe(pages):
        out = []
        for i, page in enumerate(pages, 1):
            out += [(i, build.label_of(f)) for f in page[3:]]
        return out

    def test_moves_tail_until_fit(self):
        frags = [frag(f"{c} 구역") for c in "①②③④⑤⑥⑦"]
        pages = build.paginate(frags, self.fake_probe)
        self.assertEqual([len(p) for p in pages], [3, 3, 1])

    def test_single_section_too_big_fails(self):
        def probe(pages):
            return [(1, build.label_of(pages[0][0]))]
        with self.assertRaises(build.BuildError) as cm:
            build.paginate([frag("① 큰 구역")], probe)
        self.assertIn("① 큰 구역", str(cm.exception))

    def test_page_cap(self):
        def one_per_page(pages):
            return [(i, build.label_of(p[1])) for i, p in enumerate(pages, 1) if len(p) > 1]
        frags = [frag(f"구역{i}") for i in range(10)]
        with self.assertRaises(build.BuildError):
            build.paginate(frags, one_per_page, max_pages=3)

    def test_parse_overflow(self):
        self.assertEqual(build.parse_overflow('<div data-overflow="1쪽 ③ 가 나, 2쪽 ⑤ 다"></div>'),
                         [(1, "③ 가 나"), (2, "⑤ 다")])
        self.assertEqual(build.parse_overflow("<div></div>"), [])


@unittest.skipUnless(HAS_CHROME, "Chrome 없음")
class TestChromeBuild(unittest.TestCase):
    def test_real_overflow_paginates(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            sec = tmp / "sections"
            sec.mkdir()
            labels = [f"구역{i:02d}" for i in range(12)]
            for i, lab in enumerate(labels):
                (sec / f"{i:02d}.html").write_text(frag(lab, filler=18), encoding="utf-8")
            spec = {"chapter": 9, "title": "9장 넘침", "sections": [{"label": l} for l in labels]}
            (tmp / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = build.build(tmp / "spec.json", sec, tmp / "out", pdf=False)
            html = out.read_text(encoding="utf-8")
            self.assertGreater(html.split("<body", 1)[1].count('<section class="page"'), 1)
            self.assertEqual(build.chrome_overflow(out), [])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
