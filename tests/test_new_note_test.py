import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.new_note_test import main, parse_quiz_specs  # noqa: E402


def _main_quiet(argv):
    """생성기 출력(경로·오류 메시지)이 테스트 출력에 섞이지 않게 한다."""
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        return main(argv)


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
            rc = _main_quiet(["0908",
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


# 다중 출처 fixture — 매핑표에 출처 열, 퀴즈 항목에 src 필드
FIXTURE_MD_MULTI = """# 0999 테스트

## ⏱ 30초 요약

| 주제 | 한 줄 |
|---|---|
| a | b |

## ⏪ 지난 회차 복습

- 요점

## ── 2장 시작 ──

### §1 절

본문.

## ✂️ 여기서 강의가 끊겼습니다

다음.

## 부록. 문항 ↔ 개념 매핑

[`0999.html`](0999.html)

| 출처 | # | 무엇을 묻는가 | 노트 위치 | 상태 |
|---|---|---|---|---|
| 1강 | 32 | a | §1 절 | |
| 2강 | 1 | b | §1 절 | |
"""

FIXTURE_HTML_OK = """<!doctype html><html><body><script>
const QUIZ = [
  { n:32, src:"1강", q:"a", opts:["x","y"], answer:0, why:"w", trap:{}, ref:"§1 절" },
  { n:1, src:"2강", q:"b", opts:["x","y"], answer:0, why:"w", trap:{}, ref:"§1 절" }
];
</script></body></html>"""

FIXTURE_HTML_MISSING_SRC = FIXTURE_HTML_OK.replace('{ n:1, src:"2강",', '{ n:1,')


class TestGeneratorMultiSource(unittest.TestCase):
    """다중 출처 모드 — (src, n) 쌍 비교와 src 누락 검출"""

    def _run_multi(self, html_text):
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, "root")
            _write(os.path.join(root, "정리노트", "0999.md"), FIXTURE_MD_MULTI)
            _write(os.path.join(root, "정리노트", "0999.html"), html_text)
            out = os.path.join(d, "t.py")
            self.assertEqual(_main_quiet(["0999", "--quiz", "1강:32", "--quiz", "2강:1", "--out", out]), 0)
            os.environ["NOTE_REPO_ROOT"] = root
            try:
                return _run(_load(out, "gen_0999_" + str(id(html_text))))
            finally:
                os.environ.pop("NOTE_REPO_ROOT", None)

    def test_multi_mode_accepts_complete_src(self):
        """src 가 모두 있으면 퀴즈 집합 검사 통과"""
        res = self._run_multi(FIXTURE_HTML_OK)
        self.assertTrue(res.wasSuccessful(), res.failures + res.errors)

    def test_multi_mode_rejects_missing_src(self):
        """src 가 하나라도 빠지면 퀴즈 집합 검사가 실패"""
        res = self._run_multi(FIXTURE_HTML_MISSING_SRC)
        failed = {t.id().rsplit(".", 1)[-1] for t, _ in res.failures}
        self.assertIn("test_quiz_covers_exactly_this_lecture", failed)


class TestGeneratorCli(unittest.TestCase):
    """CLI 방어 — 덮어쓰기·형식 혼용·MMDD"""

    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "t.py")
            self.assertEqual(_main_quiet(["0908", "--quiz", "7", "--out", out]), 0)
            self.assertEqual(_main_quiet(["0908", "--quiz", "7", "--out", out]), 2)
            self.assertEqual(_main_quiet(["0908", "--quiz", "7", "--out", out, "--force"]), 0)

    def test_parse_quiz_specs(self):
        multi, items = parse_quiz_specs(["7,8"])
        self.assertFalse(multi)
        self.assertEqual(items, [(None, 7), (None, 8)])
        multi, items = parse_quiz_specs(["1강:32,40", "2강:1"])
        self.assertTrue(multi)
        self.assertEqual(items, [("1강", 32), ("1강", 40), ("2강", 1)])
        with self.assertRaises(ValueError):
            parse_quiz_specs(["7,8", "1강:3"])
        with self.assertRaises(ValueError):
            parse_quiz_specs(["abc"])

    def test_rejects_bad_mmdd(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(_main_quiet(["910", "--quiz", "7", "--out", os.path.join(d, "t.py")]), 2)

    def test_duplicate_numbers_are_collapsed(self):
        """--quiz 7,7,8 → 생성 파일의 QUIZ 는 {7, 8}"""
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "t.py")
            self.assertEqual(_main_quiet(["0908", "--quiz", "7,7,8", "--out", out]), 0)
            with open(out, encoding="utf-8") as f:
                self.assertIn("QUIZ = {7, 8}", f.read())

    def test_output_cannot_overwrite_generator_source_or_aliases(self):
        for alias_kind in ('direct', 'symlink', 'hardlink'):
            with self.subTest(alias=alias_kind), tempfile.TemporaryDirectory() as directory:
                source = os.path.join(directory, 'new_note_test.py')
                _write(source, '# temporary generator source\n')
                output = source
                if alias_kind != 'direct':
                    output = os.path.join(directory, 'output-' + alias_kind)
                    if alias_kind == 'symlink':
                        os.symlink(source, output)
                    else:
                        os.link(source, output)
                with open(source, 'rb') as source_file:
                    before = source_file.read()
                with patch('scripts.new_note_test.__file__', source):
                    self.assertEqual(_main_quiet([
                        '0999', '--quiz', '1', '--out', output, '--force'
                    ]), 2)
                with open(source, 'rb') as source_file:
                    self.assertEqual(source_file.read(), before)

        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, 'new_note_test.py')
            _write(source, '# temporary generator source\n')
            output = os.path.join(directory, 'generated.py')
            with patch('scripts.new_note_test.__file__', source):
                self.assertEqual(_main_quiet(['0999', '--quiz', '1', '--out', output]), 0)
                with open(output, 'rb') as generated_file:
                    first = generated_file.read()
                self.assertEqual(_main_quiet(['0999', '--quiz', '1', '--out', output]), 2)
                self.assertEqual(_main_quiet([
                    '0999', '--quiz', '1', '--out', output, '--force'
                ]), 0)
                with open(output, 'rb') as generated_file:
                    self.assertEqual(generated_file.read(), first)


class TestMarkerData(unittest.TestCase):
    def test_json_data_full_qids_and_legacy_fallback(self):
        import json
        from scripts.new_note_test import parse_question_data, html_quiz_qids
        meta = {'date': '0999'}
        items = [{'n': 1, 'src': 'web-a', 'qid': 'web-a:q01', 'q': 'fake n:99', 'answer': 0, 'why': 'ok', 'ref': 'DNA'},
                 {'n': 1, 'src': 'web-b', 'qid': 'web-b:q01', 'answer': 1, 'why': 'ok', 'ref': 'DNA'}]
        html = '/* QUESTION-DATA-START */\nconst META = ' + json.dumps(meta) + ';\nconst QUIZ = ' + json.dumps(items) + ';\n/* QUESTION-DATA-END */'
        self.assertEqual(parse_question_data(html), (meta, items))
        self.assertEqual(html_quiz_qids(html), ['web-a:q01', 'web-b:q01'])
        self.assertIsNone(parse_question_data(FIXTURE_HTML_OK))
        self.assertEqual(html_quiz_qids(FIXTURE_HTML_OK), [])
        generated = {'__file__': '/tmp/test.py'}
        from scripts.new_note_test import render
        exec(compile(render('0999', True, [('web-a', 1), ('web-b', 1)], [], None, False), '<generated>', 'exec'), generated)
        self.assertEqual(generated['_html_quiz_set'](html), {('web-a', 1), ('web-b', 1)})
        self.assertEqual(generated['_html_item_count'](html), 2)
        self.assertEqual(generated['html_quiz_qids'](html), ['web-a:q01', 'web-b:q01'])
        check = generated['TestNoteHtml']('test_every_question_has_answer_and_reason')
        check.html = html
        check.test_every_question_has_answer_and_reason()
        check.html = html.replace('\"answer\": 0, ', '')
        with self.assertRaises(AssertionError):
            check.test_every_question_has_answer_and_reason()

    def test_malformed_marker_block_rejected(self):
        from scripts.new_note_test import parse_question_data
        for html in ['/* QUESTION-DATA-START */',
                     '/* QUESTION-DATA-START */ const META = {}; const QUIZ = []; alert(1); /* QUESTION-DATA-END */',
                     '/* QUESTION-DATA-START */ const META = []; const QUIZ = {}; /* QUESTION-DATA-END */']:
            with self.assertRaises(ValueError):
                parse_question_data(html)

    def test_legacy_entrypoint_without_jsonschema(self):
        import subprocess
        code = '''import builtins, runpy, sys
original = builtins.__import__
def blocked(name, *args, **kwargs):
    if name == 'jsonschema' or name.startswith('jsonschema.'):
        raise ImportError('jsonschema deliberately unavailable')
    return original(name, *args, **kwargs)
builtins.__import__ = blocked
sys.argv = ['new_note_test.py', '--help']
runpy.run_path('scripts/new_note_test.py', run_name='__main__')
'''
        result = subprocess.run([sys.executable, '-c', code], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            output = os.path.join(directory, 'generated.py')
            code = code.replace("sys.argv = ['new_note_test.py', '--help']",
                                "sys.argv = ['new_note_test.py', '0999', '--quiz', '1', '--out', sys.argv[1]]")
            result = subprocess.run([sys.executable, '-c', code, output], cwd=REPO_ROOT,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(os.path.isfile(output))


if __name__ == "__main__":
    unittest.main()
