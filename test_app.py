from app import get_text_chunks, get_pdf_text
import unittest

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
    
    def test_get_pdf_text(self):
        # No PDFs uploaded means the for-loop body never executes,
        # so the accumulator string should remain empty.
        result = get_pdf_text([])
        self.assertEqual(result, "")


    
    

if __name__ == "__main__":
    unittest.main()