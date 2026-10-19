from playwright.sync_api import sync_playwright, expect
from exam_fixtures import make_pack


def test_navigation_keeps_answers_and_submission_controls_reveal(repo):
    path = make_pack(repo)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(path.as_uri())
        page.locator('#pager-next').click(timeout=1500)
        assert page.locator('article.card:visible').count() == 1
        page.locator('#p1 input[value="B"]').check()
        expect(page.locator('#p2')).to_be_visible()
        page.locator('#pager-prev').click()
        assert page.locator('#p1 input[value="B"]').is_checked()
        assert page.locator('.solution:visible').count() == 0
        page.evaluate("location.hash='p75'")
        page.locator('#submit-exam').click()
        page.locator('.exam-result-row a[href="#p1"]').click()
        if page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
            page.locator('#toggle-right').click()
        expect(page.locator('#exam-aid .answer')).to_be_visible()
        assert page.locator('#exam-aid').inner_text().find('정답: B') >= 0
        page.locator('#toggle-right').click()
        page.once('dialog', lambda d: d.accept())
        page.locator('#reset-exam').click()
        assert page.locator('.solution:not([hidden])').count() == 0
        assert page.locator('#exam-aid .answer').count() == 0
        browser.close()


def test_choice_advances_without_grading_and_short_input_stays(repo):
    path=make_pack(repo)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(path.as_uri()+'#p1')
        page.locator('#p1 input[value=B]').check()
        expect(page.locator('#p2')).to_be_visible()
        assert page.locator('#p1 input[value=B]').is_checked()
        assert page.locator('.solution:visible').count()==0
        assert page.locator('#p1 .result').inner_text()==''
        page.locator('#pager-prev').click()
        expect(page.locator('#p1')).to_be_visible()
        page.locator('#p1 input[value=A]').check()
        expect(page.locator('#p2')).to_be_visible()
        page.evaluate("location.hash='p55'")
        page.locator('#p55 input[value=B]').check()
        expect(page.locator('#p56')).to_be_visible()
        page.locator('#p56 input').fill('Aa')
        expect(page.locator('#p56')).to_be_visible()
        assert page.locator('#p56 input').input_value()=='Aa'
        assert page.locator('.solution:visible').count()==0
        page.evaluate("location.hash='p75'")
        page.locator('#p75 input').fill('last')
        expect(page.locator('#p75')).to_be_visible()
        expect(page.locator('#submit-exam')).to_be_visible()
        browser.close()


def test_original_question_number_hidden_but_decimal_preserved(repo):
    import re
    path=make_pack(repo)
    text=path.read_text()
    text=re.sub(r'(<div class="problem">\s*<p[^>]*>)',r'\g<1>1. ',text,count=1)
    # A decimal at the beginning is content, not an original question number.
    start=text.index('<article class="card" id="p2">')
    text=text[:start]+re.sub(r'(<div class="problem">\s*<p[^>]*>)',r'\g<1>3.2 ',text[start:],count=1)
    path.write_text(text)
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        page=browser.new_page();page.goto(path.as_uri()+'#p1')
        assert not page.locator('#p1 .problem').inner_text().startswith('1. ')
        assert page.locator('#p2 .problem').inner_text().startswith('3.2 ')
        browser.close()
