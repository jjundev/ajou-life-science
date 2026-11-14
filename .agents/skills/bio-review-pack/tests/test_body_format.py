"""정리노트 본문 형식(비교표·함정 표·사슬·접힘)의 마크업 검사와, 새 구조 토픽이 조립·검사·MD 변환을 통과하는지 지킨다."""

import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from _util import FIXTURES, MINI_RUN

import assemble
import check_html
import html2md

NEW_TOPIC = FIXTURES / "body-format" / "s1-var.html"


def topic(body: str) -> str:
    return f'<html lang="ko"><body><article class="topic" id="t">{body}</article></body></html>'


def codes(source: str) -> list[str]:
    return [p.code for p in check_html.check_common(check_html.parse_html(source), source, Path("note.html"))]


PAIRS_HEAD = '<thead><tr><th>묻는 것</th><th>틀리기 쉬운 답</th><th>맞는 답</th></tr></thead>'
PAIRS_ROW = '<tr><th>단위</th><td><del>원래 단위</del></td><td>제곱 단위</td></tr>'


class TestBodyFormatShapes(unittest.TestCase):
    def test_pairs_with_header_and_rows_passes(self):
        self.assertEqual(codes(topic(f'<table class="pairs">{PAIRS_HEAD}<tbody>{PAIRS_ROW}</tbody></table>')), [])

    def test_pairs_needs_three_columns(self):
        row = '<tr><th>단위</th><td>제곱 단위</td></tr>'
        self.assertEqual(codes(topic(f'<table class="pairs">{PAIRS_HEAD}<tbody>{row}</tbody></table>')), ["pairs-shape"])

    def test_pairs_needs_header_row(self):
        self.assertEqual(codes(topic(f'<table class="pairs"><tbody>{PAIRS_ROW}{PAIRS_ROW}</tbody></table>')), ["pairs-shape"])

    def test_pairs_needs_a_body_row(self):
        self.assertEqual(codes(topic(f'<table class="pairs">{PAIRS_HEAD}</table>')), ["pairs-shape"])

    def test_chain_link_count(self):
        for n, expected in ((1, ["chain-shape"]), (2, []), (5, []), (6, ["chain-shape"])):
            with self.subTest(links=n):
                links = "".join(f"<li>고리{i}</li>" for i in range(n))
                self.assertEqual(codes(topic(f'<ol class="chain">{links}</ol>')), expected)

    def test_fold_needs_summary(self):
        self.assertEqual(codes(topic('<details class="more"><summary>더 자세히</summary><p>표기</p></details>')), [])
        self.assertEqual(codes(topic('<details class="more"><p>표기</p></details>')), ["fold-summary"])
        self.assertEqual(codes(topic('<details class="more"><summary> </summary><p>표기</p></details>')), ["fold-summary"])

    def test_prof_fold_title_counts_as_summary(self):
        body = '<div class="layer prof"><details><summary class="layer-title">교수님 말씀</summary><blockquote>"비유"</blockquote></details></div>'
        self.assertEqual(codes(topic(body)), [])

    def test_outside_topics_is_not_checked(self):
        source = '<html lang="ko"><body><ol class="chain"><li>하나</li></ol><details><p>x</p></details></body></html>'
        self.assertEqual(codes(source), [])

    def test_old_structure_still_passes(self):
        body = ('<div class="layer formal"><span class="layer-title">정확히 말하면</span><ol class="steps"><li>하나</li></ol></div>'
                '<div class="layer prof"><span class="layer-title">교수님 말씀</span><p>"말씀"</p></div>'
                '<div class="layer warn"><span class="layer-title">꼭 기억해요</span><p>구분</p></div>')
        self.assertEqual(codes(topic(body)), [])


class TestNewStructurePack(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = self.tmp / "run"
        shutil.copytree(MINI_RUN, self.run)
        section = self.run / "sections" / "s1.html"
        text = section.read_text(encoding="utf-8")
        old = re.search(r'      <article class="topic" id="s1-var">.*?</article>\n', text, re.S)
        self.assertIsNotNone(old)
        section.write_text(text.replace(old.group(0), NEW_TOPIC.read_text(encoding="utf-8")), encoding="utf-8")
        self.m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        self.note, self.review = assemble.assemble(self.run, self.tmp / "out")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_check_pack_passes(self):
        self.assertEqual([str(p) for p in check_html.check_pack(self.m, self.note, self.review)], [])

    def test_folded_prof_still_counts_as_layer(self):
        doc = check_html.parse_html(Path(self.note).read_text(encoding="utf-8"))
        self.assertIn("prof", doc.containers["s1-var"].child_classes)

    def test_markdown_keeps_tables_chain_and_folds(self):
        (note_md, review_md), _ = html2md.convert_pack(self.note, self.review)
        self.assertEqual(html2md.check_md(self.note, note_md), [])
        md = Path(note_md).read_text(encoding="utf-8")
        for expected in ("| 나타내는 것 | 값들의 가운데 | 퍼진 정도 |", "| 분산의 단위 | ~~원래 단위~~ | 원래 단위의 제곱 |",
                         "1. 평균 구하기", "<details><summary>더 자세히</summary>", "<details><summary>교수님 말씀</summary>"):
            with self.subTest(expected=expected):
                self.assertIn(expected, md)


if __name__ == "__main__":
    unittest.main()
