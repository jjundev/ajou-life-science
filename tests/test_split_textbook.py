import unittest
import os
import tempfile
import fitz
from scripts.split_textbook import CHAPTERS, validate_metadata, split_pdf

class TestSplitTextbook(unittest.TestCase):
    def test_metadata_coverage(self):
        """총 522쪽이 1쪽부터 522쪽까지 누락 및 겹침 없이 연속되는지 검증"""
        self.assertEqual(len(CHAPTERS), 23)
        self.assertTrue(validate_metadata(CHAPTERS, total_pages=522))

    def test_validate_metadata_edge_cases(self):
        """validate_metadata의 비정상 케이스 탐지 검증"""
        # 빈 리스트
        self.assertFalse(validate_metadata([]))
        # 시작 페이지가 1이 아닌 경우
        self.assertFalse(validate_metadata([{"start": 2, "end": 10}]))
        # 연속성 단절(누락)
        self.assertFalse(validate_metadata([
            {"start": 1, "end": 10},
            {"start": 12, "end": 20}
        ], total_pages=20))
        # 중복(겹침)
        self.assertFalse(validate_metadata([
            {"start": 1, "end": 10},
            {"start": 10, "end": 20}
        ], total_pages=20))
        # 최종 페이지 불일치
        self.assertFalse(validate_metadata([
            {"start": 1, "end": 10}
        ], total_pages=20))

    def test_split_pdf_execution(self):
        """임시 디렉토리에서 PDF(4쪽) 분할 동작 및 무결성 검증"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = os.path.join(temp_dir, "test_src.pdf")
            temp_out = os.path.join(temp_dir, "test_out_dir")
            
            doc = fitz.open()
            for _ in range(4):
                doc.new_page()
            doc.save(temp_src)
            doc.close()

            dummy_meta = [
                {"id": "part1", "title": "Part 1", "start": 1, "end": 2, "filename": "p1.pdf"},
                {"id": "part2", "title": "Part 2", "start": 3, "end": 4, "filename": "p2.pdf"}
            ]
            
            res = split_pdf(temp_src, temp_out, dummy_meta)
            self.assertEqual(len(res), 2)
            
            doc1 = fitz.open(os.path.join(temp_out, "p1.pdf"))
            self.assertEqual(len(doc1), 2)
            doc1.close()
            
            doc2 = fitz.open(os.path.join(temp_out, "p2.pdf"))
            self.assertEqual(len(doc2), 2)
            doc2.close()

if __name__ == "__main__":
    unittest.main()
