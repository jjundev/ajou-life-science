"""보강 모드(scripts/augment.py): 기존 카드·manifest 추출과 복습문제만 다시 조립."""

import json
from pathlib import Path
import shutil
import tempfile
import unicodedata
import unittest

from _util import MINI_RUN, REPO

import assemble
import augment


def fixture_pack(tmp: Path) -> Path:
    """mini-run을 조립한 팩 폴더(.pack 포함)."""
    pack = tmp / "pack"
    assemble.assemble(MINI_RUN, pack)
    return pack


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pack = fixture_pack(self.tmp)
        self.run = self.tmp / "run"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_extract_uses_pack_manifest(self):
        info = augment.extract(self.pack, self.run)
        self.assertFalse(info["reconstructed"])
        self.assertEqual(info["next_id"], "p3")
        self.assertEqual(info["parts"], {"partA": 1, "partB": 1})
        self.assertEqual(sorted(p.name for p in (self.run / "cards").iterdir()), ["p1.html", "p2.html"])
        card = (self.run / "cards" / "p2.html").read_text(encoding="utf-8")
        self.assertTrue(card.startswith('<article class="card" id="p2" data-source="기출 3강 7">'))
        self.assertTrue(card.endswith("</article>"))
        base = json.loads((self.run / "work" / "base-ids.json").read_text(encoding="utf-8"))
        self.assertEqual(base["p2"], {"part": "partB", "source": "기출 3강 7", "answer": "(2)"})
        self.assertEqual(json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))["forbidden_outside_preview"], ["d-separation"])

    def test_extract_reconstructs_without_pack(self):
        shutil.rmtree(self.pack / ".pack")
        info = augment.extract(self.pack, self.run)
        self.assertTrue(info["reconstructed"])
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["forbidden_outside_preview"], [])
        self.assertEqual(m["preview_topic"], "s2-next")
        self.assertEqual([s["id"] for s in m["sections"]], ["s1", "s2"])
        self.assertEqual(m["sections"][0]["short"], "1 기초")
        self.assertTrue(m["sections"][0]["topics"][1]["supp"])
        self.assertEqual([q["id"] for q in m["problems"]], ["p1", "p2"])
        self.assertEqual(m["problems"][1]["answer"], "(2)")
        self.assertIn("금지어 미복원", (self.run / "work" / "reconstructed.txt").read_text(encoding="utf-8"))

    def test_reconstruct_sees_note_gap_badge(self):
        note, review = augment.find_pack_files(self.pack)
        text = note.read_text(encoding="utf-8").replace("보충 · 수업에서 다루지 않았어요", "보충 · 노트에 빠졌던 수업 내용")
        note.write_text(text, encoding="utf-8")
        m = augment.reconstruct(note, review)
        self.assertTrue(m["sections"][0]["topics"][1]["supp"])

    def test_html_drift_from_pack_manifest_warns(self):
        _, review = augment.find_pack_files(self.pack)
        review.write_text(review.read_text(encoding="utf-8").replace("<h1>복습문제 2선 — 테스트</h1>", "<h1>복습문제 2선 — 손으로 고침</h1>"), encoding="utf-8")
        info = augment.extract(self.pack, self.run)
        self.assertTrue(any("manifest" in w for w in info["warnings"]), info["warnings"])

    def test_clean_pack_has_no_warnings(self):
        self.assertEqual(augment.extract(self.pack, self.run)["warnings"], [])

    def test_duplicate_review_files_stop(self):
        _, review = augment.find_pack_files(self.pack)
        (self.pack / "복습문제_0101-0102_Old_Copy.html").write_text(review.read_text(encoding="utf-8"), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.find_pack_files(self.pack)
        self.assertIn("둘 이상", str(cm.exception))

    def test_pack_manifest_mismatch_stops(self):
        m = json.loads((self.pack / ".pack" / "manifest.json").read_text(encoding="utf-8"))
        m["problems"] = [q for q in m["problems"] if q["id"] != "p2"]
        (self.pack / ".pack" / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.extract(self.pack, self.run)
        self.assertIn("p2", str(cm.exception))

    def test_nfd_file_names(self):
        for p in list(self.pack.iterdir()):
            if p.suffix == ".html":
                p.rename(self.pack / unicodedata.normalize("NFD", p.name))
        note, review = augment.find_pack_files(self.pack)
        self.assertEqual(unicodedata.normalize("NFC", review.name), "복습문제_0101-0102_Mini_Test.html")
        self.assertTrue(review.exists())
        self.assertEqual(augment.extract(self.pack, self.run)["next_id"], "p3")


def new_card(run: Path, pid: str, source: str) -> None:
    """fixture p2 카드를 복제해 새 카드를 만든다."""
    text = (run / "cards" / "p2.html").read_text(encoding="utf-8")
    text = text.replace('id="p2"', f'id="{pid}"').replace('data-source="기출 3강 7"', f'data-source="{source}"')
    text = text.replace("<h3>P2.", f"<h3>{pid.upper()}.")
    assert f'id="{pid}"' in text and source in text
    (run / "cards" / f"{pid}.html").write_text(text, encoding="utf-8")


def add_problem(run: Path, pid: str, part: str, source: str) -> None:
    m = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    m["problems"].append({"id": pid, "part": part, "source": source, "variant": part == "partC",
                          "anchor": "s1-mean", "level": 2, "date": "0101", "terms": ["정답: (2)"], "answer": "(2)"})
    (run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    new_card(run, pid, source)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pack = fixture_pack(self.tmp)
        self.run = self.tmp / "run"
        self.note, self.review = augment.find_pack_files(self.pack)
        self.original = self.review.read_text(encoding="utf-8")
        self.note_before = self.note.read_bytes()
        augment.extract(self.pack, self.run)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_round_trip_without_additions(self):
        result = augment.build(self.pack, self.run, today="2026-10-09")
        self.assertEqual(result["added"], [])
        self.assertEqual(self.review.read_text(encoding="utf-8"), self.original)
        self.assertEqual(self.note.read_bytes(), self.note_before)
        self.assertIn("- 2026-10-09 augment: 추가 없음", (self.pack / ".pack" / "log.md").read_text(encoding="utf-8"))

    def test_appends_new_problems_by_part(self):
        add_problem(self.run, "p3", "partC", "생성 변형 s1-mean")
        add_problem(self.run, "p4", "partA", "웹과제 2장 q01")
        result = augment.build(self.pack, self.run, today="2026-10-09")
        self.assertEqual(result["added"], ["p3", "p4"])
        html = self.review.read_text(encoding="utf-8")
        order = [m.group(1) for m in augment.CARD_RE.finditer(html)]
        self.assertEqual(order, ["p1", "p4", "p2", "p3"])
        self.assertIn('<section id="partC"><h2>C. 변형 연습</h2>', html)
        self.assertIn("<h1>복습문제 4선 — 테스트</h1>", html)
        self.assertIn("<p>테스트용 문제 <b>1개</b>입니다.</p>", html)  # 문항 수 표현이 없어 그대로
        self.assertTrue(any("review_intro" in w for w in result["warnings"]))
        self.assertIn("변형 연습은 수업 내용으로 만든 생성 문제입니다.", html)
        self.assertEqual(self.note.read_bytes(), self.note_before)
        saved = json.loads((self.pack / ".pack" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([q["id"] for q in saved["problems"]], ["p1", "p4", "p2", "p3"])

    def test_guard_rejects_changed_old_card(self):
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        m["problems"][1]["answer"] = "(3)"
        (self.run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.build(self.pack, self.run)
        self.assertIn("p2.answer", str(cm.exception))
        self.assertEqual(self.review.read_text(encoding="utf-8"), self.original)

    def test_guard_rejects_missing_card_and_low_new_id(self):
        (self.run / "cards" / "p1.html").unlink()
        m = json.loads((self.run / "manifest.json").read_text(encoding="utf-8"))
        m["problems"].append(dict(m["problems"][1], id="p0"))
        (self.run / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(augment.AugmentError) as cm:
            augment.build(self.pack, self.run)
        self.assertIn("p1: 카드 파일 없음", str(cm.exception))
        self.assertIn("p0: 새 문항 id는 p3부터", str(cm.exception))

    def test_second_augment_continues_numbering(self):
        add_problem(self.run, "p3", "partC", "생성 변형 s1-mean")
        augment.build(self.pack, self.run, today="2026-10-09")
        run2 = self.tmp / "run2"
        self.assertEqual(augment.extract(self.pack, run2)["next_id"], "p4")
        add_problem(run2, "p4", "partC", "생성 변형 s1-var")
        self.assertEqual(augment.build(self.pack, run2, today="2026-10-10")["added"], ["p4"])
        log = (self.pack / ".pack" / "log.md").read_text(encoding="utf-8")
        self.assertIn("2026-10-09 augment: 추가 p3", log)
        self.assertIn("2026-10-10 augment: 추가 p4", log)

    def test_cli_reports_failure(self):
        (self.run / "work" / "base-ids.json").unlink()
        self.assertEqual(augment.main(["build", str(self.pack), str(self.run)]), 1)


class TestRefreshTexts(unittest.TestCase):
    def manifest(self, intro, footer, parts):
        problems = []
        for part, n in parts.items():
            for i in range(n):
                src = "웹과제 4장 q01" if part == "partA" else ("생성 변형 s1-a" if part == "partC" else "기출 4강 1")
                problems.append({"id": f"{part}{i}", "part": part, "source": src})
        return {"review_title": "복습문제 1선 — 1001 수업 범위", "review_intro": intro,
                "footer_review": footer, "problems": problems}

    def test_counts_only_digits_change(self):
        m = self.manifest("웹과제 6문항, 기출 23문항, 생성 변형 15문항이에요. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.",
                          "출처: 기출(3강 합본) · 웹과제(3장). 변형 연습은 수업 내용으로 만든 생성 문제입니다.",
                          {"partA": 7, "partB": 23, "partC": 16})
        self.assertEqual(augment.refresh_texts(m, {"partA", "partB", "partC"}), [])
        self.assertEqual(m["review_title"], "복습문제 46선 — 1001 수업 범위")
        self.assertEqual(m["review_intro"], "웹과제 7문항, 기출 23문항, 생성 변형 16문항이에요. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.")
        self.assertEqual(m["footer_review"], "출처: 기출(3강 합본) · 웹과제(4장). 변형 연습은 수업 내용으로 만든 생성 문제입니다.")

    def test_refresh_inserts_new_part_phrases(self):
        m = self.manifest("기출 <b>20개</b>와 변형 연습 <b>6개</b>입니다. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.",
                          "출처: 2023·2024 생명과학 기출(4·5강 합본). 정답은 대조했습니다. 변형 연습은 수업 내용으로 만든 생성 문제입니다.",
                          {"partA": 3, "partB": 20, "partC": 8})
        self.assertEqual(augment.refresh_texts(m, {"partB", "partC"}), [])
        self.assertEqual(m["review_intro"], "웹과제 <b>3개</b>, 기출 <b>20개</b>와 변형 연습 <b>8개</b>입니다. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.")
        self.assertEqual(m["footer_review"], "출처: 2023·2024 생명과학 기출(4·5강 합본) · 웹과제(4장). 정답은 대조했습니다. 변형 연습은 수업 내용으로 만든 생성 문제입니다.")

    def test_intro_without_counts_is_left_alone(self):
        intro = "먼저 풀어 보고, 막히면 힌트를 열어 보세요. 원문이 모호한 문항은 풀이에서 구분해요."
        m = self.manifest(intro, "출처: 기출(4강 합본).", {"partB": 2, "partC": 1})
        warnings = augment.refresh_texts(m, {"partB"})
        self.assertEqual(m["review_intro"], intro)
        self.assertTrue(any("review_intro" in w for w in warnings))

    def test_existing_part_without_count_phrase_warns(self):
        intro = "기출을 먼저 풀고 변형으로 확인해요."
        m = self.manifest(intro, "출처: 기출(4강 합본). 변형 연습은 수업 내용으로 만든 생성 문제입니다.", {"partB": 15, "partC": 6})
        warnings = augment.refresh_texts(m, {"partB", "partC"})
        self.assertEqual(m["review_intro"], intro)
        self.assertTrue(any("기출" in w for w in warnings), warnings)
        self.assertTrue(any("생성 변형" in w for w in warnings), warnings)

    def test_ensure_parts_orders_defaults(self):
        m = {"parts": [{"id": "partB", "title": "B. 기출", "short": "B 기출"}],
             "problems": [{"part": "partC"}, {"part": "partA"}, {"part": "partB"}]}
        augment.ensure_parts(m)
        self.assertEqual([p["id"] for p in m["parts"]], ["partA", "partB", "partC"])
        self.assertEqual(m["parts"][0], {"id": "partA", "title": "A. 웹과제", "short": "A 웹과제"})


class TestReconstructRealPacks(unittest.TestCase):
    """저장소의 실제 팩마다: HTML에서 복원한 manifest로 다시 조립하면 원본과 바이트까지 같다."""

    def test_round_trip_from_html(self):
        packs = sorted(p for p in (REPO / "복습노트").iterdir() if p.is_dir() and not p.name.startswith("."))
        checked = 0
        for pack in packs:
            try:
                note, review = augment.find_pack_files(pack)
            except augment.AugmentError:
                continue
            with self.subTest(pack=pack.name), tempfile.TemporaryDirectory() as tmp:
                m = augment.reconstruct(note, review)
                run = Path(tmp)
                (run / "cards").mkdir()
                html = review.read_text(encoding="utf-8")
                for c in augment.CARD_RE.finditer(html):
                    (run / "cards" / f"{c.group(1)}.html").write_text(c.group(0), encoding="utf-8")
                self.assertEqual(assemble.build_review(m, run), html)
                checked += 1
        self.assertGreater(checked, 0)


class TestAugmentRealPacks(unittest.TestCase):
    """.pack이 있는 실제 팩: 복사본에서 extract → build(추가 없음)가 원본 복습문제와 같다."""

    def test_round_trip_with_pack_records(self):
        checked = 0
        for pack in sorted((REPO / "복습노트").iterdir()):
            if not (pack / ".pack" / "manifest.json").is_file():
                continue
            with self.subTest(pack=pack.name), tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / pack.name
                shutil.copytree(pack, copy, ignore=shutil.ignore_patterns("풀이기록"))
                _, review = augment.find_pack_files(copy)
                original = review.read_text(encoding="utf-8")
                augment.extract(copy, Path(tmp) / "run")
                augment.build(copy, Path(tmp) / "run", today="2026-10-09")
                self.assertEqual(review.read_text(encoding="utf-8"), original)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
