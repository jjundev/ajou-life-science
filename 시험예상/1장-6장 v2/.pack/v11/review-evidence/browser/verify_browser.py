"""Real-Chromium verification of the v11 exam page against references/exam-ui.md and verification.md (browser)."""
import json, sys, time
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

REPO = Path(r"C:/Users/Hyunjun/Desktop/현준대학/26-2/생명과학")
SRC = REPO / '시험예상/1장-6장/.pack/v11'
HTML = REPO / '시험예상/1장-6장/시험예상문제_1장-6장_v11.html'
URL = 'http://127.0.0.1:8765/' + quote('시험예상/1장-6장/시험예상문제_1장-6장_v11.html')
OUT = SRC / 'review-evidence/browser'
OUT.mkdir(parents=True, exist_ok=True)
pack = json.load(open(SRC / 'pack.json', encoding='utf-8'))
P = {p['id']: p for p in pack['problems']}
IDS = [f'p{i}' for i in range(1, 76)]

def wrong(p):
    ids = [o['id'] for o in p['options']]
    return next(i for i in ids if i != p['answer']['option_id'])

def run(width, height, scheme, mode):
    rec = dict(width=width, height=height, scheme=scheme, mode=mode, checks={}, errors=[], remote=[], failed=[], console_errors=[])
    C = rec['checks']
    def ok(name, cond, detail=''):
        C[name] = dict(pass_=bool(cond), detail=str(detail)[:400])
        if not cond: print('  FAIL', width, scheme, mode, name, detail)
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport=dict(width=width, height=height), color_scheme=scheme, accept_downloads=True)
        page = ctx.new_page()
        page.on('pageerror', lambda e: rec['errors'].append(str(e)))
        page.on('console', lambda m: rec['console_errors'].append(m.text) if m.type == 'error' else None)
        page.on('request', lambda r: rec['remote'].append(r.url) if not r.url.startswith(('http://127.0.0.1:8765', 'data:', 'blob:')) else None)
        page.on('requestfailed', lambda r: rec['failed'].append(r.url))
        page.goto(URL); page.wait_for_load_state('networkidle')
        def go(h):
            page.evaluate('(h)=>{location.hash=h}', h); page.wait_for_timeout(60)
        def cur():
            return page.evaluate("location.hash")
        def nooverflow():
            return page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        # Theme actually applied
        bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
        rec['body_background'] = bg
        # Toolbar
        ok('toolbar_single_reset', page.locator('#reset-exam').count() == 1 and page.get_by_role('button', name='다시 풀기').count() == 1)
        ok('cover_submit_hidden', not page.locator('#submit-exam').is_visible())
        page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-toolbar.png'))
        # 75 cards, titles, toc, overflow, images
        bad_title, overflow, imgs_bad = [], [], []
        for pid in IDS:
            go(pid)
            card = page.locator('#' + pid)
            h3 = card.locator('h3').first.inner_text().strip()
            toc = page.locator(f'.toc-list a[href="#{pid}"] .toc-title').text_content().strip()
            exp = f"{pid}. {P[pid]['concept_summary']}"
            if not (card.is_visible() and h3 == exp and toc == exp): bad_title.append((pid, h3, toc))
            if not nooverflow(): overflow.append(pid)
            for im in card.locator('img').all():
                if not page.evaluate('(e)=>e.complete && e.naturalWidth>0', im.element_handle()): imgs_bad.append(pid)
            if pid in ('p2', 'p30', 'p54'):
                ok(f'middle_submit_hidden_{pid}', not page.locator('#submit-exam').is_visible())
        ok('all75_titles_match_body_and_toc', not bad_title, bad_title[:3])
        ok('no_horizontal_overflow_all_cards', not overflow, overflow[:5])
        ok('figures_loaded', not imgs_bad and page.locator('article.card img').count() == 5, imgs_bad)
        ok('choices_render_55', page.locator('article.card ul.choices').count() == 55 and page.locator('.exam-input input[type=radio]').count() == sum(len(P[i]['options']) for i in IDS[:55]))
        ok('short_inputs_20', page.locator('.exam-input input[type=text]').count() == 20)
        # Right panel title does not repeat the card title before submit
        go('p3')
        ok('aid_panel_no_title_repeat_before_submit', P['p3']['concept_summary'] not in page.locator('#panel-right').inner_text())
        # MCQ auto advance, preserve, change, focus
        go('p1'); page.locator('#p1 input[value="%s"]' % wrong(P['p1'])).check(); page.wait_for_timeout(120)
        ok('mcq_auto_advance', cur() == '#p2', cur())
        ok('focus_moves_to_next_title', page.evaluate("document.activeElement && document.activeElement.closest('#p2') && document.activeElement.tagName=='H3'"))
        ok('no_reveal_after_select', page.locator('.solution:visible').count() == 0 and page.locator('#p1 .result').inner_text() == '')
        go('p1'); ok('answer_preserved_after_back', page.locator('#p1 input:checked').get_attribute('value') == wrong(P['p1']))
        page.locator('#p1 input[value="%s"]' % P['p1']['answer']['option_id']).check(); page.wait_for_timeout(120)
        ok('changed_answer_moves_again', cur() == '#p2' and page.evaluate("document.querySelector('#p1 input:checked').value") == P['p1']['answer']['option_id'])
        go('p55'); page.locator('#p55 input[value="%s"]' % P['p55']['answer']['option_id']).check(); page.wait_for_timeout(120)
        ok('last_mcq_to_first_short', cur() == '#p56', cur())
        page.locator('#p56 input').fill('과당 '); page.wait_for_timeout(200)
        ok('short_no_auto_advance', cur() == '#p56' and not page.locator('#exam-results').is_visible())
        # Answer plan
        plan = {}
        if mode == 'mixed':
            for i, pid in enumerate(IDS[:55]):
                if pid in ('p1', 'p55'): continue
                if i % 7 == 3: continue  # unanswered
                plan[pid] = wrong(P[pid]) if i % 5 == 2 else P[pid]['answer']['option_id']
            shorts = {}
            for j, pid in enumerate(IDS[55:]):
                a = P[pid]['answer']
                if j % 4 == 0: shorts[pid] = a['canonical']
                elif j % 4 == 1: shorts[pid] = (a['accepted'][-1].upper() if not a['case_sensitive'] else a['accepted'][-1])
                elif j % 4 == 2: shorts[pid] = '모르겠음'
            shorts['p56'] = '과당 '
        else:
            for pid in IDS[:55]:
                if pid not in ('p1', 'p55'): plan[pid] = P[pid]['answer']['option_id']
            shorts = {pid: P[pid]['answer']['canonical'] for pid in IDS[55:]}
            shorts['p56'] = '과당 '
        for pid, v in plan.items():
            go(pid); page.locator(f'#{pid} input[value="{v}"]').check()
        for pid, v in shorts.items():
            go(pid); page.locator(f'#{pid} input').fill(v)
        go('p75'); page.wait_for_timeout(100)
        ok('last_shows_submit_hides_first', page.locator('#submit-exam').is_visible() and not page.locator('#pager-next').is_visible(), page.locator('#pager-next').inner_text())
        ok('no_reveal_before_submit', page.locator('article.card .solution:visible, article.card .provenance:visible').count() == 0)
        page.emulate_media(media='print'); ok('print_hides_before_submit', page.locator('.solution:visible').count() == 0); page.emulate_media(media='screen')
        page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-last-question.png'))
        page.locator('#submit-exam').click(); page.wait_for_timeout(300)
        ok('results_route', cur() == '#exam-results' and page.locator('#exam-results').is_visible())
        ok('inputs_locked', page.evaluate("[...document.querySelectorAll('.exam-input input')].every(n=>n.disabled)"))
        ok('all_results_filled', page.evaluate("[...document.querySelectorAll('article.card .result')].every(n=>n.textContent.trim())"))
        rows = page.locator('.exam-result-row'); ok('result_rows_75', rows.count() == 75)
        res = page.evaluate("[...document.querySelectorAll('.exam-result-row')].map(r=>r.dataset.result)")
        from collections import Counter
        cnt = Counter(res); rec['result_counts'] = dict(cnt)
        # expected
        exp = {}
        for pid in IDS[:55]:
            v = {'p1': P['p1']['answer']['option_id'], 'p55': P['p55']['answer']['option_id']}.get(pid, plan.get(pid))
            exp[pid] = 'unanswered' if v is None else ('correct' if v == P[pid]['answer']['option_id'] else 'incorrect')
        for pid in IDS[55:]:
            v = shorts.get(pid)
            if v is None or not v.strip(): exp[pid] = 'unanswered'
            else:
                a = P[pid]['answer']; n = lambda s: s.strip() if a['case_sensitive'] else s.strip().casefold()
                exp[pid] = 'matched' if n(v) in {n(x) for x in [a['canonical'], *a['accepted']]} else 'pending'
        ok('results_match_expected', res == [exp[i] for i in IDS], [(i, r, exp[i]) for i, r in zip(IDS, res) if r != exp[i]][:5])
        # scorecard
        desktop = width >= 1024
        ok('panel_title_scorecard', page.locator('#panel-right-title').text_content() == '채점표' and page.locator('#toggle-right span').text_content() == '채점표')
        ok('scorecard_panel_open_state', (page.locator('#toggle-right').get_attribute('aria-expanded') == 'true') == desktop)
        if not desktop:
            page.locator('#toggle-right').click(); page.wait_for_timeout(450)
            ok('mobile_scorecard_opens', page.locator('#exam-scorecard').is_visible())
            page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-scorecard.png'))
            page.locator('#panel-right [data-panel-close]').click(); page.wait_for_timeout(450)
            ok('mobile_scorecard_closes', not page.locator('#exam-scorecard').is_visible() and page.locator('#toggle-right').get_attribute('aria-expanded') == 'false')
        sc = page.evaluate("(()=>{const t=document.getElementById('exam-scorecard');return {rows:t.tBodies[0].rows.length,cols:[...t.tBodies[0].rows].map(r=>r.cells.length),links:[...t.querySelectorAll('a')].map(a=>[a.textContent,a.dataset.result,a.getAttribute('aria-label')])}})()")
        sym = {'correct': '○', 'incorrect': '×', 'matched': '○', 'pending': '?', 'unanswered': '—'}
        ok('scorecard_5col_75', sc['rows'] == 15 and all(c == 5 for c in sc['cols']) and len(sc['links']) == 75)
        ok('scorecard_symbols', all(t == f'{i+1} {sym[exp[IDS[i]]]}' and r == exp[IDS[i]] and lab.startswith(f'{i+1}번') and '문제와 해설 보기' in lab for i, (t, r, lab) in enumerate(sc['links'])))
        page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-results.png'), full_page=False)
        # filters (scorecard unaffected)
        fl = {}
        for val in ['all', 'correct', 'incorrect', 'matched', 'pending', 'unanswered']:
            page.select_option('#results-filter', val); page.wait_for_timeout(50)
            shown = page.locator('.exam-result-row:visible').count()
            fl[val] = (shown, page.locator('#results-empty').is_visible(), page.locator('#exam-scorecard a').count())
        rec['filters'] = fl
        ok('filters_consistent', all(fl[k][0] == (75 if k == 'all' else cnt.get(k, 0)) and fl[k][1] == (fl[k][0] == 0) and fl[k][2] == 75 for k in fl), fl)
        if mode == 'allcorrect': ok('empty_category_message', fl['incorrect'][0] == 0 and fl['incorrect'][1])
        page.select_option('#results-filter', 'all')
        # review prompt copy (replaces JSON export since skill commit 62f2093)
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='http://127.0.0.1:8765')
        page.locator('#copy-prompt').click(); page.wait_for_timeout(400)
        txt = page.evaluate("navigator.clipboard.readText()").replace('\r\n', '\n')  # Windows clipboard returns CRLF
        (OUT / f'{width}-{scheme}-{mode}-prompt.txt').write_text(txt, encoding='utf-8')
        rec['prompt_chars'] = len(txt)
        ok('prompt_copied_status', '복사했어요' in page.locator('#prompt-status').inner_text(), page.locator('#prompt-status').inner_text())
        ok('prompt_header_and_doc', txt.startswith('# 생명과학 복기 요청') and HTML.name in txt and '시험 예상문제' in txt)
        import re as _re
        def section(name):
            m = _re.search(r'### ' + _re.escape(name) + r'\n(.*?)(?=\n### |\n## |\Z)', txt, _re.S)
            return set(_re.findall(r'^#### (p\d+)\.', m.group(1), _re.M)) if m else set()
        want = {k: {i for i in IDS if exp[i] == k} for k in ('incorrect', 'pending', 'unanswered')}
        got = {'incorrect': section('오답'), 'pending': section('자기채점 대기'), 'unanswered': section('미응답')}
        ok('prompt_groups_match_results', got == want, {k: (sorted(got[k] - want[k])[:3], sorted(want[k] - got[k])[:3]) for k in got})
        cm = _re.search(r'## 확신 있게 맞힌 문항\n(.*?)(?=\n\n|\Z)', txt, _re.S)
        conf = set(_re.findall(r'^- (p\d+)\.', cm.group(1), _re.M)) if cm else set()
        ok('prompt_correct_titles_only', conf == {i for i in IDS if exp[i] in ('correct', 'matched')})
        ok('prompt_raw_input_kept', ('내 답: "과당 "' in txt) if exp.get('p56') == 'pending' else True)
        ok('prompt_no_rendered_math', 'katex' not in txt.lower() and '<' not in txt.replace('<-', ''))
        ok('summary_text_consistent', f"정답률" in page.locator('#results-summary').inner_text())
        # clipboard blocked -> direct copy dialog
        page.evaluate("()=>{navigator.clipboard.writeText=()=>Promise.reject(new Error('blocked')); document.execCommand=()=>false; return 1}")
        page.locator('#copy-prompt').click(); page.wait_for_timeout(400)
        dlg = page.locator('dialog[open], [role=dialog]:visible textarea, textarea:visible').first
        ta = page.locator('textarea:visible').first
        ok('prompt_dialog_fallback', ta.count() == 1 and ta.input_value().startswith('# 생명과학 복기 요청')
           and page.evaluate("(()=>{const t=[...document.querySelectorAll('textarea')].find(x=>x.offsetParent);return t && t.selectionEnd - t.selectionStart === t.value.length})()"),
           page.locator('#prompt-status').inner_text())
        page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-prompt-dialog.png'))
        close = page.get_by_role('button', name='닫기').last
        close.click(); page.wait_for_timeout(200)
        ok('copy_failure_keeps_results', page.locator('.exam-result-row').count() == 75)
        ok('refresh_notice_present', '새로고침' in page.locator('#exam-results').inner_text())
        # result row -> card + solution in panel -> back/forward sync
        page.locator('.exam-result-row a[href="#p5"]').scroll_into_view_if_needed(); page.locator('.exam-result-row a[href="#p5"]').click(); page.wait_for_timeout(200)
        ok('row_link_opens_card', cur() == '#p5' and page.locator('#p5').is_visible())
        if not desktop and page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
            page.locator('#toggle-right').click(); page.wait_for_timeout(450)
        panel = page.locator('#panel-right').inner_text()
        ok('panel_shows_solution_and_source', page.locator('#panel-right-title').text_content() == '풀이 도움' and '출처 보기' in panel and P['p5']['concept_summary'] not in panel)
        page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-review.png'))
        if not desktop: page.locator('#panel-right [data-panel-close]').click(); page.wait_for_timeout(450)
        page.go_back(); page.wait_for_timeout(250)
        ok('back_to_results_syncs_panel', cur() == '#exam-results' and page.locator('#panel-right-title').text_content() == '채점표' and page.locator('#exam-results').is_visible())
        page.go_forward(); page.wait_for_timeout(250)
        ok('forward_to_card_syncs_panel', cur() == '#p5' and page.locator('#panel-right-title').text_content() == '풀이 도움')
        page.locator('#submit-exam').click(); page.wait_for_timeout(200)
        ok('all_results_button_returns', cur() == '#exam-results')
        # scorecard link navigation
        if not desktop and page.locator('#toggle-right').get_attribute('aria-expanded') != 'true':
            page.locator('#toggle-right').click(); page.wait_for_timeout(450)
        page.locator('#exam-scorecard a').nth(60).focus(); page.keyboard.press('Enter'); page.wait_for_timeout(200)
        ok('scorecard_link_navigates', cur() == '#p61')
        go('exam-results')
        # keyboard focus
        page.keyboard.press('Tab'); ok('keyboard_focus_moves', page.evaluate("document.activeElement && document.activeElement!==document.body"))
        # print of results
        page.emulate_media(media='print'); page.screenshot(path=str(OUT / f'{width}-{scheme}-{mode}-results-print.png'))
        ok('results_print_visible', page.locator('#exam-results').is_visible()); page.emulate_media(media='screen')
        ok('no_overflow_results', nooverflow())
        if not desktop and page.locator('#toggle-right').get_attribute('aria-expanded') == 'true':
            page.locator('#panel-right [data-panel-close]').click(); page.wait_for_timeout(450)
        # reset: cancel then accept
        page.once('dialog', lambda d: (rec.__setitem__('reset_msg', d.message), d.dismiss())); page.locator('#reset-exam').click(); page.wait_for_timeout(150)
        ok('reset_confirm_mentions_prompt', '복기 프롬프트' in rec.get('reset_msg',''), rec.get('reset_msg'))
        ok('reset_cancel_keeps', page.locator('.exam-result-row').count() == 75 and page.evaluate("document.querySelector('.exam-input input').disabled"))
        page.once('dialog', lambda d: d.accept()); page.locator('#reset-exam').click(); page.wait_for_timeout(250)
        ok('reset_clears', cur() == '#p1' and page.locator('input:checked').count() == 0 and page.locator('.exam-result-row').count() == 0
           and page.evaluate("[...document.querySelectorAll('.exam-input input[type=text]')].every(n=>n.value==='' && !n.disabled)")
           and page.locator('.solution:visible').count() == 0 and page.locator('#exam-scorecard').count() == 0 and page.locator('#submit-exam').inner_text() == '전체 제출')
        ok('no_js_errors', not rec['errors'] and not rec['console_errors'], rec['errors'][:3] + rec['console_errors'][:3])
        ok('no_external_requests_or_failures', not rec['remote'] and not rec['failed'], rec['remote'][:3] + rec['failed'][:3])
        b.close()
    rec['status'] = 'pass' if all(v['pass_'] for v in C.values()) else 'fail'
    return rec

def nojs():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True); pg = b.new_page(java_script_enabled=False); pg.goto(URL)
        r = pg.locator('.solution:visible, .provenance:visible').count() == 0
        pg.emulate_media(media='print'); r = r and pg.locator('.solution:visible').count() == 0
        b.close(); return r

if __name__ == '__main__':
    out = dict(url=URL, html=str(HTML), runs=[])
    for (w, h) in [(1280, 900), (375, 812)]:
        for s in ['light', 'dark']:
            for mode in ['mixed', 'allcorrect']:
                r = run(w, h, s, mode); out['runs'].append(r); print(w, s, mode, r['status'], r.get('result_counts'), r['body_background'])
    out['no_js'] = 'pass' if nojs() else 'fail'
    out['status'] = 'pass' if all(r['status'] == 'pass' for r in out['runs']) and out['no_js'] == 'pass' else 'fail'
    json.dump(out, open(OUT / 'browser-verification.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('NOJS', out['no_js'], 'OVERALL', out['status'])
