import pytest
from playwright.sync_api import sync_playwright, expect
from exam_fixtures import make_pack

CLIPBOARD_MOCK = '''
  window.__copied = null;
  Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
    writeText: async (text) => { window.__copied = text; }
  }});
'''
CLIPBOARD_BLOCKED = '''
  Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
    writeText: async () => { throw new Error('denied'); }
  }});
  document.execCommand = () => false;
'''


def section(text, heading):
    start = text.index(heading)
    nxt = [i for i in (text.find('\n### ', start + 1), text.find('\n## ', start + 1)) if i != -1]
    return text[start:min(nxt) if nxt else len(text)]


@pytest.mark.parametrize('width,scheme', [(1280,'light'),(1280,'dark'),(375,'light'),(375,'dark')])
def test_results_prompt_and_review_roundtrip(repo, width, scheme):
    path = make_pack(repo)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport=dict(width=width,height=900), color_scheme=scheme)
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.add_init_script(CLIPBOARD_MOCK)
        page.goto(path.as_uri())
        def visit(id):
            page.evaluate('(id) => location.hash=id', id)
            page.locator('#'+id).wait_for(state='visible')
        visit('p1'); page.locator('#p1 input[value=B]').check()
        visit('p2'); page.locator('#p2 input[value=A]').check()
        visit('p56'); page.locator('#p56 input').fill('Aa')
        visit('p57'); page.locator('#p57 input').fill('  <script>different</script>  ')
        assert page.locator('#exam-results:visible').count()==0
        page.evaluate("location.hash='p75'")
        expect(page.locator('#p75')).to_be_visible()
        page.locator('#submit-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        expect(page.locator('#results-title')).to_be_focused()
        # A swipe over the results must not reach the shared question pager.
        page.locator('#results-title').evaluate('''node => {
            node.dispatchEvent(new TouchEvent('touchstart', {bubbles:true, touches:[new Touch({identifier:1,target:node,clientX:300,clientY:300})]}));
            node.dispatchEvent(new TouchEvent('touchend', {bubbles:true, changedTouches:[new Touch({identifier:1,target:node,clientX:60,clientY:300})]}));
        }''')
        page.wait_for_timeout(50)
        assert page.evaluate('location.hash')=='#exam-results'
        expect(page.locator('#results-title')).to_be_visible()
        assert page.locator('.exam-result-row').count()==75
        assert page.locator('#pager-next').is_hidden()
        assert page.locator('.exam-result-row[data-result=pending]').inner_text().find('<script>different</script>')>=0
        page.locator('#results-filter').select_option('incorrect')
        assert page.locator('.exam-result-row:visible').count()==1
        page.locator('#results-filter').select_option('matched')
        assert page.locator('.exam-result-row:visible').count()==1
        page.locator('#results-filter').select_option('all')
        assert page.locator('#export-exam').count()==0
        page.locator('#copy-prompt').click()
        expect(page.locator('#prompt-status')).to_have_text('복기 프롬프트를 복사했어요. AI 채팅에 붙여 넣으세요.')
        copied=page.evaluate('window.__copied')
        assert '시험 예상문제(' in copied
        review=copied[copied.index('## 다시 볼 문항'):copied.index('## 확신 있게 맞힌 문항')]
        correct=copied[copied.index('## 확신 있게 맞힌 문항'):]
        assert '#### p2.' in section(review,'### 오답')
        assert '#### p2. p2.' not in copied
        assert '보기:\n- [A] ' in section(review,'### 오답') and '내 답: [A] / 정답: [' in review
        assert '- 풀이: ' in section(review,'### 오답')
        pending=section(review,'### 자기채점 대기')
        assert '#### p57.' in pending
        assert '내 답: "  <script>different</script>  "' in pending and '(허용:' in pending
        assert '#### p75.' in section(review,'### 미응답')
        assert '- p1. ' in correct and '- p56. ' in correct
        assert '#### p1.' not in copied
        page.locator('.exam-result-row a[href="#p1"]').click()
        expect(page.locator('#p1')).to_be_visible()
        assert page.locator('#p1 input[value=B]').is_disabled()
        if page.locator('#toggle-right').get_attribute('aria-expanded')!='true':
            page.locator('#toggle-right').click()
        expect(page.locator('#exam-aid .answer')).to_be_visible()
        if width<600: page.locator('#panel-right [data-panel-close]').click()
        page.locator('#submit-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        page.once('dialog', lambda d:d.dismiss())
        page.locator('#reset-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        page.once('dialog', lambda d:d.accept())
        page.locator('#reset-exam').click()
        assert page.locator('#exam-results:visible').count()==0
        assert page.locator('input:checked').count()==0
        assert page.locator('.solution:visible').count()==0
        assert not errors
        browser.close()


def test_blank_submit_and_copy_fallback(repo):
    path=make_pack(repo)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page()
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.add_init_script(CLIPBOARD_BLOCKED)
        page.goto(path.as_uri())
        page.evaluate("location.hash='p75'")
        expect(page.locator('#p75')).to_be_visible()
        page.locator('#submit-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        assert page.locator('.exam-result-row[data-result=unanswered]').count()==75
        page.locator('#copy-prompt').click()
        dialog=page.locator('dialog.review-prompt-dialog[open]')
        expect(dialog).to_have_count(1)
        text=dialog.locator('textarea').input_value()
        assert '### 미응답' in text
        assert 'katex' not in text
        expect(page.locator('#prompt-status')).to_have_text('자동 복사가 막혀 있어요. 열린 창에서 직접 복사해 주세요.')
        assert not errors
        browser.close()


@pytest.mark.parametrize('width', [1280,375])
def test_last_question_submit_and_scorecard(repo,width):
    path=make_pack(repo)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page(viewport=dict(width=width,height=900))
        page.goto(path.as_uri())
        expect(page.locator('#submit-exam')).to_be_hidden()
        page.evaluate("location.hash='p1'")
        page.locator('#p1 input[value=B]').check()
        expect(page.locator('#submit-exam')).to_be_hidden()
        page.evaluate("location.hash='p2'"); page.locator('#p2 input[value=A]').check()
        page.evaluate("location.hash='p56'"); page.locator('#p56 input').fill('Aa')
        page.evaluate("location.hash='p57'"); page.locator('#p57 input').fill('unknown')
        page.evaluate("location.hash='p74'")
        expect(page.locator('#p74')).to_be_visible()
        expect(page.locator('#submit-exam')).to_be_hidden()
        page.locator('#pager-next').click()
        expect(page.locator('#submit-exam')).to_be_visible()
        expect(page.locator('#pager-next')).to_be_hidden()
        page.locator('#submit-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        if width<600:
            expect(page.locator('#toggle-right')).to_have_attribute('aria-expanded','false')
            page.locator('#toggle-right').click()
        expect(page.locator('#panel-right-title')).to_have_text('채점표')
        cells=page.locator('#exam-scorecard td a')
        expect(cells).to_have_count(75)
        for id,symbol in [('p1','○'),('p2','×'),('p56','○'),('p57','?'),('p75','—')]:
            expect(page.locator('#exam-scorecard a[href="#'+id+'"]')).to_contain_text(symbol)
        assert page.locator('#exam-scorecard tr').count()==15
        assert page.locator('#exam-scorecard').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
        if width<600: page.locator('#panel-right [data-panel-close]').click()
        page.locator('#results-filter').select_option('incorrect')
        if width<600: page.locator('#toggle-right').click()
        expect(cells).to_have_count(75)
        page.locator('#exam-scorecard a[href="#p2"]').click()
        expect(page.locator('#exam-aid .answer')).to_be_visible()
        expect(page.locator('#panel-right-title')).to_have_text('풀이 도움')
        if width<600: page.locator('#panel-right [data-panel-close]').click()
        expect(page.locator('#p2')).to_be_visible()
        expect(page.locator('#submit-exam')).to_have_text('전체 결과')
        page.locator('#submit-exam').click()
        expect(page.locator('#results-title')).to_be_visible()
        if width<600: page.locator('#toggle-right').click()
        expect(cells).to_have_count(75)
        if width<600: page.locator('#panel-right [data-panel-close]').click()
        page.once('dialog',lambda d:d.accept());page.locator('#reset-exam').click()
        expect(page.locator('#submit-exam')).to_be_hidden()
        expect(cells).to_have_count(0)
        browser.close()
