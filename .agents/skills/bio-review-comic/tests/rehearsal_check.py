"""Exercise the rehearsal and promotion CLIs in an isolated repository."""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from browser_check import run_check
from test_comic import ComicPipeline, SCRIPT
import comic_rehearsal
from comic_links import block_for, managed_blocks


def cli(*args, expected_exit=0):
    result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                            text=True, capture_output=True, check=False)
    assert result.returncode == expected_exit, result.stdout + result.stderr
    return json.loads(result.stdout or result.stderr)


def main():
    ComicPipeline.setUpClass()
    f = ComicPipeline('test_held_pages_stay_visible_and_are_not_complete')
    f.setUp()
    try:
        original = f.note.read_bytes()
        css = f.note.with_name('note.css')
        css.write_text('article { color: inherit; }')
        f.note.write_bytes(original.replace(b'</head>', b'<link rel="stylesheet" href="note.css"></head>'))
        f.run = Path(f.tmp.name) / 'with-css'
        f.api.extract(f.repo, '1105', f.run)
        f.ready(held=True)
        f.images()
        f.api.build(f.run)
        f.reviews(automatic=False)
        missing = cli('rehearse', '--run', f.run, '--out', f.run / 'missing-preview', expected_exit=1)
        assert '미리보기 자동 검사 증거 확인 실패' in missing['error']
        run_check(f.run, 'preview', f.run / 'preview-check')
        original = f.note.read_bytes()
        before = {p: p.read_bytes() for p in f.repo.rglob('*') if p.is_file()}
        out = f.run / 'rehearsal'
        checked = cli('rehearse', '--run', f.run, '--out', out)
        assert checked['stage'] == 'rehearsal' and checked['status'] == 'passed'
        assert len(checked['views']) == 4
        assert all((v['pages'], v['panels'], v['link_round_trips']) == (2, 8, 2) for v in checked['views'])
        assert {p: p.read_bytes() for p in f.repo.rglob('*') if p.is_file()} == before
        assert not (f.run / 'publication.json').exists()
        comic_candidate = Path(checked['inputs']['comic']['path'])
        note_candidate = Path(checked['inputs']['note']['path'])
        assert note_candidate.name == f.note.name and comic_candidate.name.startswith('학습만화_')

        def wrong_fragment(*args):
            candidate, plan = planner(*args)
            text = candidate.decode('utf-8')
            match, href = next((m, h) for m, h in managed_blocks(text) if h.endswith('#s0-miller'))
            page = next(p for p in args[4] if p['id'] == 's0-miller')
            replacement = block_for(href.rsplit('#', 1)[0] + '#s1-cheatsheet', page['note_link'])
            return (text[:match.start()] + replacement + text[match.end():]).encode('utf-8'), plan

        planner = comic_rehearsal.plan_note_links
        wrong = f.run / 'wrong-hash'
        with patch.object(comic_rehearsal, 'plan_note_links', wrong_fragment):
            bad_hash = comic_rehearsal.rehearse(f.run, wrong)
        assert bad_hash['status'] == 'failed' and len(bad_hash['views']) == 4
        for view in bad_hash['views']:
            failure, = view['failures']
            assert (failure['topic'], failure['check'], view['link_round_trips']) == ('s0-miller', 'note_to_comic', 1)
            assert failure['actual'].endswith('#s1-cheatsheet')
        cli('publish', '--run', f.run, '--rehearsal', wrong, expected_exit=1)

        candidate_bytes = note_candidate.read_bytes()
        note_candidate.write_bytes(candidate_bytes + b' ')
        rejected = cli('publish', '--run', f.run, '--rehearsal', out, expected_exit=1)
        assert '검사 후보 또는 입력 변경' in rejected['error']
        note_candidate.write_bytes(candidate_bytes)
        css_before = css.read_bytes()
        css.write_bytes(css_before + b' ')
        stale = cli('publish', '--run', f.run, '--rehearsal', out, expected_exit=1)
        assert '로컬 자원 변경' in stale['error']
        css.write_bytes(css_before)
        assert {p: p.read_bytes() for p in f.repo.rglob('*') if p.is_file()} == before

        publication = cli('publish', '--run', f.run, '--rehearsal', out)
        assert Path(publication['html']).read_bytes() == comic_candidate.read_bytes()
        assert f.note.read_bytes() == candidate_bytes != original
        assert publication['link_verification']['status'] == 'pending'
        repeated = cli('publish', '--run', f.run, '--rehearsal', out)
        assert repeated['version'] == publication['version']
        assert list(Path(publication['version']).parent.iterdir()) == [Path(publication['version'])]

        # Keep the lesson source and the generated href valid, but make the new link unclickable on mobile.
        css.write_bytes(css_before + b'\n@media(max-width:500px){#s0-miller .comic-note a{display:none}}')
        run_check(f.run, 'preview', f.run / 'preview-mobile')
        bad = cli('rehearse', '--run', f.run, '--out', f.run / 'mobile', expected_exit=1)
        for view in bad['views']:
            failures = [(row['topic'], row['check']) for row in view['failures']]
            assert failures == ([('s0-miller', 'note_to_comic')] if view['width'] == 375 else []), view
        cli('publish', '--run', f.run, '--rehearsal', f.run / 'mobile', expected_exit=1)
        assert f.note.read_bytes() == candidate_bytes
        assert Path(publication['html']).read_bytes() == comic_candidate.read_bytes()
    finally:
        f.doCleanups()
    print('rehearsal browser checks passed')


if __name__ == '__main__':
    main()
