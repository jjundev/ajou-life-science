import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "정리노트" / "0917.md"
GUIDE = ROOT / "정리노트" / "eli5" / "src" / "0917" / "guide.py"

ACTIVE = {
    f"3강:{n}"
    for n in (1, 2, 3, 5, 7, 11, 14, 18, 20, 22, 24, 25, 26, 27, 28, 29,
              30, 31, 34, 36, 37, 38, 40)
}
DEFERRED = {
    f"3강:{n}"
    for n in (4, 6, 8, 9, 10, 12, 13, 15, 16, 17, 19, 21, 23, 32, 33, 35, 39)
}


class Test0917Eli5Source(unittest.TestCase):
    def test_source_contract_covers_all_3gang_questions(self):
        self.assertTrue(NOTE.is_file(), "0917 source note is missing")
        self.assertTrue(GUIDE.is_file(), "0917 guide module is missing")

        scripts = ROOT / ".agents" / "skills" / "study-note-eli5" / "scripts"
        sys.path.insert(0, str(scripts))
        sys.path.insert(0, str(GUIDE.parent))
        try:
            from question_scope import extract_question_scope
            scope = extract_question_scope(NOTE.read_text(encoding="utf-8"))
            spec = importlib.util.spec_from_file_location("eli5_0917", GUIDE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
            sys.path.pop(0)

        self.assertEqual(set(scope), ACTIVE | DEFERRED)
        self.assertEqual({q["id"] for q in module.QUESTIONS}, ACTIVE)
        self.assertEqual(set(module.DEFERRED), DEFERRED)
        self.assertEqual(len(ACTIVE | DEFERRED), 40)
        self.assertNotIn("web_scope", module.META)


if __name__ == "__main__":
    unittest.main()
