import pytest
from exam_fixtures import make_pack,approve_questions,POLICY
from exam_check import check_set
from exam_build import build_exam
from exam_contract import ExamError

def test_incomplete_or_unreviewed_rejected(repo):
 p=make_pack(repo)
 assert not check_set(p)
 assert check_set(p,require_reviews=True)
 approve_questions(p);assert not check_set(p,require_reviews=True)
 src=p.parent/'.pack/v1'
 with pytest.raises(ExamError):build_exam(repo,src)
 p.write_text(p.read_text().replace('id="p75"','id="other"'))
 assert check_set(p)
def test_policy_and_assets_invalidate_review(repo):
 p=make_pack(repo);approve_questions(p)
 (repo/POLICY/'webquiz-style.md').write_text('new policy')
 assert check_set(p,require_reviews=True)
def test_missing_new_feedback_invalidates_review(repo):
 p=make_pack(repo);approve_questions(p)
 f=repo/'웹과제/6장/note-feedback.md';f.parent.mkdir(parents=True);f.write_text('new')
 assert check_set(p,require_reviews=True)
def test_rebuild_resets_review(repo):
 import json
 p=make_pack(repo);src=p.parent/'.pack/v1';review=json.loads((src/'question-review.json').read_text());review['reviews']['browser']['status']='pass'
 (src/'question-review.json').write_text(json.dumps(review));build_exam(repo,src)
 assert all(r['status']=='not_run' for r in json.loads((src/'question-review.json').read_text())['reviews'].values())
def test_blueprint_and_card_tampering(repo):
 p=make_pack(repo);src=p.parent/'.pack/v1';(src/'blueprint.md').write_text('missing')
 assert check_set(p)

def test_card_and_html_cannot_both_drift_from_pack(repo):
 p=make_pack(repo);src=p.parent/'.pack/v1';old='c1-mcq-';s=p.read_text()
 # Replace a question condition in both rendered HTML and saved card, not pack.
 p.write_text(s.replace('조건을 판단해요?','바뀐 조건?',1))
 f=src/'cards/p1.html';f.write_text(f.read_text().replace('조건을 판단해요?','바뀐 조건?',1))
 assert check_set(p)


def test_both_exam_pages_share_fonts_and_bind_them_to_review(repo):
    from urllib.parse import unquote
    from exam_dom import parse
    from exam_presentations import pair_paths

    exam = make_pack(repo)
    approve_questions(exam)
    src = exam.parent / '.pack/v1'
    assert not (src / 'vendor').exists()
    styles = set()
    for page in pair_paths(src)[1:]:
        link = next(n.attrs['href'] for n in parse(page.read_text()).find_all(
            lambda n: n.tag == 'link' and n.attrs.get('href', '').endswith('pretendard.css')))
        styles.add((page.parent / unquote(link)).resolve())
    css, = styles
    assert css.is_relative_to(repo / '복습노트/_shared') and css.is_file()
    assert check_set(exam, require_reviews=True) == []

    (css.parent / 'woff2/Pretendard-Regular.woff2').unlink()
    assert any('공용 자원' in error and 'Pretendard-Regular' in error
               for error in check_set(exam, require_reviews=True))
