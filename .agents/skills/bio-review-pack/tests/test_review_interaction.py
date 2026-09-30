import unittest
from _util import SKILL, REPO
import review_interaction as ri

CARD = '''<article class="card" id="p1"><div class="problem"><p>틀린 것을 고르시오.</p>
<ul class="choices"><li>(1) 옳은 설명</li><li>(2) 틀린 설명</li></ul></div>
<details class="solution"><summary>풀이 보기</summary><ol class="steps">
<li>(1) 맞는 설명이므로 답이 아니에요.</li><li>(2) 틀린 설명이므로 답이에요.</li>
<li>수업과의 연결: 분류</li></ol><p class="answer">정답: (2)</p></details></article>'''

class TestModel(unittest.TestCase):
    def test_negative(self):
        m = ri.build_model(CARD, 'test.html')
        self.assertEqual(m['errors'], [])
        self.assertEqual(m['cards']['p1']['answer'], '2')
        self.assertEqual([o['diagnostic'] for o in m['cards']['p1']['options']], [0, 1])

    def test_letters(self):
        m = ri.build_model(CARD.replace('(1)', 'A.').replace('(2)', 'B.').replace('정답: B.', '정답: B'), 'test.html')
        self.assertEqual(m['cards']['p1']['answer'], 'B')

    def test_missing_and_duplicate(self):
        for source in (CARD.replace('<li>(2) 틀린 설명이므로 답이에요.</li>', ''), CARD.replace('(2)', '(1)')):
            m = ri.build_model(source, 'test.html')
            self.assertNotIn('p1', m['cards'])
            self.assertTrue(m['errors'])

    def test_static(self):
        self.assertEqual(ri.build_model('<article class="card" id="p1">빈칸</article>', 'test.html')['skipped'], ['p1'])

    def test_version(self):
        a = ri.build_model(CARD, 'test.html')['cards']['p1']['version']
        b = ri.build_model(CARD.replace('정답: (2)', '정답: (1)'), 'test.html')['cards']['p1']['version']
        self.assertNotEqual(a, b)

    def test_ambiguous(self):
        overrides = {'test.html': {'p1': {'mode':'ambiguous', 'notice':'두 해석이 가능해요.'}}}
        m = ri.build_model(CARD, 'test.html', overrides)
        self.assertEqual(m['cards']['p1']['mode'], 'ambiguous')
        self.assertEqual(m['cards']['p1']['notice'], '두 해석이 가능해요.')

    def test_alternative_wording_requires_explicit_review(self):
        for note in ['답이 하나로 딱 떨어지지 않아요.', '해석에 따라 보기 (1)도 성립할 수 있어요.']:
            source = CARD.replace('</details>', '<p>'+note+'</p></details>')
            self.assertEqual(ri.build_model(source, 'test.html')['errors'][0]['reason'], '모호성 문구 수동 검토 필요')

    def test_explicit_mapping(self):
        source = CARD.replace('(1) 맞는', '설명 하나').replace('(2) 틀린 설명이므로', '설명 둘')
        source = source.replace('<li>설명 하나', '<li data-explains="1">설명 하나').replace('<li>설명 둘', '<li data-explains="2">설명 둘')
        self.assertEqual(ri.build_model(source, 'test.html')['errors'], [])

    def test_install_idempotent(self):
        source = '<html><body>' + CARD + '</body></html>'
        output = ri.install(source, 'test.html')
        self.assertIn(CARD, output)
        self.assertEqual(ri.install(output, 'test.html'), output)
        self.assertEqual(output.count('id="review-interaction-model"'), 1)

    def test_install_adds_pager_leave_event_once(self):
        pager = '\n'.join([
            '<script id="pager-ui">',
            '      function render(i, target) {',
            '        if (i !== cur) {',
            "          if (cur >= 0) screens[cur].classList.remove('is-current', 'enter-next', 'enter-prev');",
            '        }',
            '      }',
            '</script>'])
        source = '<html><body>' + CARD + pager + '</body></html>'
        output = ri.install(source, 'test.html')
        marker = "detail: { index: cur, screen: screens[cur] }"
        self.assertEqual(output.count(marker), 1)
        self.assertLess(output.index(marker), output.index("screens[cur].classList.remove"))
        self.assertEqual(ri.install(output, 'test.html'), output)

    def test_pager_patch_leaves_pages_without_pager_alone(self):
        source = '<html><body>' + CARD + '</body></html>'
        self.assertEqual(ri.patch_pager_shell(source), source)

    def test_pager_patch_rejects_unknown_pager_structure(self):
        with self.assertRaises(ValueError):
            ri.patch_pager_shell('<script id="pager-ui">function render(){}</script>')

    def test_review_template_already_has_pager_leave_event(self):
        template = (SKILL / 'assets/review-template.html').read_text(encoding='utf-8')
        self.assertEqual(ri.patch_pager_shell(template), template)
        self.assertEqual(template.count("detail: { index: cur, screen: screens[cur] }"), 1)

    def test_existing_packs_embed_current_interaction_assets(self):
        files = sorted((REPO / '복습노트').glob('*/복습문제_*.html'))
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            with self.subTest(file=path.name):
                source = path.read_text(encoding='utf-8')
                self.assertEqual(ri.install(source, path.name), source)

    def test_assets_have_no_help_text(self):
        for name in ('review-interaction.js', 'review-interaction.css'):
            text = (SKILL / 'assets' / name).read_text(encoding='utf-8')
            with self.subTest(asset=name):
                self.assertNotIn('review-help', text)
                self.assertNotIn('해설이 열려요', text)
                self.assertNotIn('다른 보기도 눌러', text)

    def test_generated_packs_have_no_help_text(self):
        files = sorted((REPO / '복습노트').glob('**/복습문제_*.html'))
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            text = path.read_text(encoding='utf-8')
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertNotIn('review-help', text)
                self.assertNotIn('해설이 열려요', text)

    def test_safe_json(self):
        override = {'test.html': {'p1': {'mode':'ambiguous','notice':'</script><script>alert(1)</script>'}}}
        output = ri.install('<body>'+CARD+'</body>', 'test.html', override)
        self.assertNotIn('"notice": "</script>', output)
        self.assertIn('\\u003c/script>', output)

    def test_tampered_model(self):
        m = ri.build_model(CARD, 'test.html')
        m['cards']['p1']['answer'] = 'X'
        self.assertTrue(ri.validate_model(CARD, m))

    def test_checker_rejects_tampered_embedded_model(self):
        from check_html import check_common, parse_html
        source = ri.install('<html lang="ko"><body>'+CARD+'</body></html>', 'test.html')
        source = source.replace('"answer": "2"', '"answer": "X"')
        errors = check_common(parse_html(source), source, REPO / 'test.html')
        self.assertTrue(any(e.code == 'review-interaction' for e in errors))

    def test_strict_missing_diagnostic_and_static_fallback(self):
        source = '<body>'+CARD.replace('<li>(2) 틀린 설명이므로 답이에요.</li>','')+'</body>'
        with self.assertRaises(ValueError):
            ri.install(source,'test.html')
        self.assertIn('풀이 보기',ri.install(source,'test.html',strict=False))

    def test_duplicate_id_rejected(self):
        self.assertTrue(ri.build_model(CARD+CARD,'test.html')['errors'])

    def test_all_packs(self):
        files = sorted((REPO / '복습노트').glob('*/복습문제_*.html'))
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            with self.subTest(file=path.name):
                self.assertEqual(ri.build_model(path.read_text(encoding='utf-8'), path.name)['errors'], [])

    def test_existing_alternative_interpretations_are_not_binary_graded(self):
        cases = {'0910':['p4','p28','p40'], '0915':['p3'], '0917':['p2','p17'], '0922':['p12']}
        for date, ids in cases.items():
            path = next((REPO / '복습노트' / date).glob('복습문제*.html'))
            model = ri.build_model(path.read_text(encoding='utf-8'), path.name)
            for cid in ids:
                with self.subTest(date=date, card=cid):
                    self.assertEqual(model['cards'][cid]['mode'], 'ambiguous')
