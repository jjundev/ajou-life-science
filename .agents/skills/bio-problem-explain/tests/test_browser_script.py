"""mpe_cli browser: standard explanation browser check on a synthetic forecast stage."""
import json
from test_forecast_pipeline import build_run, approve
from test_cli import call
from mpe_browser import link_problems


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
