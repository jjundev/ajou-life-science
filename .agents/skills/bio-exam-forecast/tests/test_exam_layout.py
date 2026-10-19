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
        page.locator('#pager-next').click()
        page.locator('#pager-prev').click()
        assert page.locator('#p1 input[value="B"]').is_checked()
        assert page.locator('.solution:visible').count() == 0
        page.locator('#submit-exam').click()
        if page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
            page.locator('#toggle-right').click()
        expect(page.locator('#exam-aid .answer')).to_be_visible()
        assert page.locator('#exam-aid').inner_text().find('정답: B') >= 0
        page.locator('#toggle-right').click()
        page.locator('#reset-exam').click()
        assert page.locator('.solution:not([hidden])').count() == 0
        assert page.locator('#exam-aid .answer').count() == 0
        browser.close()
