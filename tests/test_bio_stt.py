import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents/skills/bio-stt"
CLAUDE_DIR = ROOT / ".claude/skills/bio-stt"

class BioSttTests(unittest.TestCase):
    def setUp(self):
        # We import from .agents/skills/bio-stt/scripts/infer_context.py
        import sys
        scripts_dir = str(SKILL_DIR / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

    def test_01_skill_entrypoints_and_metadata(self):
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "SKILL.md must exist in .agents/skills/bio-stt/")
        # Ensure it is NOT linked into .claude/skills (disallow Claude)
        self.assertFalse(CLAUDE_DIR.exists(), ".claude/skills/bio-stt must NOT exist (disallow Claude)")

        content = skill_md.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "SKILL.md must have frontmatter")
        import yaml
        frontmatter = yaml.safe_load(content.split("---")[1])
        self.assertEqual(frontmatter.get("name"), "bio-stt")
        self.assertIn("Gemini Only", frontmatter.get("description", ""))
        self.assertIn("Model Compatibility Gate", content, "SKILL.md must contain Model Compatibility Gate")
        self.assertIn("STT/<MMDD> 생명.md", content, "SKILL.md must document standard output path")

    def test_02_parse_date(self):
        from infer_context import parse_date

        self.assertEqual(parse_date("20261006_생명.m4a"), "1006")
        self.assertEqual(parse_date("1006 생명.mp3"), "1006")
        self.assertEqual(parse_date("1006.m4a"), "1006")
        self.assertEqual(parse_date("녹음_1001.wav"), "1001")
        self.assertEqual(parse_date("/path/to/2026-0929-class.m4a"), "0929")
        self.assertEqual(parse_date("audio.m4a", date_override="1006"), "1006")

        with self.assertRaises(ValueError):
            parse_date("audio_without_date.m4a")

    def test_03_infer_chapter(self):
        from infer_context import infer_chapter

        # 1006 has 예습노트/1006 covering 5장
        ch_1006 = infer_chapter(ROOT, "1006")
        self.assertEqual(ch_1006, 5)

        # 1001 has 복습노트/1001 ending 4장 and starting 5장
        ch_1001 = infer_chapter(ROOT, "1001")
        self.assertIn(ch_1001, [4, 5])

    def test_03b_infer_chapter_reads_chapter_close_from_assets(self):
        from infer_context import infer_chapter

        # 3장 마감을 쓰는 이유: 기본 fallback(5장)과 구분되도록 (3 + 1 = 4)
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            assets = repo / "복습노트/1001/.assets"
            assets.mkdir(parents=True)
            (assets / "장마감_1001_3장.md").write_text("x", encoding="utf-8")
            self.assertEqual(infer_chapter(repo, "1006"), 4)
            self.assertEqual(infer_chapter(repo, "1001"), 3)

    def test_03c_infer_chapter_ignores_chapter_close_at_date_root(self):
        from infer_context import infer_chapter

        # 장마감은 .assets 안에서만 찾는다(옛 루트 위치 호환 없음)
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "복습노트/1001").mkdir(parents=True)
            (repo / "복습노트/1001/장마감_1001_3장.md").write_text("x", encoding="utf-8")
            self.assertEqual(infer_chapter(repo, "1006"), 5)

    def test_04_extract_terms(self):
        from infer_context import extract_chapter_terms

        terms = extract_chapter_terms(ROOT, chapter=5)
        self.assertIsInstance(terms, list)
        self.assertGreater(len(terms), 10)
        # Should include core terms of chapter 5
        term_text = " ".join(terms)
        self.assertTrue(any(k in term_text for k in ["DNA", "복제", "전사", "번역", "폴리머레이스", "프라이머"]))

    def test_05_build_stt_prompt(self):
        from infer_context import build_stt_prompt

        prompt = build_stt_prompt(chapter=5, chapter_title="DNA 복제와 유전자 발현", terms=["DNA", "복제", "헬리케이스"])
        self.assertIn("생명과학", prompt)
        self.assertIn("5장", prompt)
        self.assertIn("DNA 복제와 유전자 발현", prompt)
        self.assertIn("헬리케이스", prompt)
        self.assertIn("이수체", prompt)  # Common error correction rule

    def test_06_merge_transcripts(self):
        import tempfile
        from merge_transcripts import merge_transcripts

        with tempfile.TemporaryDirectory() as tmpdir:
            part1 = Path(tmpdir) / "1006_생명_part01.md"
            part2 = Path(tmpdir) / "1006_생명_part02.md"
            part1.write_text("첫 번째 파트 발화 내용입니다.\n\n이수체에 대해 설명합니다.\n", encoding="utf-8")
            part2.write_text("두 번째 파트 발화 내용입니다.\n\n헬리케이스 효소가 작동합니다.\n", encoding="utf-8")

            out_file = Path(tmpdir) / "1006 생명.md"
            res = merge_transcripts(
                target_dir=tmpdir,
                prefix="1006_생명",
                out_file=str(out_file),
                keep_parts=True,
            )
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("# 1006_생명 전체 오디오 전사본", content)
            self.assertIn("## Part 01", content)
            self.assertIn("## Part 02", content)
            self.assertIn("이수체에 대해 설명합니다.", content)
            self.assertIn("헬리케이스 효소가 작동합니다.", content)

            # Test timestamp stripping when timestamps=False
            part3 = Path(tmpdir) / "1006_생명_part03.md"
            part3.write_text("00:15\n이 문장은 타임스탬프가 제거되어야 합니다.\n", encoding="utf-8")
            out_file2 = Path(tmpdir) / "1006_merged2.md"
            merge_transcripts(
                target_dir=tmpdir,
                prefix="1006_생명",
                out_file=str(out_file2),
                timestamps=False,
                keep_parts=True,
            )
            content2 = out_file2.read_text(encoding="utf-8")
            self.assertNotIn("00:15", content2)
            self.assertIn("이 문장은 타임스탬프가 제거되어야 합니다.", content2)

if __name__ == "__main__":
    unittest.main()
