#!/usr/bin/env python3
"""
Comprehensive automated test suite for human-article-writer linter (check_article.py).
Zero external dependencies: uses Python standard library `unittest`.

Run:
    python -m unittest discover tests
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
CHECKER_PY = SCRIPTS_DIR / "check_article.py"

# Add scripts directory to path for direct imports
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import check_article


class TestCheckerUnit(unittest.TestCase):
    """Unit tests for internal parsing, tokenization, and linguistic checks."""

    def test_words_tokenization(self):
        sample = "Don't delay; let's verify café and Devanagari हिन्दी words."
        tokens = check_article.words(sample)
        self.assertIn("Don't", tokens)
        self.assertIn("let's", tokens)
        self.assertIn("café", tokens)
        self.assertIn("हिन्दी", tokens)

    def test_sentences_split(self):
        sample = "First short sentence. Second one goes here! Does Hindi danda work। Yes it does."
        sents = check_article.sentences(sample)
        self.assertEqual(len(sents), 4)

    def test_code_block_fence_ignored(self):
        lines = [
            "# Heading",
            "This is normal prose text.",
            "```python",
            "import os",
            "# In this article we will explore fake code comments",
            "def test():",
            "    pass",
            "```",
            "## Section 1",
            "More regular text here.",
        ]
        sections, h1_count, deep = check_article.parse(lines)
        self.assertEqual(h1_count, 1)
        self.assertEqual(len(deep), 0)
        # Verify code block lines were excluded from prose body
        all_body = " ".join(t for s in sections for _, t in s["body"])
        self.assertNotIn("import os", all_body)
        self.assertNotIn("explore fake code comments", all_body)
        self.assertIn("normal prose text", all_body)
        self.assertIn("More regular text here", all_body)

    def test_get_available_languages(self):
        langs = check_article.get_available_languages()
        self.assertIn("en", langs)
        self.assertIn("es", langs)
        self.assertIn("hi", langs)
        self.assertIn("fr", langs)
        self.assertIn("de", langs)
        self.assertGreaterEqual(len(langs), 34)

    def test_banned_phrases_loading(self):
        hard_en, soft_en = check_article.load_phrases("en")
        self.assertTrue(len(hard_en) > 0)
        self.assertIn("delve", hard_en)

        hard_es, soft_es = check_article.load_phrases("es")
        self.assertTrue(len(hard_es) > 0)
        self.assertIn("desentrañar", hard_es)

    def test_em_dash_detection(self):
        sample = "We were running fast — and then stopped."
        self.assertIn("—", sample)

    def test_list_of_three_regex(self):
        sample_en = "Speed, reliability, and security are essential."
        m_en = check_article.THREE_LIST.search(sample_en)
        self.assertIsNotNone(m_en)

        sample_es = "Rapidez, fiabilidad y seguridad son claves."
        m_es = check_article.THREE_LIST.search(sample_es)
        self.assertIsNotNone(m_es)

        sample_hi = "Gati, suraksha aur suvidha zaroori hai."
        m_hi = check_article.THREE_LIST.search(sample_hi)
        self.assertIsNotNone(m_hi)

    def test_verbose_fillers_regex(self):
        sample = "We avoided downtime due to the fact that servers scaled."
        m = check_article.VERBOSE_FILLERS.search(sample)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(0).lower(), "due to the fact that")

    def test_one_line_closers_regex(self):
        sample = "The deployment succeeded. Let that sink in."
        m = check_article.ONE_LINE_CLOSERS.search(sample)
        self.assertIsNotNone(m)

    def test_shallow_ing_riders_regex(self):
        sample = "We upgraded our proxies, ensuring zero packet drops."
        m = check_article.ING_RIDERS.search(sample)
        self.assertIsNotNone(m)

    def test_section_variance_check(self):
        # Identical section lengths should trigger variance warning
        uniform_sections = [
            {"heading": "Sec 1", "body": [(1, "word " * 100)]},
            {"heading": "Sec 2", "body": [(2, "word " * 102)]},
            {"heading": "Sec 3", "body": [(3, "word " * 101)]},
            {"heading": "Sec 4", "body": [(4, "word " * 100)]},
        ]
        issues = check_article.check_section_variance(uniform_sections)
        self.assertTrue(len(issues) > 0)
        self.assertIn("sections are very similar in length", issues[0])

        # Varied section lengths should pass cleanly
        varied_sections = [
            {"heading": "Sec 1", "body": [(1, "word " * 180)]},
            {"heading": "Sec 2", "body": [(2, "word " * 60)]},
            {"heading": "Sec 3", "body": [(3, "word " * 160)]},
            {"heading": "Sec 4", "body": [(4, "word " * 75)]},
        ]
        clean_issues = check_article.check_section_variance(varied_sections)
        self.assertEqual(len(clean_issues), 0)


class TestCheckerIntegration(unittest.TestCase):
    """End-to-end CLI execution tests via subprocess."""

    def run_checker(self, args):
        cmd = [sys.executable, str(CHECKER_PY)] + args
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        return res

    def test_bundled_examples_pass_clean(self):
        # Default 900 target without extra tolerance overrides
        res_with = self.run_checker(["examples/with-notes-how-to.md", "--tool", "DevPulse"])
        self.assertEqual(res_with.returncode, 0, f"with-notes-how-to failed: {res_with.stdout}")
        self.assertIn("Clean.", res_with.stdout)

        res_without = self.run_checker(["examples/without-notes-general.md", "--no-notes"])
        self.assertEqual(res_without.returncode, 0, f"without-notes-general failed: {res_without.stdout}")
        self.assertIn("Clean.", res_without.stdout)

    def test_json_output_mode(self):
        res = self.run_checker(["examples/without-notes-general.md", "--no-notes", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("stats", data)
        self.assertIn("fix", data)
        self.assertIn("check", data)
        self.assertEqual(len(data["fix"]), 0)
        self.assertEqual(len(data["check"]), 0)

    def test_banned_phrase_fails_with_exit_code_1(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write(
                "# Test Title\n\n"
                "Opening review paragraph introducing the topic.\n\n"
                "We delve deep into this crucial topic.\n\n"
                "## Section 1\n\n"
                "Content here.\n"
            )
            temp_path = tf.name

        try:
            res = self.run_checker([temp_path])
            self.assertEqual(res.returncode, 1)
            self.assertIn('banned phrase "delve"', res.stdout)
            self.assertIn('banned phrase "crucial"', res.stdout)
        finally:
            os.remove(temp_path)

    def test_no_notes_flag_flags_claimed_experience(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False, encoding="utf-8") as tf:
            tf.write(
                "# Test Title\n\n"
                "This is a proper introductory overview paragraph before sections.\n\n"
                "## Section 1\n\n"
                "When I tested this tool in production last week, the latency spiked.\n"
            )
            temp_path = tf.name

        try:
            # Without --no-notes, claimed experience is an INFO item (exit code 0 unless other errors)
            res_normal = self.run_checker([temp_path])
            self.assertEqual(res_normal.returncode, 0)
            self.assertIn("INFO", res_normal.stdout)
            self.assertIn("claimed first-hand experience", res_normal.stdout)

            # With --no-notes, claimed experience becomes a hard FIX error (exit code 1)
            res_strict = self.run_checker([temp_path, "--no-notes"])
            self.assertEqual(res_strict.returncode, 1)
            self.assertIn("FIX (must change)", res_strict.stdout)
            self.assertIn("no real notes were given", res_strict.stdout)
        finally:
            os.remove(temp_path)

    def test_missing_file_exit_code_2(self):
        res = self.run_checker(["non_existent_file_xyz_123.md"])
        self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()
