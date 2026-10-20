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

    def test_legacy_without_panel_is_unaffected(self):
        self.assertEqual(self.codes('<div class="sum"></div>', panel=False), [])

    def test_closing_topic_without_summary_is_allowed(self):
        self.assertEqual(self.codes('', learning=False), [])


if __name__ == '__main__':
    unittest.main()
