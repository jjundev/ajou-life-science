import importlib.util
import os
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from scripts.new_note_test import main, parse_quiz_specs  # noqa: E402


def _load(path, name):
    """생성된 테스트 파일을 모듈로 읽는다. import 시점에 NOTE_REPO_ROOT 를 읽으므로 먼저 설정할 것."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(mod):
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    with open(os.devnull, "w") as sink:
        return unittest.TextTestRunner(stream=sink, verbosity=0).run(suite)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class TestGeneratorEquivalence(unittest.TestCase):
    """생성기가 손으로 쓴 test_note_0908.py 와 같은 판정을 내리는지"""

    def test_generated_0908_passes_against_real_files(self):
        """0908 파라미터로 생성한 테스트가 실제 0908.md/html 에 대해 전부 통과 (10개)"""
        for rel in ("정리노트/0908.md", "정리노트/0908.html"):
            if not os.path.isfile(os.path.join(REPO_ROOT, rel)):
                self.skipTest(f"{rel} 이 없습니다.")
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "test_note_0908.py")
            rc = main(["0908",
                       "--quiz", "7,8,11,14,17,22,30,33,35",
                       "--scope-terms", "세포골격,미세소관,중간섬유,확산,삼투,능동수송,촉진확산",
                       "--prior", "0903",
                       "--out", out])
            self.assertEqual(rc, 0)
            os.environ["NOTE_REPO_ROOT"] = REPO_ROOT
            try:
                res = _run(_load(out, "gen_0908"))
            finally:
                os.environ.pop("NOTE_REPO_ROOT", None)
            self.assertTrue(res.wasSuccessful(), res.failures + res.errors)
            self.assertEqual(res.testsRun, 10)


if __name__ == "__main__":
    unittest.main()
