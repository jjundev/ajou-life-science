"""Synthetic questions: verify two presentations, never academic correctness."""
import json
import pytest
from playwright.sync_api import sync_playwright
from exam_fixtures import make_pack, approve_questions
from exam_check import check_set, completion_status


def practice_of(question):
    return question.with_name(question.name.replace('_v', '_연습형_v'))


def test_both_presentations_share_questions_and_gate_reviews(repo):
    question = make_pack(repo)
    practice = practice_of(question)
    assert practice.is_file(), '시험예상 생성 시 연습형도 필요'
    from exam_dom import parse, inner
    def cards(path):
        import re
        return [re.sub(r' data-choice="[A-Z]"', '', inner(next(n.find_all(lambda x:'problem' in x.classes)))) for n in parse(path.read_text()).find_all(lambda n:n.tag == 'article')]
    assert cards(question) == cards(practice)
    approve_questions(question)
    assert not check_set(question, require_reviews=True)
    practice.write_text(practice.read_text().replace('조건을 판단해요?', '조건을 무시해요?', 1))
    assert check_set(question, require_reviews=True)
    assert completion_status(question, None, dict(repairs_used=0))['status'] == 'unverified'


def test_both_browser_modes_need_review(repo):
    question = make_pack(repo)
    approve_questions(question)
    path = question.parent / '.pack/v1/question-review.json'
    review = json.loads(path.read_text())
    assert 'presentations' in review['reviews']['browser'], '각 풀이형 브라우저 검토 필요'
    review['reviews']['browser']['presentations']['practice']['status'] = 'not_run'
    path.write_text(json.dumps(review))
    assert check_set(question, require_reviews=True)


@pytest.mark.parametrize('width', [375, 1280])
@pytest.mark.parametrize('scheme', ['light', 'dark'])
def test_review_practice_and_short_answers(repo, width, scheme):
    practice = practice_of(make_pack(repo))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport=dict(width=width, height=900), color_scheme=scheme)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(practice.as_uri() + '#p1')
        assert page.locator('.presentation-links,#practice-results,#exam-results,#submit-exam').count() == 0
        assert page.locator('.topbar #open-explanation').count() == 1
        page.locator('#p1 .review-choice').nth(1).click()
        assert page.locator('#p1').is_visible()
        assert page.locator('#p1 .review-status').inner_text() == '정답이에요.'
        assert page.locator('#p1 .review-diagnostic:visible').count() == 1
        page.locator('#p1 .review-choice').nth(0).click()
        assert page.locator('#p1 .review-diagnostic:visible').count() == 2
        if page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
            page.locator('#toggle-right').click()
        page.locator('.aid[data-card-id="p1"] .review-unsure').click()
        assert page.locator('.aid[data-card-id="p1"] .review-unsure').get_attribute('data-unsure') == 'true'
        if width < 1024:
            page.locator('#panel-right [data-panel-close]').click()
        page.locator('#p1 .review-reset').click()
        assert page.locator('#p1 .review-status').inner_text() == ''
        page.locator('#p1 .review-choice').nth(0).click()
        assert '정답이 아니에요' in page.locator('#p1 .review-status').inner_text()
        page.evaluate("location.hash='p56'")
        page.locator('#p56 input').fill('aa')
        assert page.locator('#p56 .review-status').inner_text() == ''
        page.locator('#p56 .check-answer').click()
        assert page.locator('#p56 .review-status').inner_text() == '자기채점 대기'
        assert page.locator('#p56 input').is_disabled()
        page.locator('#p56 .review-reset').click()
        page.locator('#p56 input').fill('Aa')
        page.locator('#p56 .check-answer').click()
        assert page.locator('#p56 .review-status').inner_text() == '자동 일치'
        page.evaluate("""window.ReviewPrompt.copyText=async(_,text)=>{window.copiedPrompt=text;return true;};""")
        page.evaluate("location.hash='p75'")
        page.locator('.review-export').click()
        assert 'Aa' in page.evaluate('window.copiedPrompt')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.evaluate("location.hash='p56'")
        page.reload()
        assert page.locator('#p56 input').input_value() == ''
        assert page.locator('#p56 .review-status').inner_text() == ''
        assert page.locator('#progress-n').text_content() == '0'
        assert page.locator('.review-choice[data-selected="true"]').count() == 0
        assert not errors
        browser.close()


@pytest.mark.parametrize('width', [375, 1280])
def test_exam_toolbar_and_reload_start_a_fresh_attempt(repo, width):
    question = make_pack(repo)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport=dict(width=width, height=900))
        page.goto(question.as_uri() + '#p1')
        bar = page.locator('.presentation-links')
        assert page.locator('.presentation-links a').count() == 0
        assert bar.is_hidden()
        page.locator('#p1 input[value="B"]').check()
        page.evaluate("location.hash='p75'")
        page.locator('#submit-exam').click()
        assert bar.is_visible()
        assert page.locator('#exam-results').is_visible()
        page.reload()
        assert page.locator('input:checked').count() == 0
        assert page.locator('.exam-input input:disabled').count() == 0
        assert page.locator('#exam-results').is_hidden()
        assert page.locator('#results-list').inner_text() == ''
        assert page.locator('#summary').inner_text() == ''
        assert bar.is_hidden()
        assert page.locator('#p1').is_visible()
        assert page.locator('#progress-n').text_content() == '0'
        assert page.locator('#exam-aid .solution').count() == 0
        browser.close()


def test_practice_requires_explicit_option_explanations(repo):
    from exam_presentations import practice_from_exam, set_hash
    from exam_contract import ExamError
    question = make_pack(repo)
    src = question.parent / '.pack/v1'
    pack = json.loads((src/'pack.json').read_text())
    pack['problems'][0].pop('option_explanations', None)
    with pytest.raises(ExamError, match='보기별 설명'):
        practice_from_exam(question.read_text(), pack, set_hash(src))
