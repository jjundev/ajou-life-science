"""Exercise the production browser CLI with synthetic rasters."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

from test_comic import ComicPipeline, SCRIPT
from comic_links import block_for, managed_blocks, strip_links


def run_check(run, stage, output, *options, expected_exit=0):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), 'browser-check', '--run', str(run),
         '--stage', stage, '--out', str(output), *options],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    return json.loads((output / 'report.json').read_text(encoding='utf-8'))


def expect_views(report, output, *, round_trips=2):
    assert report['status'] == 'passed', report
    assert {(view['width'], view['height'], view['theme']) for view in report['views']} == {
        (1440, 900, 'light'), (1440, 900, 'dark'), (375, 812, 'light'), (375, 812, 'dark'),
    }
    assert len(report['views']) == 4
    assert report['held'] == [{'id': 's0-recap', 'reason': '그림 검토 보류'}]
    for view in report['views']:
        assert (view['pages'], view['panels'], view['link_round_trips']) == (2, 12, round_trips), view
        assert (output / view['screenshot']).is_file(), view


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    ComicPipeline.setUpClass()
    fixture = ComicPipeline('test_held_pages_stay_visible_and_are_not_complete')
    fixture.setUp()
    try:
        book = fixture.ready(held=True)
        page = book['pages'][0]
        page['panels'] += [copy.deepcopy(page['panels'][0]) for _ in range(4)]
        page['panels'][3]['caption'] = '가정한 실험 조건에서 얻은 결과와 실제 과거의 사건을 구별해야 해요. ' * 9
        page['panels'][3]['dialogue'][1]['text'] = '재료가 검출된 관찰과 살아 있는 세포의 생성은 구별해야 해요. ' * 6
        for panel in page['panels']:
            panel['characters'] = []
        fixture.write('storyboard.json', book)
        fixture.images()
        fixture.api.build(fixture.run)
        review_path = fixture.run / 'review.json'
        before = review_path.read_bytes()
        preview = run_check(fixture.run, 'preview', args.output / 'preview')
        expect_views(preview, args.output / 'preview')
        assert review_path.read_bytes() == before

        fixture.reviews()  # Synthetic fixture reports are confined to this test.
        publication = fixture.api.publish(fixture.run, link_notes=False)
        version = Path(publication['version'])
        comic_only = run_check(version, 'published', args.output / 'comic-only', '--comic-only')
        expect_views(comic_only, args.output / 'comic-only', round_trips=0)
        assert comic_only['link_mode'] == 'comic-only'
        assert all(view['comic_to_source_returns'] == 2 for view in comic_only['views'])

        fixture.api.link_notes(fixture.run)
        current = fixture.note.read_text(encoding='utf-8')
        changed = current.replace('유기물이 검출되었어요.', '실험에서 유기물이 검출되었어요.')
        assert changed != current
        fixture.note.write_text(changed, encoding='utf-8')
        final = run_check(version, 'published', args.output / 'published')
        expect_views(final, args.output / 'published')
        assert final['source_status'] == 'changed_since_publication'
        assert final['inputs']['note']['sha256'] != preview['inputs']['note']['sha256']

        match, href = next((match, href) for match, href in managed_blocks(changed)
                           if urlsplit(href).fragment == 's0-miller')
        wrong_href = href.rsplit('#', 1)[0] + '#s1-cheatsheet'
        damaged = changed[:match.start()] + block_for(wrong_href, page['note_link']) + changed[match.end():]
        assert strip_links(damaged) == strip_links(changed)
        fixture.note.write_text(damaged, encoding='utf-8')
        expect_bad_fragment(run_check(version, 'published', args.output / 'wrong-fragment', expected_exit=1))

        # A literal href-only edit invalidates the managed block too. Still exercise the click.
        literal = changed.replace(f'<a href="{href}"', f'<a href="{wrong_href}"', 1)
        assert literal != changed
        fixture.note.write_text(literal, encoding='utf-8')
        negative = run_check(version, 'published', args.output / 'href-only', expected_exit=1)
        assert negative['source_status'] == 'invalid_managed_links', negative
        assert [failure['check'] for failure in negative['failures']] == ['note_link_integrity'], negative
        expect_bad_fragment(negative)
        print(json.dumps({'status': 'passed', 'reports': str(args.output.resolve())}))
    finally:
        fixture.doCleanups()


def expect_bad_fragment(report):
    assert report['status'] == 'failed', report
    assert len(report['views']) == 4
    for view in report['views']:
        assert (view['pages'], view['panels'], view['link_round_trips']) == (2, 12, 1), view
        failure, = view['failures']
        assert (failure['topic'], failure['check']) == ('s0-miller', 'note_to_comic'), failure
        assert failure['expected'].endswith('#s0-miller'), failure
        assert failure['actual'].endswith('#s1-cheatsheet'), failure


if __name__ == '__main__':
    main()
