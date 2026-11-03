"""일반 페이지 요약의 구조를 검사한다. 의미 충족도는 본문 대조로 검토한다."""
import unittest
from pathlib import Path
from _util import SKILL
import check_html


class TestPageSummary(unittest.TestCase):
    def codes(self, summary, panel=True, learning=True):
        source = ('<html lang="ko"><body>'
                  + ('<span id="sum-for"></span>' if panel else '')
                  + '<article class="topic" id="t">'
                  + ('<div class="layer formal"><p>본문</p></div>' if learning else '')
                  + summary + '</article></body></html>')
        return [p.code for p in check_html.check_common(
            check_html.parse_html(source), source, Path('note.html'))]

    def test_empty_summary_fails(self):
        self.assertIn('sum-empty', self.codes('<div class="sum" hidden> </div>'))

    def test_missing_lead_fails(self):
        self.assertIn('sum-lead-missing', self.codes('<div class="sum" hidden><p>설명</p></div>'))

    def test_empty_lead_fails(self):
        self.assertIn('sum-lead-empty', self.codes('<div class="sum" hidden><p class="sum-lead"> </p></div>'))

    def test_duplicate_summary_fails(self):
        summary = '<div class="sum" hidden><p class="sum-lead">핵심</p></div>'
        self.assertIn('sum-duplicate', self.codes(summary * 2))

    def test_duplicate_lead_fails(self):
        self.assertIn('sum-lead-duplicate', self.codes(
            '<div class="sum" hidden><p class="sum-lead">가</p><p class="sum-lead">나</p></div>'))

    def test_nested_lead_does_not_replace_direct_lead(self):
        self.assertIn('sum-lead-missing', self.codes(
            '<div class="sum" hidden><div><p class="sum-lead">핵심</p></div></div>'))

    def test_four_terms_are_allowed(self):
        terms = ''.join(f'<dt>개념{i}</dt><dd>뜻{i}</dd>' for i in range(4))
        self.assertEqual(self.codes('<div class="sum" hidden><p class="sum-lead">핵심</p>'
            '<p class="panel-label">용어</p><dl class="terms">' + terms + '</dl></div>'), [])

    def test_lead_repeating_any_term_fails(self):
        for terms in (
            '<dt>점진주의</dt><dd>작은 변화가 누적돼요.</dd><dt>단속평형</dt><dd>정체와 변화가 번갈아요.</dd>',
            '<dt>단속평형</dt><dd>정체와 변화가 번갈아요.</dd><dt>점진주의</dt><dd>작은 변화가 누적돼요.</dd>',
        ):
            with self.subTest(terms=terms):
                self.assertIn('sum-lead-repeats-term', self.codes(
                    '<div class="sum" hidden><p class="sum-lead">작은 변화가 누적돼요.</p>'
                    '<p class="panel-label">용어</p><dl class="terms">' + terms + '</dl></div>'))

    def test_repetition_ignores_inline_markup_entities_whitespace_and_unicode_form(self):
        self.assertIn('sum-lead-repeats-term', self.codes(
            '<div class="sum" hidden><p class="sum-lead">가 나 다.</p>'
            '<p class="panel-label">용어</p><dl class="terms"><dt>표지</dt>'
            '<dd><b>가</b>&nbsp; 나\n 다.</dd></dl></div>'))

    def test_repeat_diagnostic_identifies_topic_and_term(self):
        source = ('<div id="sum-for"></div><article class="topic" id="rates">'
                  '<div class="sum" hidden><p class="sum-lead">작은 변화가 누적돼요.</p>'
                  '<dl class="terms"><dt>점진주의</dt><dd>작은 변화가 누적돼요.</dd></dl>'
                  '</div></article>')
        problems = check_html.page_summary_problems(source)
        repeats = [p for p in problems if p.code == 'sum-lead-repeats-term']
        self.assertEqual(len(repeats), 1)
        self.assertEqual(repeats[0].where, 'rates')
        self.assertIn('점진주의', repeats[0].detail)

    def test_distinct_lead_and_partial_matches_are_allowed(self):
        for lead in ('점진주의와 단속평형은 변화 속도의 양상이에요.',
                     '작은 변화가 누적돼요. 점진주의의 설명이에요.',
                     '작은 변화가 누적돼요!'):
            with self.subTest(lead=lead):
                self.assertEqual(self.codes(
                    '<div class="sum" hidden><p class="sum-lead">' + lead + '</p>'
                    '<p class="panel-label">용어</p><dl class="terms">'
                    '<dt>점진주의</dt><dd>작은 변화가 누적돼요.</dd></dl></div>'), [])

    def test_lead_without_terms_is_allowed(self):
        self.assertEqual(self.codes(
            '<div class="sum" hidden><p class="sum-lead">핵심 관계예요.</p></div>'), [])

    def test_repeated_term_in_another_topic_is_allowed(self):
        source = ('<div id="sum-for"></div><article class="topic" id="a">'
                  '<div class="sum" hidden><p class="sum-lead">공통 개념이에요.</p></div>'
                  '</article><article class="topic" id="b"><div class="sum" hidden>'
                  '<p class="sum-lead">다른 핵심이에요.</p><dl class="terms">'
                  '<dt>개념</dt><dd>공통 개념이에요.</dd></dl></div></article>')
        self.assertEqual(check_html.page_summary_problems(source), [])

    def test_repeated_lead_without_panel_is_unaffected(self):
        self.assertEqual(self.codes(
            '<div class="sum" hidden><p class="sum-lead">핵심이에요.</p>'
            '<p class="panel-label">용어</p><dl class="terms">'
            '<dt>핵심</dt><dd>핵심이에요.</dd></dl></div>', panel=False), [])

    def test_legacy_without_panel_is_unaffected(self):
        self.assertEqual(self.codes('<div class="sum"></div>', panel=False), [])

    def test_closing_topic_without_summary_is_allowed(self):
        self.assertEqual(self.codes('', learning=False), [])


if __name__ == '__main__':
    unittest.main()
