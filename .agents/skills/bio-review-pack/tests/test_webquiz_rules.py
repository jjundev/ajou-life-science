"""웹과제형 변형 연습 규칙(webquiz-style.md와 관련 규칙 문장)을 고정한다."""

import re
import unittest

from _util import SKILL

REFS = SKILL / "references"
TYPES = ("쌍둥이", "그림", "상황 전이", "ㄱㄴㄷ", "용어 바꿔 쓰기")


def read(path):
    return path.read_text(encoding="utf-8")


def section(text, heading):
    """`heading` 줄부터 같은 수준 이상의 다음 제목 전까지."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading)
    rest = text[start + len(heading):]
    m = re.search(rf"\n#{{1,{level}}} ", rest)
    return heading + (rest[: m.start()] if m else rest)


class TestWebquizStyle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(REFS / "webquiz-style.md")

    def test_sections(self):
        for h in ("## 1. 출처", "## 2. 수치", "## 3. 유형", "## 4. 할당", "## 5. 갱신"):
            with self.subTest(h=h):
                self.assertIn(f"\n{h}\n", self.text)

    def test_types_have_four_parts(self):
        body = section(self.text, "## 3. 유형")
        for t in TYPES:
            with self.subTest(t=t):
                part = section(body, f"### {t}")
                for label in ("정의:", "실제 예:", "만드는 법:", "피할 것:"):
                    self.assertIn(label, part)

    def test_evidence_numbers(self):
        body = section(self.text, "## 2. 수치")
        for s in ("46", "70%", "33%", "17%"):
            with self.subTest(s=s):
                self.assertIn(s, body)

    def test_twin_guards(self):
        twin = section(section(self.text, "## 3. 유형"), "### 쌍둥이")
        self.assertIn("발문은 글자 그대로", twin)
        self.assertIn("보기 5개는 새로 쓴다", twin)
        self.assertIn("금지어", twin)
        self.assertIn("같은 팩 partA", twin)

    def test_quota(self):
        q = section(self.text, "## 4. 할당")
        for s in ("10~15개", "토픽당 최대 3개", "쌍둥이 2", "그림 2", "상황 전이 2", "ㄱㄴㄷ 1",
                  "용어 바꿔 쓰기 2", "약 1/3", "보기는 5개", "만들 수 없으면 0개", "못 채우면"):
            with self.subTest(s=s):
                self.assertIn(s, q)

    def test_update_is_proposal_only(self):
        u = section(self.text, "## 5. 갱신")
        self.assertIn("webquiz-style.md 갱신 제안", u)
        self.assertIn("이 파일은 고치지 않는다", u)


class TestSelectionRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s6 = section(read(REFS / "problem-selection.md"), "## 6. 변형 연습")
        cls.cards = read(REFS / "card-rules.md")

    def test_section6_points_to_style(self):
        self.assertIn("`references/webquiz-style.md`", self.s6)
        self.assertIn("10~15개", self.s6)
        self.assertIn("못 채우면", self.s6)
        self.assertNotIn("3~8개", self.s6)

    def test_twin_exception_and_five_options(self):
        self.assertIn("쌍둥이는 발문만 원문 그대로", self.s6)
        self.assertIn("보기는 5개가 기본", self.s6)
        self.assertNotIn("보기 수는 원문 형식에 맞출 필요가 없다", self.s6)

    def test_variants_table_has_type_column(self):
        self.assertIn("| id | 혼동 묶음 | 웹과제 유형 | 형태 |", self.s6)
        for v in ("`쌍둥이`", "`그림`", "`상황`", "`ㄱㄴㄷ`", "`없음`", "`+부정형`", "`+용어`"):
            with self.subTest(v=v):
                self.assertIn(v, self.s6)

    def test_card_rules_for_twin_and_statements(self):
        self.assertIn("정답을 바꾼 생성 변형이에요", self.cards)
        self.assertIn("원문 정답과 달라진 점", self.cards)
        self.assertIn("`ㄱ.`~`ㄷ.`", self.cards)


class TestReportRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = read(SKILL / "SKILL.md")
        # 9단계 안 코드 블록에 "## 복습팩 …" 줄이 있어 section()은 거기서 끊긴다. 다음 절 제목까지 직접 자른다.
        cls.report = cls.skill[cls.skill.index("### 9. 보고"):cls.skill.index("## 오류 처리")]

    def test_report_counts_types(self):
        self.assertIn("변형 v (쌍둥이 a · 그림 b · 상황 c · ㄱㄴㄷ d · 부정형 e)", self.report)
        self.assertIn("0개인 유형은 사유", self.report)

    def test_report_mentions_style_update(self):
        self.assertIn("webquiz-style.md 갱신 제안", self.report)
        self.assertIn("풀이기록", self.report)

    def test_regeneration_protects_card_ids(self):
        # 다시 만들 때 카드 번호가 바뀌면 interactive-overrides.json(카드 id 키)과 풀이기록이 엉뚱한 문항에 붙는다
        self.assertIn("interactive-overrides.json", self.report)
        self.assertIn("기존 카드 번호를 유지", self.report)
        self.assertIn("git", self.report)


if __name__ == "__main__":
    unittest.main()
