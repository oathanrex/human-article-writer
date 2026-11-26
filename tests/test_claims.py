#!/usr/bin/env python3
"""Tests for scripts/check_claims.py - the provenance gate.

The rule under test is the whole product: a number may only come from a source the
writer actually read. A book summary, a newsletter and an AI notebook are all fine for
framing and all refused for numbers.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_claims as cc  # noqa: E402

HEADER = ("| id | claim | value | source | type | verified |\n"
          "|----|-------|-------|--------|------|----------|\n")
TODAY = date.today().isoformat()

SINGLE_ARTICLE = """# Draft

## A section

The study found that editors raised scores by 0.6 SD.
"""

CLEAN_ARTICLE = """# Draft

## A section

The study found that editors raised scores by 0.6 SD and acceptance by 8.4 pp.
"""


def claims_file(rows):
    with tempfile.NamedTemporaryFile("w", suffix=".claims.md", delete=False) as f:
        f.write("# Claims\n\n" + HEADER + rows)
        return f.name


def article_file(text=CLEAN_ARTICLE):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
        return f.name


class TestRules(unittest.TestCase):
    def run_check(self, rows, article=CLEAN_ARTICLE):
        stats, findings = cc.check(article, "# Claims\n\n" + HEADER + rows)
        fails = [f for f in findings if f["level"] == cc.FAIL]
        warns = [f for f in findings if f["level"] == cc.WARN]
        return stats, fails, warns

    def test_primary_with_doi_passes(self):
        rows = (f"| C1 | editors raised scores | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n"
                f"| C2 | acceptance rose | 8.4 pp | https://doi.org/10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n")
        stats, fails, _ = self.run_check(rows)
        self.assertEqual(fails, [], fails)
        self.assertEqual(stats["covered"], 2)

    def test_primary_without_doi_or_url_fails(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | I remember reading it | primary | {TODAY} |\n"
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any("DOI or URL" in f["message"] for f in fails), fails)

    def test_number_from_a_book_summary_fails(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | notebook summary of Pinker | book-summary | {TODAY} |\n"
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any("book-summary" in f["message"] for f in fails), fails)

    def test_number_from_a_secondary_source_fails(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | a newsletter | secondary | {TODAY} |\n"
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any("secondary" in f["message"] for f in fails), fails)

    def test_secondary_without_a_number_is_only_a_warning(self):
        rows = f"| C1 | the curse of knowledge is real | | a book about writing | secondary | {TODAY} |\n"
        _, fails, warns = self.run_check(rows, article="# D\n\n## S\n\nExperts forget what it is like not to know.\n")
        self.assertEqual(fails, [], fails)
        self.assertEqual(len(warns), 1)

    def test_no_source_always_fails(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | | none | {TODAY} |\n"
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any(o["where"] == "C1" and "no source" in o["message"] for o in fails), fails)

    def test_own_needs_a_file_that_exists(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "run.txt")
            rows_missing = f"| C1 | it ran fast | 0.09 seconds | {path} | own | {TODAY} |\n"
            _, fails, _ = self.run_check(rows_missing)
            self.assertTrue(any("does not exist" in f["message"] for f in fails), fails)

            pathlib.Path(path).write_text("elapsed_s 0.09\n")
            rows_ok = f"| C1 | it ran fast | 0.09 seconds | {path} | own | {TODAY} |\n"
            _, fails2, _ = self.run_check(rows_ok, article="# D\n\n## S\n\nIt ran in 0.09 seconds.\n")
            self.assertEqual(fails2, [], fails2)

    def test_verified_must_be_a_past_or_today_date(self):
        for bad in ("", "yesterday", (date.today() + timedelta(days=3)).isoformat()):
            rows = f"| C1 | editors raised scores | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {bad} |\n"
            _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
            self.assertTrue(any("verified" in f["message"] for f in fails), (bad, fails))

    def test_duplicate_ids_fail(self):
        rows = (f"| C1 | a | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n"
                f"| C1 | b | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n")
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any("duplicate id" in f["message"] for f in fails), fails)

    def test_number_in_the_draft_with_no_row_fails(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n"
        article = SINGLE_ARTICLE + "\nIt also cut time by 37%.\n"
        _, fails, _ = self.run_check(rows, article=article)
        self.assertTrue(any("has no row" in f["message"] and "37%" in f["message"] for f in fails), fails)

    def test_numbers_inside_code_fences_are_ignored(self):
        rows = f"| C1 | editors raised scores | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n"
        article = SINGLE_ARTICLE + "\n```bash\nsleep 300\n```\n"
        _, fails, _ = self.run_check(rows, article=article)
        self.assertEqual(fails, [], fails)

    def test_same_number_different_unit_is_not_a_match(self):
        rows = f"| C1 | the sample size | 0.6 people | doi:10.1016/j.jebo.2023.11.011 | primary | {TODAY} |\n"
        _, fails, _ = self.run_check(rows, article=SINGLE_ARTICLE)
        self.assertTrue(any("has no row" in f["message"] for f in fails), fails)


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_claims.py")] + list(args),
                              capture_output=True, text=True, cwd=str(ROOT))

    def test_bundled_clean_example_exits_zero(self):
        p = self.run_cli("--article", "examples/claims-demo.md",
                         "--claims", "examples/claims-demo.claims.md")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_bundled_failure_example_exits_one(self):
        p = self.run_cli("--article", "examples/failing-secondary-source.md",
                         "--claims", "examples/failing-secondary-source.claims.md")
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("book-summary source", p.stdout)

    def test_missing_file_exits_two(self):
        p = self.run_cli("--article", "does-not-exist.md", "--claims", "examples/claims-demo.claims.md")
        self.assertEqual(p.returncode, 2)

    def test_table_without_required_columns_exits_two(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as art:
            art.write("# D\n\n## S\n\nIt rose 5%.\n")
        with tempfile.NamedTemporaryFile("w", suffix=".claims.md", delete=False) as cl:
            cl.write("| id | claim |\n|---|---|\n| C1 | something |\n")
        p = self.run_cli("--article", art.name, "--claims", cl.name)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)

    def test_json_output_is_valid_and_carries_the_verdict(self):
        p = self.run_cli("--article", "examples/failing-secondary-source.md",
                         "--claims", "examples/failing-secondary-source.claims.md", "--json")
        self.assertEqual(p.returncode, 1)
        start = p.stdout.index("{")
        data = json.loads(p.stdout[start:])
        self.assertGreaterEqual(data["fails"], 3)
        self.assertEqual(data["stats"]["rows"], 7)

    def test_list_numbers_shows_what_the_checker_can_see(self):
        p = self.run_cli("--article", "examples/claims-demo.md",
                         "--claims", "examples/claims-demo.claims.md", "--list-numbers")
        self.assertEqual(p.returncode, 0)
        self.assertIn("8.4 percentage points", p.stdout)
        self.assertIn("0.09 seconds", p.stdout)


if __name__ == "__main__":
    unittest.main()
