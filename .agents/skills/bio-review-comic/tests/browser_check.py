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
from comic_browser_evidence import PREVIEW_RECORD, link_status
from comic_contract import write
from comic_source import digest


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
        resource = fixture.note.parent / 'fixture.css'
        resource.write_text('.topic { color: inherit; }')
        note_html = fixture.note.read_bytes().replace(b'</head>', b'<link rel="stylesheet" href="fixture.css"></head>')
        fixture.note.write_bytes(note_html)
        # Re-extract so the linked stylesheet is part of the source served in Chromium.
        previous = fixture.run
        fixture.run = previous.parent / 'with-css'
        fixture.api.extract(fixture.repo, '1105', fixture.run, review_version=1)
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

        fixture.reviews(automatic=False)  # Actual Chromium evidence came from run_check.
        pointer = fixture.read(PREVIEW_RECORD)
        report_path = Path(pointer['report'])
        full_report = report_path.read_bytes()
        missing_view = json.loads(full_report)
        missing_view['views'].pop()
        write(report_path, missing_view)
        fixture.write(PREVIEW_RECORD, {**pointer, 'sha256': digest(report_path.read_bytes())})
        expect_publish_blocked(fixture, '4종')
        report_path.write_bytes(full_report)
        fixture.write(PREVIEW_RECORD, pointer)
        original = fixture.note.read_bytes()
        # Adding a valid managed block leaves the lesson digest intact but changes browser inputs.
        extra = block_for('other.html#s0-miller', page['note_link']).encode()
        fixture.note.write_bytes(original.replace(b'</article>', extra + b'</article>', 1))
        expect_publish_blocked(fixture, '입력 변경')
        fixture.note.write_bytes(original)
        assert preview['local_resources'][resource.relative_to(fixture.repo).as_posix()] == digest(resource.read_bytes())
        css = resource.read_bytes()
        resource.write_bytes(css + b'\n')
        expect_publish_blocked(fixture, '로컬 자원 변경')
        resource.write_bytes(css)
        publication = fixture.api.publish(fixture.run, link_notes=False)
        version = Path(publication['version'])
        assert (version / 'checks/automatic-preview/report.json').read_bytes() == full_report
        comic_only = run_check(version, 'published', args.output / 'comic-only', '--comic-only')
        expect_views(comic_only, args.output / 'comic-only', round_trips=0)
        assert comic_only['link_mode'] == 'comic-only'
        assert all(view['comic_to_source_returns'] == 2 for view in comic_only['views'])
        assert link_status(version)['status'] == 'skipped'

        fixture.api.link_notes(fixture.run)
        repeated = fixture.api.publish(fixture.run)
        assert repeated['version'] == publication['version']
        assert repeated['link_verification']['status'] == 'pending'
        current = fixture.note.read_text(encoding='utf-8')
        changed = current.replace('유기물이 검출되었어요.', '실험에서 유기물이 검출되었어요.')
        assert changed != current
        fixture.note.write_text(changed, encoding='utf-8')
        final = run_check(version, 'published', args.output / 'published')
        expect_views(final, args.output / 'published')
        assert final['source_status'] == 'changed_since_publication'
        assert link_status(version)['status'] == 'passed'
        assert (version / link_status(version)['report']).is_file()
        assert final['inputs']['note']['sha256'] != preview['inputs']['note']['sha256']

        match, href = next((match, href) for match, href in managed_blocks(changed)
                           if urlsplit(href).fragment == 's0-miller')
        wrong_href = href.rsplit('#', 1)[0] + '#s1-cheatsheet'
        damaged = changed[:match.start()] + block_for(wrong_href, page['note_link']) + changed[match.end():]
        assert strip_links(damaged) == strip_links(changed)
        fixture.note.write_text(damaged, encoding='utf-8')
        assert link_status(version)['status'] == 'pending'
        expect_bad_fragment(run_check(version, 'published', args.output / 'wrong-fragment', expected_exit=1))
        assert link_status(version)['status'] == 'failed'
        public = Path(publication['html'])
        unchanged = (public.read_bytes(), (version / 'publication.json').read_bytes())
        repair = fixture.api.link_notes(version, repair_fragments=True)
        assert [row['page'] for row in repair['results'] if row['status'] == 'updated'] == ['s0-miller']
        assert link_status(version)['status'] == 'pending'
        expect_views(run_check(version, 'published', args.output / 'repaired'), args.output / 'repaired')
        assert link_status(version)['status'] == 'passed'
        assert (public.read_bytes(), (version / 'publication.json').read_bytes()) == unchanged

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


def expect_publish_blocked(fixture, reason):
    before = fixture.note.read_bytes()
    with fixture.assertRaisesRegex(ValueError, reason):
        fixture.api.publish(fixture.run)
    assert not (fixture.run / 'publication.json').exists()
    assert not (fixture.note.parent / '.assets').exists()
    assert fixture.note.read_bytes() == before


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
