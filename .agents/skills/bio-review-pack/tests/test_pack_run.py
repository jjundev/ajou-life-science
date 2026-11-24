"""pack_run.py: 서브에이전트 TSV 기록을 합쳐 메인에 몇 줄만 돌려주는지 확인한다."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from _util import MINI_RUN, SKILL

import manifest
import pack_run


class PackRunCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / "run"
        shutil.copytree(MINI_RUN, self.run)
        self.reports = self.run / "work" / "reports"
        self.reports.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, rows):
        (self.reports / name).write_text("".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")


class TestContext(PackRunCase):
    def test_section_gets_its_own_values(self):
        text = pack_run.context(self.run, "s1")
        self.assertIn("s1-mean", text)
        self.assertIn("기출 3강 7", text)          # anchor가 이 섹션인 문항
        self.assertIn("자매염색분체", text)          # 판별 용어
        self.assertNotIn("정답:", text)             # 정답은 작성자에게 주지 않는다
        self.assertIn("d-separation", text)         # 금지어
        self.assertNotIn("복습문제_0101", text)      # 다른 섹션의 링크

    def test_unknown_section_fails(self):
        with self.assertRaises(pack_run.RunError):
            pack_run.context(self.run, "s9")


class TestAuditMerge(PackRunCase):
    def test_merges_rows_and_reports_only_defects(self):
        self.put("rows-s1.tsv", [
            ["# 토픽", "본문의 핵심 주장", "대응하는 요약 문장", "판정·생략 이유"],
            ["s1-var", "분산은 퍼진 정도", "분산은 퍼진 정도예요", "반영"],
            ["s1-mean", "첫 문장 검토: 평균=무게중심", "평균은 무게중심이에요", "통과"],
            ["s1-mean", "평균은 합을 개수로 나눈다", "", "누락: 요약에 정의가 없음"],
        ])
        out = pack_run.audit_merge(self.run)
        table = (self.run / "summary-audit.md").read_text(encoding="utf-8")
        self.assertIn("| 토픽 | 본문의 핵심 주장 | 대응하는 요약 문장 | 판정·생략 이유 |", table)
        self.assertLess(table.index("s1-mean"), table.index("s1-var"))  # manifest 토픽 순서
        self.assertIn("누락/수정 필요 1", out[0])
        self.assertIn("- s1-mean: 누락", "\n".join(out))
        self.assertIn("- s1-var: 첫 문장 검토 없음", out)
        self.assertLessEqual(len(out), pack_run.MAX_LINES + 1)
        findings = (self.reports / "findings-audit.tsv").read_text(encoding="utf-8")
        self.assertIn("important\ts1-mean", findings)

    def test_no_rows_is_an_error(self):
        with self.assertRaises(pack_run.RunError):
            pack_run.audit_merge(self.run)


class TestBlindCheck(PackRunCase):
    def test_compares_answers_and_levels(self):
        self.put("blind.tsv", [
            ["p1", "3/2", "s1-mean", "", "합 → 나누기", "1"],
            ["p2", "근거 없음", "—", "보기 (3)의 근거가 노트에 없음", "판정 불가", "판정 불가"],
        ])
        out = pack_run.blind_check(self.run)
        self.assertIn("1/2 풀림", out[0])
        self.assertIn("p2", out[1])
        self.assertIn("anchor s1-var", out[1])
        self.assertTrue((self.run / "blind-results.md").is_file())
        findings = (self.reports / "findings-blind.tsv").read_text(encoding="utf-8")
        self.assertTrue(findings.startswith("critical\ts1-var\t"))  # 원문은 anchor 토픽의 섹션 작성자에게

    def test_variant_goes_to_card_first(self):
        self.put("blind.tsv", [["p1", "2", "", "정답이 둘", "", "1"]])
        pack_run.blind_check(self.run)
        self.assertTrue((self.reports / "findings-blind.tsv").read_text(encoding="utf-8").startswith("critical\tp1\t"))

    def test_all_solved_leaves_no_findings(self):
        self.put("blind.tsv", [["p1", "3/2", "s1-mean", "", "", "1"], ["p2", "( 2 )", "s1-var", "", "", "1"]])
        out = pack_run.blind_check(self.run)
        self.assertEqual(len(out), 1)
        self.assertIn("문항 이의 미기록 2", out[0])
        self.assertFalse((self.reports / "findings-blind.tsv").exists())

    def test_matching_answer_with_objection_goes_to_card_writer(self):
        self.put("blind.tsv", [["p1", "3/2", "s1-mean", "", "합 → 나누기", "1", "조건이 빠져 2도 성립"]])
        out = pack_run.blind_check(self.run)
        self.assertIn("1/1 풀림", out[0])
        self.assertIn("문항 이의 1", out[0])
        pack_run.fixes(self.run)
        path = self.run / "work" / "fixes" / "cards-p1.txt"
        self.assertTrue(path.is_file())
        self.assertIn("조건이 빠져 2도 성립", path.read_text(encoding="utf-8"))

    def test_original_with_objection_and_mismatched_answer_has_one_card_finding(self):
        self.put("blind.tsv", [["p2", "(3)", "s1-var", "", "", "1", "보기 (2)도 성립"]])
        pack_run.blind_check(self.run)
        findings = (self.reports / "findings-blind.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].startswith("critical\tp2\t"))
        self.assertIn("보기 (2)도 성립", findings[0])
        self.assertIn("리뷰어 (3)", findings[0])
        self.assertIn("key-check.md", findings[0])

    def test_recheck_clears_resolved_objection(self):
        self.put("blind.tsv", [["p1", "3/2", "s1-mean", "", "", "1", "2도 성립"]])
        pack_run.blind_check(self.run)
        self.assertTrue((self.reports / "findings-blind.tsv").is_file())

        self.put("blind.tsv", [["p1", "3/2", "s1-mean", "", "", "1", "없음"]])
        out = pack_run.blind_check(self.run)
        self.assertIn("문항 이의 0", out[0])
        self.assertIn("문항 이의 미기록 0", out[0])
        self.assertFalse((self.reports / "findings-blind.tsv").exists())


class TestFixes(PackRunCase):
    def test_routes_findings_to_owners(self):
        self.put("findings-general.tsv", [
            ["Critical", "[s1-mean]", "정의가 틀림", "합을 개수로 나눈다고 고친다"],
            ["important", "p2", "보기 진단 없음", "보기 (4) 진단을 더한다"],
            ["minor", "s1-var", "문장이 길다", "나눈다"],
            ["minor-easy", "s2", "오타", "고친다"],
            ["important", "x9-none", "알 수 없는 id", "?"],
        ])
        out = pack_run.fixes(self.run)
        fixes = self.run / "work" / "fixes"
        self.assertEqual(sorted(p.name for p in fixes.iterdir()), ["cards-p1.txt", "s1.txt", "s2.txt"])
        self.assertIn("정의가 틀림", (fixes / "s1.txt").read_text(encoding="utf-8"))
        self.assertNotIn("문장이 길다", (fixes / "s1.txt").read_text(encoding="utf-8"))
        text = "\n".join(out)
        self.assertIn("수정 요청 3건", text)
        self.assertIn("담당을 못 찾은 결함 1건", text)
        self.assertIn("반영하지 않는 minor 1건", text)
        self.assertEqual(len((self.reports / "unapplied.tsv").read_text(encoding="utf-8").splitlines()), 2)

    def test_card_groups_are_tens(self):
        self.assertEqual([pack_run.card_group(p) for p in ("p1", "p10", "p11", "p25")],
                         ["cards-p1", "cards-p1", "cards-p11", "cards-p21"])


class TestMergeProblems(PackRunCase):
    def test_problems_and_topic_requests_enter_manifest(self):
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        problems = m["problems"]
        m["problems"] = []
        (self.run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        (self.run / "work" / "problems.json").write_text(json.dumps({
            "problems": problems,
            "topic_requests": [{"topic": "s1-mean", "add_terms": ["무게중심", "산술평균"], "supp": True, "why": "p1 판별"}],
        }, ensure_ascii=False), encoding="utf-8")
        out = pack_run.merge_problems(self.run)
        merged = manifest.load(self.run / "manifest.json")
        self.assertEqual(len(merged["problems"]), 2)
        topic = merged["sections"][0]["topics"][0]
        self.assertEqual(topic["required_terms"].count("무게중심"), 1)
        self.assertIn("산술평균", topic["required_terms"])
        self.assertTrue(topic["supp"])
        self.assertIn("문항 2개 반영", out[0])

    def test_unknown_anchor_is_rejected(self):
        (self.run / "work" / "problems.json").write_text(json.dumps({"problems": [{"id": "p1", "anchor": "s9-x"}]}), encoding="utf-8")
        with self.assertRaises(pack_run.RunError):
            pack_run.merge_problems(self.run)


class TestFeedbackAndStatus(PackRunCase):
    def test_feedback_section_is_replaced_not_appended(self):
        (self.run / "note-feedback-audit.md").write_text("# 계획\n\n| ID | 범위 |\n|---|---|\n| q01 | 이번 |\n", encoding="utf-8")
        self.put("feedback-s1.tsv", [["q01", "s1-mean", "평균은 무게중심이에요", "본문 반영"]])
        pack_run.feedback_merge(self.run)
        out = pack_run.feedback_merge(self.run)
        text = (self.run / "note-feedback-audit.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(pack_run.APPLIED_HEAD), 1)
        self.assertIn("| q01 | 이번 |", text)
        self.assertIn("본문 반영 1", out[0])

    def test_status_is_short(self):
        out = pack_run.status(self.run)
        self.assertLessEqual(len(out), 8)
        self.assertIn("문항 2", out[1])

    def test_cli_reports_failure(self):
        self.assertEqual(pack_run.main(["audit-merge", "--run", str(self.run)]), 1)


class TestContractDocumented(unittest.TestCase):
    def test_contract_names_the_report_files(self):
        text = (SKILL / "references" / "report-contract.md").read_text(encoding="utf-8")
        for s in ("work/reports/", "rows-<sid>.tsv", "findings-<이름>.tsv", "blind.tsv", "feedback-<sid>.tsv",
                  "영수증", "pack_run.py", "Bash"):
            with self.subTest(s=s):
                self.assertIn(s, text)

    def test_briefs_point_to_the_contract(self):
        for name in ("content-rules.md", "card-rules.md", "review-prompt.md", "stt-summary-prompt.md", "problem-selection.md"):
            with self.subTest(name=name):
                self.assertIn("report-contract.md", (SKILL / "references" / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
