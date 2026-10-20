"""본문 보충과 패널 요약의 대응·구분을 검사한다. 의미 충족도는 별도 검토다."""
import unittest
from pathlib import Path
from _util import SKILL
import check_html

LABEL = '보충 · 수업에서 다루지 않았어요'
GAP = '보충 · 노트에 빠졌던 수업 내용'


class TestSupplementSummary(unittest.TestCase):
    def codes(self, summary='', source_id='extra', label=LABEL, extra=''):
        source = (f'<html lang="ko"><body><span id="sum-for"></span>'
                  f'<article class="topic" id="t"><div class="layer supp" id="{source_id}">'
                  f'<span class="badge supp">{label}</span><p>본문 설명</p></div>'
                  f'<div class="sum" hidden><p class="sum-lead">수업 요약</p>{summary}</div>'
                  f'</article>{extra}</body></html>')
        return [p.code for p in check_html.check_common(check_html.parse_html(source), source, Path('note.html'))]

    def entry(self, label=LABEL, text='보충 핵심', target='extra'):
        return (f'<div class="sum-supp" data-supp-source="{target}">'
                f'<p class="sum-supp-label">{label}</p><ul><li>{text}</li></ul>'
                f'<a class="sum-supp-link" href="#{target}">본문 보충 보기</a></div>')

    def test_missing_summary_fails(self):
        self.assertIn('supp-summary-missing', self.codes())

    def test_both_labels_pass(self):
        for label in (LABEL, GAP):
            self.assertEqual(self.codes(self.entry(label=label), label=label), [])

    def test_source_requires_anchor(self):
        self.assertIn('supp-source-id', self.codes(source_id=''))

    def test_mismatched_label_fails(self):
        self.assertIn('supp-summary-label', self.codes(self.entry(label=GAP)))

    def test_empty_summary_fails(self):
        self.assertIn('supp-summary-empty', self.codes(self.entry(text=' ')))

    def test_duplicate_summary_fails(self):
        self.assertIn('supp-summary-duplicate', self.codes(self.entry() * 2))

    def test_wrong_topic_is_not_a_source(self):
        other = '<article class="topic" id="other"><div class="layer supp" id="foreign"></div></article>'
        self.assertIn('supp-summary-source', self.codes(self.entry(target='foreign'), extra=other))

    def test_link_must_return_to_source(self):
        self.assertIn('supp-summary-link', self.codes(self.entry().replace('href="#extra"', 'href="#t"')))

    def test_body_without_summary_panel_is_unaffected(self):
        source = '<html lang="ko"><body><article class="topic"><div class="layer supp">보충</div></article></body></html>'
        self.assertEqual(check_html.check_common(check_html.parse_html(source), source, Path('old.html')), [])

    def test_template_has_panel_styles(self):
        text = (SKILL / 'assets/note-template.html').read_text()
        self.assertIn('.sum-supp {', text)
        self.assertIn('.sum-supp-label {', text)


if __name__ == '__main__':
    unittest.main()
