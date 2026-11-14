import json
import tempfile
import unittest
from pathlib import Path

from _util import card_html, exam_card_html, make_repo, make_set, overview_html, write_pool
import build
import check

ANSWERS = "ABCDE"


def base_cards(**over):
    cards = {"o1": overview_html()}
    cards.update({f"p{i}": card_html(i, ANSWERS[i - 1]) for i in range(1, 6)})
    cards.update(over)
    return cards


def codes(problems):
    return {p.split("]")[0].lstrip("[") for p in problems}


class TestCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def built(self, version=1, cards=None, extra=None):
        return build.build(make_set(self.repo, 9, version, cards or base_cards(), extra))

    def test_clean_set_passes(self):
        self.assertEqual(check.check(self.built()), [])

    def test_optional_types_zero(self):
        out = self.built(extra={"types_required": {"ㄱㄴㄷ": 0, "장섞기": 0}})
        self.assertEqual(check.check(out), [])

    def test_stale(self):
        out = self.built()
        (out.parent / ".pack" / "v1" / "cards" / "p1.html").write_text(
            card_html(1, "A", stem="바뀐 발문?"), encoding="utf-8")
        self.assertIn("stale", codes(check.check(out)))

    def test_answer_spread(self):
        cards = base_cards(p2=card_html(2, "A"))
        self.assertIn("answer-spread", codes(check.check(self.built(cards=cards))))

    def test_negative_double_wrong(self):
        bad = card_html(1, "A", types="부정형").replace("<li>B. 맞아요", "<li>B. 틀려요")
        self.assertIn("diagnosis", codes(check.check(self.built(cards=base_cards(p1=bad)))))

    def test_forbidden_word(self):
        cards = base_cards(p1=card_html(1, "A", stem="금지어가 든 발문?"))
        self.assertIn("wording", codes(check.check(self.built(cards=cards))))

    def test_types_required(self):
        out = self.built(extra={"types_required": {"그림": 1}})
        self.assertIn("types", codes(check.check(out)))

    def test_stem_dup_across_versions(self):
        self.built(version=1)
        self.assertIn("stem-dup", codes(check.check(self.built(version=2))))

    def exam_extra(self, mode, p1):
        write_pool(self.repo, [exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2)])
        extra = {"legacy": False, "exam_sources": {"p1": {"source": "기출 9강 7", "mode": mode}},
                 "exam_counts": {mode: 1}}
        return self.built(cards=base_cards(p1=p1), extra=extra)

    def test_exam_verbatim_ok(self):
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        self.assertEqual(check.check(self.exam_extra("기출그대로", p1)), [])

    def test_exam_verbatim_mismatch(self):
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "바"])
        self.assertIn("exam-verbatim", codes(check.check(self.exam_extra("기출그대로", p1))))

    def test_exam_twin_same_answer(self):
        p1 = card_html(1, "A", kind="기출 변형", stem="기출 발문?", options=["나", "x", "y", "z", "w"])
        self.assertIn("exam-twin", codes(check.check(self.exam_extra("기출쌍둥이", p1))))

    def test_exam_reuse_across_versions(self):
        write_pool(self.repo, [exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2)])
        self.built(version=1, extra={"used_exam_sources": ["기출 9강 7"]})
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        cards = base_cards(p1=p1, **{f"p{i}": card_html(i, ANSWERS[i - 1], stem=f"v2 발문 {i}?") for i in range(2, 6)})
        out = self.built(version=2, cards=cards, extra={
            "legacy": False, "exam_sources": {"p1": {"source": "기출 9강 7", "mode": "기출그대로"}},
            "exam_counts": {"기출그대로": 1}})
        self.assertIn("exam-reuse", codes(check.check(out)))

    def test_webquiz_copy(self):
        q = self.repo / "웹과제" / "9장" / "questions.json"
        q.parent.mkdir(parents=True)
        q.write_text(json.dumps([{"original": {"content": [{"type": "text", "text": "문제 3번 발문이다?"}]}}],
                                ensure_ascii=False), encoding="utf-8")
        self.assertIn("webquiz-copy", codes(check.check(self.built())))


    def test_exam_same_source_twice_in_set(self):
        write_pool(self.repo, [exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2)])
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        p2 = card_html(2, "B", kind="기출 예상", stem="기출 발문?", options=["가", "나", "다", "라", "마"])
        out = self.built(cards=base_cards(p1=p1, p2=p2), extra={
            "legacy": False, "exam_counts": {"기출그대로": 2},
            "exam_sources": {"p1": {"source": "기출 9강 7", "mode": "기출그대로"},
                             "p2": {"source": "기출 9강 7", "mode": "기출그대로"}}})
        self.assertIn("exam-reuse", codes(check.check(out)))

    def test_exam_same_question_other_number_across_versions(self):
        write_pool(self.repo, [
            exam_card_html("기출 9강 7", "기출 발문?", ["가", "나", "다", "라", "마"], 2, "p1"),
            exam_card_html("기출 9강 8", "기출 발문?", ["가", "나", "다", "라", "마"], 2, "p2")])
        self.built(version=1, extra={"used_exam_sources": ["기출 9강 7"]})
        p1 = card_html(1, "A", kind="기출 예상", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        cards = base_cards(p1=p1, **{f"p{i}": card_html(i, ANSWERS[i - 1], stem=f"v2 발문 {i}?") for i in range(2, 6)})
        out = self.built(version=2, cards=cards, extra={
            "legacy": False, "exam_sources": {"p1": {"source": "기출 9강 8", "mode": "기출그대로"}},
            "exam_counts": {"기출그대로": 1}})
        self.assertIn("exam-reuse", codes(check.check(out)))

    def test_exam_number_mode_must_change_something(self):
        p1 = card_html(1, "A", kind="기출 변형", stem="기출 발문?", options=["나", "가", "다", "라", "마"])
        self.assertIn("exam-number", codes(check.check(self.exam_extra("기출숫자", p1))))

    def test_exam_number_mode_changed_passes(self):
        p1 = card_html(1, "A", kind="기출 변형", stem="바뀐 숫자의 기출 발문?", options=["나", "가", "다", "라", "마"])
        self.assertEqual(check.check(self.exam_extra("기출숫자", p1)), [])

    def _titled(self, title, options, answer="A", stem=None):
        html = card_html(1, answer, options=options, stem=stem)
        return html.replace("P1. [예상] 제목 1", f"P1. [예상] {title}")

    def test_title_leak_term_answer_fails(self):
        p1 = self._titled("창시자 효과와 기대 빈도", ["창시자 효과", "병목 효과", "유전자 흐름", "돌연변이", "자연 선택"])
        problems = check.check(self.built(cards=base_cards(p1=p1)))
        self.assertIn("title-leak", codes(problems))

    def test_title_leak_two_words_in_sentence_answer_fails(self):
        opts = ["최근 공통조상을 공유할수록 DNA 유사성이 높다고 본다", "몸 크기가 비슷하면 가깝다",
                "서식지가 같으면 가깝다", "화석이 많으면 가깝다", "색이 같으면 가깝다"]
        p1 = self._titled("공통조상과 유사성", opts)
        self.assertIn("title-leak", codes(check.check(self.built(cards=base_cards(p1=p1)))))

    def test_neutral_or_stem_shared_title_passes(self):
        opts = ["창시자 효과", "병목 효과", "유전자 흐름", "돌연변이", "자연 선택"]
        neutral = self._titled("작은 집단이 새로 만든 섬의 빈도", opts)
        self.assertNotIn("title-leak", codes(check.check(self.built(cards=base_cards(p1=neutral)))))
        in_stem = self._titled("창시자 효과", opts, stem="다음 중 창시자 효과에 해당하는 것은?")
        self.assertNotIn("title-leak", codes(check.check(self.built(version=2, cards=base_cards(p1=in_stem)))))

    def test_single_generic_word_in_sentence_answer_passes(self):
        opts = ["두 종은 서로 다른 시기에 번식해 교배하지 못한다", "두 종은 크기가 같다",
                "두 종은 먹이가 같다", "두 종은 색이 같다", "두 종은 서식지가 같다"]
        p1 = self._titled("번식 장벽의 종류", opts)
        self.assertNotIn("title-leak", codes(check.check(self.built(cards=base_cards(p1=p1)))))

    def test_hint_must_be_open_and_non_hint_closed(self):
        closed_hint = card_html(1, "A").replace('<details class="hint" open>', '<details class="hint">')
        self.assertIn("hint-open", codes(check.check(self.built(cards=base_cards(p1=closed_hint)))))
        open_sol = card_html(1, "A").replace('<details class="solution">', '<details class="solution" open>')
        self.assertIn("open-details", codes(check.check(self.built(version=2, cards=base_cards(p1=open_sol)))))


if __name__ == "__main__":
    unittest.main()
