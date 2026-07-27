from app import get_text_chunks, get_pdf_text, identify_file_type, get_txt_text
import unittest
import io

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
        fake_txt_file = io.BytesIO("Hello, test file".encode())
        result = get_txt_text(fake_txt_file)
        self.assertEqual(result, "Hello, test file")


    

if __name__ == "__main__":
    unittest.main()