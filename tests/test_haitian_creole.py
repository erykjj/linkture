import unittest
import sys
import os

# Add src to path so we can import linkture
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from linkture.linkture import Scriptures, _available_languages

class TestHaitianCreole(unittest.TestCase):

    def setUp(self):
        self.s = Scriptures(language='Haitian Creole')

    def test_initialization(self):
        """Test that the parser initializes with the new language."""
        self.assertIn('Haitian Creole', _available_languages)
        self.assertIsNotNone(self.s)

    def test_recognition_full_name(self):
        """Test recognition of full book names."""
        # Genesis
        res = self.s.list_scriptures("Li te li Jenèz 1:1 yè swa.")
        self.assertEqual(res, ['Jenèz 1:1'])
        
        # 1 John
        res = self.s.list_scriptures("1 Jan 1:9 se yon bèl vèsè.")
        self.assertEqual(res, ['1 Jan 1:9'])

    def test_recognition_abbreviations(self):
        """Test recognition of abbreviations."""
        # Standard: Jen.
        res = self.s.list_scriptures("Gade Jen. 1:1.")
        self.assertEqual(res, ['Jen. 1:1']) # Default output is input if rewrite is not forced, wait, list_scriptures might rewrite if _rewrite is set?
        # Actually list_scriptures uses _rewrite property.
        # By default _rewrite is False unless language != translate or form is specified.
        # So it should return exactly what was found if not rewritten.
        
        # Official: Jen
        res = self.s.list_scriptures("Jen 1:1")
        self.assertEqual(res, ['Jen 1:1'])

    def test_output_formats(self):
        """Test rewriting into different formats."""
        # Full (default if form='full')
        s_full = Scriptures(language='Haitian Creole', form='full')
        self.assertEqual(s_full.rewrite_scriptures("Jen. 1:1"), "Jenèz 1:1")
        
        # Standard
        s_std = Scriptures(language='Haitian Creole', form='standard')
        self.assertEqual(s_std.rewrite_scriptures("Jenèz 1:1"), "Jen. 1:1")
        
        # Official
        s_off = Scriptures(language='Haitian Creole', form='official')
        self.assertEqual(s_off.rewrite_scriptures("Jenèz 1:1"), "Jen 1:1")

    def test_translation_to_english(self):
        """Test translating Haitian Creole to English."""
        s_en = Scriptures(language='Haitian Creole', translate='English')
        res = s_en.rewrite_scriptures("Jenèz 1:1")
        self.assertEqual(res, "Genesis 1:1")
        
        res = s_en.rewrite_scriptures("1 Jan 1:1")
        # Normalize non-breaking spaces
        res = res.replace('\xa0', ' ')
        self.assertEqual(res, "1 John 1:1")

    def test_translation_from_english(self):
        """Test translating English to Haitian Creole."""
        s_ht = Scriptures(language='English', translate='Haitian Creole')
        res = s_ht.rewrite_scriptures("Genesis 1:1")
        self.assertEqual(res, "Jenèz 1:1")

    def test_complex_ranges(self):
        """Test complex ranges validation."""
        # Valid range
        self.assertEqual(self.s.list_scriptures("Sòm 23:1-4"), ['Sòm 23:1-4'])
        
        # Invalid range (verse out of bounds, depending on bible versification, but let's try a huge number)
        # Ps 119 has 176 verses. Ps 117 has 2.
        self.assertEqual(self.s.list_scriptures("Sòm 117:100"), []) 

    def test_bcv_encoding(self):
        """Test BCV encoding and decoding."""
        # Jenèz 1:1 -> Book 1, Chap 1, Verse 1 -> '01001001'
        # Returns a list of ranges. A single verse is start==end.
        code = self.s.code_scriptures("Jenèz 1:1")
        # Expected: [('01001001', '01001001')]
        self.assertEqual(code, [('01001001', '01001001')])
        
        # Decode back
        decoded = self.s.decode_scriptures(code)
        self.assertEqual(decoded[0], "Jenèz 1:1")

    def test_bcv_extended_coverage(self):
        """Test extended BCV edge cases to ensure full mapping correctness."""
        # 1. First Book: Genesis 1:1
        self.assertEqual(self.s.code_scriptures("Jenèz 1:1"), [('01001001', '01001001')])

        # 2. Last Book: Revelasyon 22:21 (Last verse of the Bible)
        # Check if 'Revelasyon' maps correctly to 66
        self.assertEqual(self.s.code_scriptures("Revelasyon 22:21"), [('66022021', '66022021')])

        # 3. Middle Book: Sòm 119:105
        self.assertEqual(self.s.code_scriptures("Sòm 119:105"), [('19119105', '19119105')])

        # 4. Invalid Chapter: Genesis 51 (Genesis has 50 chapters)
        # Should return empty list as it's invalid
        self.assertEqual(self.s.code_scriptures("Jenèz 51:1"), [])

        # 5. Invalid Verse: Genesis 1:32 (Genesis 1 has 31 verses)
        # Should return empty list
        self.assertEqual(self.s.code_scriptures("Jenèz 1:32"), [])

    def test_linking(self):
        """Test HTML linking."""
        res = self.s.link_scriptures("Li Jenèz 1:1 silvouple.")
        # Expect: Li <a href=...>Jenèz 1:1</a> silvouple.
        # The href format depends on implementation but usually it's just the tag wrapping the text.
        self.assertIn('<a href=', res)
        self.assertIn('>Jenèz 1:1</a>', res)

    def test_special_characters(self):
        """Test books with accents."""
        # Detewonòm (Deuteronomy)
        self.assertEqual(self.s.list_scriptures("Detewonòm 6:4"), ['Detewonòm 6:4'])
        # Job (Jòb)
        self.assertEqual(self.s.list_scriptures("Jòb 1:1"), ['Jòb 1:1'])

    def test_variations(self):
        """Test variations from the CSV."""
        # 1 Kwonik vs 1 Kwo. vs 1Kw
        books = ["1 Kwonik", "1 Kwo.", "1Kw"]
        for b in books:
            ref = f"{b} 1:1"
            self.assertEqual(self.s.list_scriptures(ref), [ref], f"Failed to recognize {b}")

if __name__ == '__main__':
    unittest.main()
