import os
import unittest
import fitz
from scripts.split_textbook import CHAPTERS


class TestGeneratedFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.output_dir = os.path.join(cls.repo_root, "교과서", "장별")

    def test_all_files_exist_and_match_pages(self):
        """교과서/장별/ 디렉토리 내 23개 분할 PDF 파일 존재 및 페이지 수, 렌더링 무결성 검증"""
        if not os.path.isdir(self.output_dir):
            self.skipTest("분할 PDF가 아직 생성되지 않았습니다. scripts/split_textbook.py를 먼저 실행하세요.")

        pdf_files = [f for f in os.listdir(self.output_dir) if f.endswith(".pdf")]
        if not pdf_files:
            self.skipTest("분할 PDF가 아직 생성되지 않았습니다. scripts/split_textbook.py를 먼저 실행하세요.")

        self.assertEqual(
            len(pdf_files),
            len(CHAPTERS),
            f"PDF 파일 수가 일치하지 않습니다. 예상: {len(CHAPTERS)}, 실제: {len(pdf_files)}"
        )

        total_pages = 0

        for item in CHAPTERS:
            filename = item["filename"]
            file_path = os.path.join(self.output_dir, filename)

            # 1. 파일 존재 검증
            self.assertTrue(
                os.path.isfile(file_path),
                f"파일이 존재하지 않습니다: {filename}"
            )

            # 2. PyMuPDF로 파일 열기 및 페이지 수 검증
            with fitz.open(file_path) as doc:
                expected_pages = item["end"] - item["start"] + 1
                actual_pages = doc.page_count

                self.assertEqual(
                    actual_pages,
                    expected_pages,
                    f"{filename}의 페이지 수 불일치. 예상: {expected_pages}, 실제: {actual_pages}"
                )
                total_pages += actual_pages

                # 3. 첫 페이지 및 마지막 페이지 렌더링 검증
                first_page = doc.load_page(0)
                pix_first = first_page.get_pixmap(dpi=72)
                self.assertGreater(pix_first.width, 0, f"{filename} 첫 페이지 렌더링 너비 오류")
                self.assertGreater(pix_first.height, 0, f"{filename} 첫 페이지 렌더링 높이 오류")

                last_page = doc.load_page(actual_pages - 1)
                pix_last = last_page.get_pixmap(dpi=72)
                self.assertGreater(pix_last.width, 0, f"{filename} 마지막 페이지 렌더링 너비 오류")
                self.assertGreater(pix_last.height, 0, f"{filename} 마지막 페이지 렌더링 높이 오류")

        # 4. 총합 페이지 수가 522쪽인지 검증
        self.assertEqual(
            total_pages,
            522,
            f"총 페이지 수가 522쪽이 아닙니다. 실제 합계: {total_pages}"
        )


if __name__ == "__main__":
    unittest.main()
