import unittest

from _util import card_html, exam_card_html, overview_html
import cards


class TestCards(unittest.TestCase):
    def test_norm_and_text(self):
        self.assertEqual(cards.norm(" A형, B형 (가)! "), "A형B형가")
        self.assertEqual(cards.text("<p>가 <b>나</b></p>\n<p>다</p>"), "가 나 다")

    def test_parse_forecast_card(self):
        c = cards.parse_cards(card_html(3, "C", types="부정형 계산"))["p3"]
        self.assertEqual(c["types"], ["부정형", "계산"])
        self.assertEqual(c["title"], "P3. [예상] 제목 3")
        self.assertEqual(c["stem"], "문제 3번 발문이다?")
        self.assertEqual(c["options"], [f"보기 3{x}" for x in "ABCDE"])
        self.assertEqual((c["answer_index"], c["answer_label"]), (2, "C"))
        self.assertEqual([d for d, _ in c["diagnoses"]], list("ABCDE"))
        self.assertEqual(dict(c["diagnoses"])["C"], "틀려요")

    def test_parse_exam_card(self):
        c = cards.parse_cards(exam_card_html("기출 9강 1", "기출 발문?", ["가", "나", "다", "라", "마"], 2))["p1"]
        self.assertEqual(c["source"], "기출 9강 1")
        self.assertEqual(c["options"], ["가", "나", "다", "라", "마"])
        self.assertEqual((c["answer_index"], c["answer_label"]), (1, "2"))

    def test_overview_has_no_options(self):
        c = cards.parse_cards(overview_html())["o1"]
        self.assertEqual((c["options"], c["answer_index"]), ([], None))


if __name__ == "__main__":
    unittest.main()
