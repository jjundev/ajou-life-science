import unittest
import xml.etree.ElementTree as ET
from scripts.question_bank.svg import validate_svg, inline_svg


class SvgTests(unittest.TestCase):
    def test_rejects_active_or_external_content(self):
        for content in ('<script>alert(1)</script>', '<image href="x.png"/>', '<foreignObject/>', '<a href="https://example.com"/>', '<path onclick="x()"/>', '<path fill="url(#x)"/>', '<path style="fill:red"/>', '<text xmlns="http://www.w3.org/1999/xhtml">x</text>'):
            with self.subTest(content=content):
                text = '<svg viewBox="0 0 10 10">' + content + '</svg>'
                self.assertTrue(validate_svg(text))
                with self.assertRaises(ValueError):
                    inline_svg(text, 'source-q09-exam', '구조식')

    def test_rejects_invalid_root_viewbox_and_declarations(self):
        for text in ('<g viewBox="0 0 10 10"/>', '<svg/>', '<svg viewBox="0 0 0 10"/>', '<svg viewBox="0 0 -1 10"/>', '<svg viewBox="0 0 NaN 10"/>', '<svg viewBox="0 0 inf 10"/>', '<svg viewBox="0 0 10"/>', '<svg viewBox="a 0 10 10"/>', '<svg', '<!DOCTYPE svg><svg viewBox="0 0 1 1"/>'):
            with self.subTest(text=text):
                self.assertTrue(validate_svg(text))

    def test_rejects_duplicate_ids_and_dangling_references(self):
        for content in ('<title id="x"/><desc id="x"/>', '<g aria-labelledby="missing"/>', '<title id="two words"/>'):
            self.assertTrue(validate_svg('<svg viewBox="0 0 10 10">' + content + '</svg>'))

    def test_internal_label_ids_are_prefixed_and_alt_is_escaped(self):
        text = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0,0,10,10" aria-labelledby="title description"><title id="title">분자 구조</title><desc id="description">원문 구조</desc><text x="1" y="5">H</text></svg>'
        result = inline_svg(text, 'web-ch01-q09-exam', '분자 & "구조"')
        root = ET.fromstring(result)
        self.assertEqual(root.attrib['aria-labelledby'], 'web-ch01-q09-exam-title web-ch01-q09-exam-description')
        self.assertEqual(root.attrib['role'], 'img')
        self.assertEqual(root.attrib['aria-label'], '분자 & "구조"')
        self.assertEqual([n.attrib['id'] for n in root if 'id' in n.attrib], ['web-ch01-q09-exam-title', 'web-ch01-q09-exam-description'])
        self.assertEqual(validate_svg(result), [])

    def test_stylesheet_processing_instruction_is_rejected(self):
        svg = '<?xml-stylesheet href="https://example.com/style.css"?><svg viewBox="0 0 1 1"/>'
        self.assertTrue(validate_svg(svg))

    def test_bad_prefix_is_rejected(self):
        for prefix in ('', 'two words', 'x" onclick="x'):
            with self.assertRaises(ValueError):
                inline_svg('<svg viewBox="0 0 10 10"/>', prefix, '구조')


class BankSvgTests(unittest.TestCase):
    def test_bank_rejects_unsafe_svg_even_with_matching_hash(self):
        import hashlib
        import tempfile
        from pathlib import Path
        from tests.question_bank_fixture import make_bank
        from scripts.question_bank.model import validate_bank
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, bank = make_bank(base)
            (base / 'image').mkdir()
            svg = base / 'image/q.svg'
            svg.write_text('<svg viewBox="0 0 10 10"><script/></svg>')
            entry = {'path': 'image/q.svg', 'sha256': hashlib.sha256(svg.read_bytes()).hexdigest(), 'alt': '구조'}
            bank['assets'] = [{'id': 'q01', 'exam': entry.copy(), 'explained': entry.copy(), 'source_ids': ['s1'], 'review': {'status': 'pending', 'payload_sha256': None, 'notes': None}}]
            errors = validate_bank(bank, base, repo_root=base)
            self.assertTrue(any('asset q01 exam' in error and 'forbidden SVG tag' in error for error in errors), errors)
            self.assertTrue(any('asset q01 explained' in error and 'forbidden SVG tag' in error for error in errors), errors)


class FigureArtifactTests(unittest.TestCase):
    def test_all_four_real_figures_are_valid_and_have_accessible_titles(self):
        from pathlib import Path
        from scripts.question_bank.model import resolve_local
        folder = resolve_local(Path(__file__).resolve().parents[1], '웹과제/1장/image')
        for name in ('q09.svg', 'q09.explained.svg', 'q14.svg', 'q14.explained.svg'):
            with self.subTest(name=name):
                value = (folder / name).read_text(encoding='utf-8')
                self.assertEqual(validate_svg(value), [])
                root = ET.fromstring(value)
                self.assertTrue(root.attrib['aria-label'])
                self.assertTrue(root.find('{http://www.w3.org/2000/svg}title').text)
                self.assertTrue(root.find('{http://www.w3.org/2000/svg}desc').text)
                if 'explained' not in name:
                    for answer in ('아미노산', '단백질', '정답', '인지질'):
                        self.assertNotIn(answer, value)

    def test_explanation_preserves_every_original_chemical_element(self):
        from pathlib import Path
        from scripts.question_bank.model import resolve_local
        folder = resolve_local(Path(__file__).resolve().parents[1], '웹과제/1장/image')
        for stem in ('q09', 'q14'):
            exam = ET.parse(folder / (stem + '.svg')).getroot()
            explained = ET.parse(folder / (stem + '.explained.svg')).getroot()
            exam_group = list(exam)[-1]
            explained_group = list(explained)[-1]
            self.assertGreater(len(explained_group), len(exam_group))
            for original, annotated in zip(exam_group, explained_group):
                original.tail = annotated.tail = None
                self.assertEqual(ET.tostring(original), ET.tostring(annotated))
