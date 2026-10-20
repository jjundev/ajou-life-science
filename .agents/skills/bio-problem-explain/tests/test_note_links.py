"""A missing concept link must never silently reach publication."""
from dataclasses import replace
from copy import deepcopy
import re
import pytest
from helpers import fragment, problem, pack, approved, source_file
from mpe_contract import validate_fragment, validate_reviews
from mpe_source import load_source
from mpe_render import build_explanation
from mpe_publish import publish_explanation
from mpe_types import ExplainError


def bare(p=None):
    return re.sub(r' data-note-link-omitted="[^"]*"', '', fragment(p))


def linked(href='정리노트_Test.html#s1', p=None):
    return bare(p).replace('data-explanation="recall">',
        f'data-explanation="recall"><p><a href="{href}">관련 개념</a></p>')


def omitted(reason='대응하는 정리노트가 없어 교재의 관련 절을 직접 대조함', p=None):
    return bare(p).replace('data-explanation="recall"',
                         f'data-explanation="recall" data-note-link-omitted="{reason}"')


def test_each_fragment_requires_recall_concept_link():
    assert any('정리노트' in e for e in validate_fragment(problem(), bare()))
    assert validate_fragment(problem(), linked()) == []


@pytest.mark.parametrize('href', ['정리노트_Test.html', '#s1', '복습문제_Test.html#p1',
                                  'https://example.com/정리노트_Test.html#s1'])
def test_navigation_or_unanchored_or_external_link_does_not_count(href):
    assert any('정리노트' in e for e in validate_fragment(problem(), linked(href)))


def test_encoded_and_decomposed_note_names_are_supported():
    from urllib.parse import quote
    import unicodedata
    for name in ('정리노트_Test.html', unicodedata.normalize('NFD', '정리노트_Test.html')):
        assert validate_fragment(problem(), linked(quote(name) + '#s1')) == []


def test_link_outside_recall_does_not_cover_missing_concept_link():
    assert validate_fragment(problem(), bare() + '<p><a href="정리노트_Test.html#s1">개념</a></p>')


@pytest.mark.parametrize('anchor', ['panel-left-title', 'panel-right-title', 'toc', 'top',
                                  's5-links', 's6-cheatsheet', 's5-next'])
def test_note_navigation_anchors_do_not_count_as_concepts(anchor):
    assert validate_fragment(problem(), linked('정리노트_Test.html#' + anchor))


def test_omission_requires_nonempty_reason_and_cannot_hide_a_link():
    assert validate_fragment(problem(), omitted()) == []
    assert validate_fragment(problem(), omitted('  '))
    assert validate_fragment(problem(), linked().replace('data-explanation="recall"',
        'data-explanation="recall" data-note-link-omitted="자료 없음"'))


@pytest.mark.parametrize('profile', ['review', 'forecast', 'exam'])
def test_omission_must_have_explicit_content_approval(profile):
    p = replace(pack(), profile=profile)
    fragments = {'p1': omitted()}
    review = approved(p, fragments)
    review['content'].pop('note_link_exceptions', None)
    assert any('링크 예외' in e for e in validate_reviews(p, fragments, review))
    entry = dict(status='pass', reviewer='내용 검토자', evidence='evidence/link-audit.md',
                 reason='대응하는 정리노트가 없어 교재의 관련 절을 직접 대조함')
    review['content']['note_link_exceptions'] = {'p1': entry}
    assert validate_reviews(p, fragments, review) == []
    for key, value in [('status', 'not_run'), ('reason', ''), ('reason', '다른 사유'),
                       ('reviewer', ''), ('evidence', '')]:
        bad = deepcopy(review); bad['content']['note_link_exceptions']['p1'][key] = value
        assert validate_reviews(p, fragments, bad)


@pytest.mark.parametrize('target', ['missing-file', 'missing-anchor', 'valid'])
def test_note_link_destination_checked_before_build(tmp_path, target):
    repo = tmp_path/'repo'; path = source_file(repo); p = load_source(path, repo)
    if target != 'missing-file':
        (path.parent/'정리노트_Test.html').write_text('<section id="'+('other' if target=='missing-anchor' else 's1')+'">개념</section>')
    fragments = {q.id: linked(p=q) for q in p.problems}
    if target == 'valid':
        artifacts = build_explanation(p, fragments, tmp_path/'stage', repo)
        publish_explanation(p, artifacts, fragments, approved(p, fragments, artifacts), path.parent, tmp_path/'backup')
    else:
        with pytest.raises(ExplainError, match='경로|링크'):
            build_explanation(p, fragments, tmp_path/'stage', repo)


def test_unapproved_omission_cannot_publish(tmp_path):
    repo=tmp_path/'repo';path=source_file(repo);p=load_source(path,repo)
    fragments={q.id:omitted(p=q) for q in p.problems}
    artifacts=build_explanation(p,fragments,tmp_path/'stage',repo)
    review=approved(p,fragments,artifacts);review['content'].pop('note_link_exceptions',None)
    with pytest.raises(ExplainError,match='링크 예외'):
        publish_explanation(p,artifacts,fragments,review,path.parent,tmp_path/'backup')
    assert not (path.parent/artifacts.html.name).exists()
