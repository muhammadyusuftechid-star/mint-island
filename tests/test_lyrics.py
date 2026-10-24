import unittest
from mint_island.modules.lyrics_module import LyricsEngine

class TestLyricsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LyricsEngine()

    def test_clean_youtube_title_standard(self):
        raw = "Queen - Bohemian Rhapsody (Official Video) [4K]"
        artist, title = self.engine.clean_youtube_title(raw)
        self.assertEqual(artist, "Queen")
        self.assertEqual(title, "Bohemian Rhapsody")

    def test_clean_youtube_title_unicode_dash(self):
        raw_en_dash = "YOASOBI – Idol (Official Music Video)"
        artist, title = self.engine.clean_youtube_title(raw_en_dash)
        self.assertEqual(artist, "YOASOBI")
        self.assertEqual(title, "Idol")

        raw_em_dash = "Eminem — Lose Yourself [HD]"
        artist, title = self.engine.clean_youtube_title(raw_em_dash)
        self.assertEqual(artist, "Eminem")
        self.assertEqual(title, "Lose Yourself")

    def test_clean_youtube_title_empty(self):
        artist, title = self.engine.clean_youtube_title("")
        self.assertEqual(artist, "")
        self.assertEqual(title, "")

    def test_parse_lrc(self):
        lrc = """
        [00:10.50]Line one
        [01:05.00]Line two
        [02:15.25]Line three
        """
        parsed = self.engine.parse_lrc(lrc)
        self.assertEqual(len(parsed), 3)
        self.assertAlmostEqual(parsed[0][0], 10.50)
        self.assertEqual(parsed[0][1], "Line one")
        self.assertAlmostEqual(parsed[1][0], 65.00)
        self.assertEqual(parsed[1][1], "Line two")
        self.assertAlmostEqual(parsed[2][0], 135.25)
        self.assertEqual(parsed[2][1], "Line three")

    def test_get_current_lyric_timing(self):
        self.engine.current_lyrics = [
            (10.0, "Intro finished"),
            (20.0, "First verse"),
            (30.0, "Chorus")
        ]
        # Before first lyric
        idx, curr, nxt = self.engine.get_current_lyric(5.0)
        self.assertEqual(idx, -1)
        self.assertEqual(curr, "...")
        self.assertEqual(nxt, "Intro finished")

        # At second lyric
        idx, curr, nxt = self.engine.get_current_lyric(25.0)
        self.assertEqual(idx, 1)
        self.assertEqual(curr, "First verse")
        self.assertEqual(nxt, "Chorus")

        # At last lyric
        idx, curr, nxt = self.engine.get_current_lyric(40.0)
        self.assertEqual(idx, 2)
        self.assertEqual(curr, "Chorus")
        self.assertEqual(nxt, "")

if __name__ == "__main__":
    unittest.main()
