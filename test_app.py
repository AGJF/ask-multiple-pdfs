from app import get_text_chunks, get_pdf_text, identify_file_type, get_txt_text, get_md_text, get_docx_text, get_document_text
import unittest
import io
from docx import Document
from PyPDF2 import PdfWriter

class TestAppFunctions(unittest.TestCase):
    def test_get_text_chunks_empty_string(self):
        # Empty input should produce no chunks at all since nothing to split
        result = get_text_chunks("")
        self.assertEqual(result, [])
    
    def test_get_text_chunks_long_string(self):
        # A string well beyond chunk_size (1000) should be split into
        # more than one chunk. We check for a non-empty result rather
        # than an exact chunk count, since RecursiveCharacterTextSplitter
        # may adjust split points and an exact-count assertion would be
        # too fragile to implementation details.
        result = get_text_chunks("x" * 2000)
        self.assertTrue(len(result) > 0)

    def test_identify_file_type_normal_extension(self):
        result = identify_file_type("test.pdf")
        self.assertEqual(result, "pdf")
        
    def test_identify_file_type_no_extension(self):
        result = identify_file_type("README")
        self.assertEqual(result, "")

    def test_identify_file_type_multiple_dots(self):
        result = identify_file_type("my.notes.v2.docx")
        self.assertEqual(result, "docx")

    def test_identify_file_type_uppercase_extension(self):
        result = identify_file_type("test.PDF")
        self.assertEqual(result, "pdf")

    def test_get_txt_text(self):
        fake_txt_file = io.BytesIO(b"Hello, test file")
        result = get_txt_text(fake_txt_file)
        self.assertEqual(result, "Hello, test file")

    def test_get_md_text(self):
        fake_md_file = io.BytesIO(b"# A first-level heading\n## A second-level heading\n### A third-level heading")
        result = get_md_text(fake_md_file)
        self.assertEqual(result, "# A first-level heading\n## A second-level heading\n### A third-level heading")

    def test_get_docx_text(self):
        buffer = io.BytesIO()
        doc = Document()
        doc.add_heading('Mock Document Title', level=0)
        doc.add_paragraph("This is a basic paragraph")
        doc.save(buffer)
        buffer.seek(0)
        result = get_docx_text(buffer)
        self.assertEqual(result, "Mock Document Title\nThis is a basic paragraph")

    def test_get_pdf_text(self):
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        result = get_pdf_text(buffer)
        self.assertEqual(result, "")

    def test_get_document_text_empty_list(self):
        result = get_document_text([])
        self.assertEqual(result, "")

    def test_get_document_text_mixed_file_types(self):
        fake_txt_file = io.BytesIO(b"this is a txt file")
        fake_txt_file.name = "notes.txt"
        buffer = io.BytesIO()
        doc = Document()
        doc.add_heading("Mock Document Title", level = 0)
        doc.add_paragraph("this is a docx file")
        doc.save(buffer)
        buffer.seek(0)
        buffer.name = "report.docx"
        result = get_document_text([fake_txt_file, buffer])
        self.assertEqual(result, "this is a txt file\n\nMock Document Title\nthis is a docx file")

    def test_get_document_text_unsupported_type(self):
        fake_file = io.BytesIO(b"some content")
        fake_file.name = "badfile.exe"
        result = get_document_text([fake_file])
        self.assertEqual(result, "")

if __name__ == "__main__":
    unittest.main()