import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from _util import SCRIPTS, card_html, overview_html, make_repo, make_set
import build
import check


def full_set(repo):
    cards = {i: overview_html(i) for i in ('o1', 'o2')}
    cards.update({f'p{i}': card_html(i, 'ABCDE'[(i-1) % 5]) for i in range(1,16)})
    return make_set(repo, 9, 1, cards)


class TestDualHtml(unittest.TestCase):
    def test_build_and_check_both_presentations(self):
        with tempfile.TemporaryDirectory() as temp:
            src = full_set(make_repo(Path(temp)))
            practice = build.build(src)
            exam = practice.with_name(practice.name.replace('_v', '_시험형_v'))
            self.assertTrue(exam.is_file(), '웹과제 생성 시 시험형도 필요')
            self.assertIn('href="#partA"', practice.read_text())
            self.assertNotIn('href="#partA"', exam.read_text())
            self.assertNotIn('<section id="partA">', exam.read_text())
            self.assertEqual(check.check(practice), [])
            self.assertEqual(check.check(exam), [])
            unrelated = exam.with_name('잘못된_시험형_v1.html')
            unrelated.write_text(exam.read_text())
            self.assertTrue(check.check(unrelated), '버전만 같은 임의 파일을 승인하면 안 됨')
            exam.write_text(exam.read_text().replace('문제 1번 발문이다?', '잘못 바뀐 문제?', 1))
            self.assertTrue(check.check(practice), '반대 형태의 변경도 감지해야 함')

    def test_exam_layout_rejects_reproducible_renderer_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            src = full_set(make_repo(Path(temp)))
            practice = build.build(src)
            current = build.render_exam(src)
            card1, card2 = (re.search(rf'<article class="card" id="p{i}">.*?</article>', current, re.S)[0]
                            for i in (1, 2))
            reversed_cards = current.replace(card1, 'CARD_PLACEHOLDER', 1).replace(card2, card1, 1)
            cases = {
                'partExtra': current.replace('<a href="#partC">', '<a href="#partExtra">분류표</a><a href="#partC">', 1)
                                    .replace('<section id="partC">', '<section id="partExtra"><h2>분류표</h2></section><section id="partC">', 1),
                'partC': re.sub(r'<a href="#partC">.*?</a>', '', current, count=1),
                'p1': reversed_cards.replace('CARD_PLACEHOLDER', card2, 1),
            }
            for target, broken in cases.items():
                with self.subTest(target=target):
                    self.assertNotEqual(broken, current)
                    build.exam_presentations.write_pair(src, {'practice': practice.read_text(), 'exam': broken})
                    # The same defect can exist in the published file and the renderer that produced it.
                    with patch.object(build, 'render_exam', return_value=broken):
                        errors = check.check(practice)
                    self.assertTrue(any('[exam-layout]' in error and target in error for error in errors), errors)

    def test_cli_distinguishes_legacy_exam_from_publishable_exam(self):
        with tempfile.TemporaryDirectory() as temp:
            src = full_set(make_repo(Path(temp)))
            practice = build.build(src)
            exam = practice.with_name(build.exam_presentations.names(build.load_pack(src))['exam'])
            legacy = build.render_exam(src, legacy_sections=True)
            build.exam_presentations.write_pair(src, {'practice': practice.read_text(), 'exam': legacy})
            for path in (practice, exam):
                with self.subTest(path=path.name):
                    cmd = [sys.executable, str(SCRIPTS / 'check.py')]
                    normal = subprocess.run([*cmd, str(path)], capture_output=True, text=True)
                    self.assertEqual(normal.returncode, 0, normal.stdout + normal.stderr)
                    self.assertIn('구버전 호환', normal.stdout)
                    strict = subprocess.run([*cmd, '--strict', str(path)], capture_output=True, text=True)
                    self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)
                    self.assertIn('재빌드', strict.stdout)

    def test_exam_navigation_excludes_overview_and_waits_for_submit(self):
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory() as temp:
            src = full_set(make_repo(Path(temp)))
            practice = build.build(src)
            exam = practice.with_name(practice.name.replace('_v', '_시험형_v'))
            self.assertTrue(exam.is_file(), '별도 시험형 HTML 누락')
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(viewport=dict(width=375, height=812), color_scheme='dark')
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(exam.as_uri()+'#p1')
                self.assertTrue(page.locator('.presentation-links').is_hidden())
                self.assertEqual(page.locator('.presentation-links a').count(), 0)
                page.wait_for_function('document.getElementById("progress-total").textContent === "15"')
                self.assertEqual(page.locator('main article.card').count(), 15)
                self.assertEqual(page.locator('#progress-total').text_content(), '15')
                page.locator('#p1 input[value="A"]').check()
                self.assertTrue(page.locator('#p2').is_visible())
                self.assertEqual(page.locator('.solution:visible').count(), 0)
                page.evaluate("location.hash='p15'")
                page.locator('#submit-exam').click()
                self.assertEqual(page.locator('#exam-scorecard td').count(), 15)
                self.assertTrue(page.locator('.presentation-links').is_visible())
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                page.locator('#results-list a[href="#p1"]').click()
                steps = page.locator('#exam-aid .solution ol.steps')
                self.assertTrue(steps.is_visible())
                self.assertTrue(steps.locator('li').first.inner_text().startswith('A.'))
                self.assertEqual(steps.locator('li').evaluate_all(
                    'items => items.map(item => getComputedStyle(item).listStyleType)'),
                    ['none'] * steps.locator('li').count())
                page.reload()
                self.assertTrue(page.locator('.presentation-links').is_hidden())
                self.assertTrue(page.locator('#exam-results').is_hidden())
                self.assertTrue(page.locator('#p1').is_visible())
                self.assertEqual(page.locator('input:checked').count(), 0)
                self.assertEqual(page.locator('#progress-n').text_content(), '0')
                page.goto(practice.as_uri()+'#p1')
                self.assertEqual(page.locator('.presentation-links a').count(), 0)
                page.locator('#p1 .review-choice').first.click()
                self.assertEqual(page.locator('#p1 .review-choice[data-selected="true"]').count(), 1)
                connection = page.locator('#panel-right .aid[data-card-id="p1"] .solution ol.steps > li')
                self.assertIn('수업과의 연결', connection.text_content())
                self.assertEqual(connection.evaluate('item => getComputedStyle(item).listStyleType'), 'none')
                page.reload()
                self.assertEqual(page.locator('.review-choice[data-selected="true"]').count(), 0)
                self.assertEqual(page.locator('#progress-n').text_content(), '0')
                self.assertEqual(errors, [])
                browser.close()
