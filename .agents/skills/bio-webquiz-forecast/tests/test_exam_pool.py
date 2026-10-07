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


if __name__ == "__main__":
    unittest.main()
