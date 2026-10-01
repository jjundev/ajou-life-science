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


if __name__ == "__main__":
    unittest.main()
