import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _util import SCRIPTS, card_html, exam_card_html, make_repo, write_pool
import blind
import exam_pool


class TestExamPool(unittest.TestCase):
    def test_load_pool_filters_chapter_and_answerless(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [
                exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 2, "p1"),
                exam_card_html("기출 8강 1", "다른 장?", list("가나다라마"), 1, "p2"),
                exam_card_html("기출 9강 2", "발문 2?", list("가나다라마"), 3, "p3").replace("정답: (3)", "정답 없음"),
            ])
            pool = exam_pool.load_pool(repo, 9)
            self.assertEqual(list(pool), ["기출 9강 1"])
            self.assertEqual(pool["기출 9강 1"]["options"][pool["기출 9강 1"]["answer_index"]], "나")

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 2)])
            out = subprocess.run([sys.executable, str(SCRIPTS / "exam_pool.py"), str(repo), "9"],
                                 capture_output=True, text=True, encoding="utf-8", check=True).stdout
            self.assertEqual(json.loads(out)[0]["answer"], "나")

    def test_blind_hides_answers(self):
        md = blind.blind_markdown(card_html(1, "B", stem="무엇일까?"))
        self.assertIn("## P1. [예상] 제목 1", md)
        self.assertIn("무엇일까?", md)
        self.assertIn("- B. 보기 1B", md)
        for leaked in ("정답", "맞아요", "틀려요", "힌트"):
            self.assertNotIn(leaked, md)


    def test_pool_skips_answer_outside_options(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 6)])
            self.assertEqual(exam_pool.load_pool(repo, 9), {})

    def test_blind_keeps_figure_and_extra_text(self):
        html = card_html(1, "B", stem="그림을 보고 답하세요.").replace(
            '<ul class="choices">',
            '<figure class="figure"><svg viewBox="0 0 340 200" role="img" aria-label="염색체 (가)~(라) 그림"></svg></figure>'
            '<p>단, 교차는 없어요.</p><div class="table-wrap"><table><tr><td>표 칸</td></tr></table></div>'
            '<ul class="choices">')
        md = blind.blind_markdown(html)
        for kept in ("염색체 (가)~(라) 그림", "단, 교차는 없어요.", "표 칸"):
            self.assertIn(kept, md)

    def test_cli_out_writes_utf8_file_and_creates_dir(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            write_pool(repo, [exam_card_html("기출 9강 1", "발문 1?", list("가나다라마"), 2)])
            out = Path(t) / "run" / "pool.json"
            subprocess.run([sys.executable, str(SCRIPTS / "exam_pool.py"), str(repo), "9", "--out", str(out)],
                           capture_output=True, check=True)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))[0]["answer"], "나")

if __name__ == "__main__":
    unittest.main()
