"""mpe_cli browser: standard explanation browser check on a synthetic forecast stage."""
import json
from test_forecast_pipeline import build_run, approve
from test_cli import call
from mpe_browser import chromium_candidates, launch_chromium, link_problems


def test_browser_writes_evidence_and_keeps_reviews(tmp_path):
    source, run, item = build_run(tmp_path)
    approve(item)
    result = call('browser', '--run', run)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((item['folder'] / 'evidence' / 'explain-browser.json').read_text())
    assert report['status'] == 'pass' and len(report['runs']) == 6
    review = json.loads((item['folder'] / 'review.json').read_text())
    assert review['browser']['status'] == 'pass', 'browser 결과는 증거일 뿐 기존 기록을 지우지 않음'
    assert any(k.endswith('evidence/explain-browser.json') for k in review['artifact_hashes'])
    assert call('publish', '--run', run).returncode == 0


def test_links_resolve_against_publish_folder(tmp_path):
    publish, stage = tmp_path / 'pub', tmp_path / 'stage'
    (publish / 'notes').mkdir(parents=True)
    stage.mkdir()
    (publish / 'notes' / 'n.html').write_text('<section id="s1-a"></section>')
    (stage / 'local.css').write_text('')
    html = ('<a href="notes/n.html#s1-a">ok</a><a href="notes/n.html#s9-missing">x</a>'
            '<a href="gone.html">x</a><a href="local.css">x</a><a href="#p1">x</a><a href="https://e.x/">x</a>')
    problems, count = link_problems(html, publish, stage)
    assert count == 4
    assert problems == ['링크 앵커 없음: notes/n.html#s9-missing', '링크 파일 없음: gone.html']


def _fake_browser(root, name, binary):
    path = root / name / 'chrome-linux' / binary
    path.parent.mkdir(parents=True)
    path.write_text('#!/bin/sh\n')
    path.chmod(0o755)
    return str(path)

def test_chromium_candidates_prefer_newest_revision(tmp_path):
    old = _fake_browser(tmp_path, 'chromium-1243', 'chrome')
    new = _fake_browser(tmp_path, 'chromium_headless_shell-1255', 'headless_shell')
    (tmp_path / 'firefox-1400').mkdir()
    assert chromium_candidates([tmp_path, None, tmp_path / 'missing']) == [new, old]

def test_launch_falls_back_when_default_executable_is_missing(tmp_path, monkeypatch):
    path = _fake_browser(tmp_path, 'chromium-1243', 'chrome')
    monkeypatch.setenv('MPE_CHROMIUM', path)
    calls = []
    class Chromium:
        def launch(self, executable_path=None):
            calls.append(executable_path)
            if executable_path is None:
                raise RuntimeError("BrowserType.launch: Executable doesn't exist at /opt/pw-browsers/chromium_headless_shell-1255")
            return 'browser'
    class PW:
        chromium = Chromium()
    assert launch_chromium(PW()) == 'browser'
    assert calls == [None, path]

def test_review_status_and_answer_compare_are_short(tmp_path):
    source, run, item = build_run(tmp_path)
    approve(item)
    status = call('review-status', '--run', run)
    assert status.returncode == 0, status.stderr
    lines = status.stdout.strip().splitlines()
    assert len(lines) == 4 and all(': pass' in line for line in lines)
    from mpe_cli import card_answer
    problems = item['pack'].problems
    answers = tmp_path / 'answers.tsv'
    answers.write_text(''.join(f'{p.id}\t{card_answer(p)}\n' for p in problems), encoding='utf-8')
    same = call('compare-answers', '--run', run, '--from', answers)
    assert same.returncode == 0 and len(same.stdout.strip().splitlines()) == 1, same.stdout + same.stderr
    answers.write_text(''.join(f'{p.id}\t{"zz" if i == 0 else card_answer(p)}\n' for i, p in enumerate(problems[:-1])), encoding='utf-8')
    diff = call('compare-answers', '--run', run, '--from', answers)
    assert diff.returncode == 1
    assert problems[0].id in diff.stdout and '답 없음: ' + problems[-1].id in diff.stdout
