# Contributing to Human Article Writer

Thanks for considering contributing! Here's how you can help.

## Ways to Contribute

### Report Issues
- Found a phrase the checker should catch? Open an issue with the phrase and why it sounds AI-generated.
- Found a false positive in the checker? Share the sentence that got flagged incorrectly.

### Add Language Support
The skill includes Tier-1 curated packs for 34 major languages and dynamically discovers any other language via its Tier-2 universal extensible architecture. To add or refine a language:

1. Create `references/banned-phrases-LANG.txt` following the format in `banned-phrases.txt`
2. (Optional) Create `references/voice-guide-LANG.md` or consult `references/multilingual-guide.md`
3. Add language-specific opinion and experience patterns in `scripts/check_article.py`
4. Optionally add or update an example in `examples/` when it demonstrates a useful new script, language-family adaptation, or checker behavior. Examples are representative, not a requirement for every supported language.
5. Test it with `python scripts/check_article.py examples/your-article.md --lang LANG`
6. Run the test suite: `python -m unittest discover tests`
7. Open a PR

### Improve the Checker
The checker in `scripts/check_article.py` catches mechanical patterns. If you find a new AI writing pattern:

1. Add a regex pattern with a clear comment explaining why it's a tell
2. Add test cases to `tests/test_checker.py`
3. Verify that all tests pass: `python -m unittest discover tests`
4. Make sure existing examples still pass cleanly with zero warnings

### Add Example Articles
Good examples help the AI write better. Requirements:
- Must pass the checker with no FIX items
- Must follow the voice guide
- Include a comment at the top noting whether it's with-notes or without-notes mode

## Pull Request Process

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/add-spanish-support`)
3. Make your changes
4. Run the checker on all examples to make sure nothing breaks
5. Open a PR with a clear description

## Code Style
- Python: Follow PEP 8
- Markdown: Use the same heading structure as existing files
- Keep things simple and readable

## Questions?
Open an issue. We'll respond as soon as we can.
