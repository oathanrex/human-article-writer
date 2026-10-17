# Changelog

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-10-17

### Added
- **Universal Multi-Language Support**: Extensible architecture supporting all 100+ languages from Google Translate and modern LLMs.
- **Native Language Packs**: Added built-in banned phrase and pattern packs for Spanish (`es`), French (`fr`), German (`de`), Portuguese (`pt`), and Italian (`it`).
- **Side-by-Side Multilingual Showcase**: Demonstrating anti-AI human cadence across English, Spanish, French, and German in `references/multilingual-guide.md`.

### Improved
- Checker: Added Portuguese and Italian opinion & experience patterns.
- Fully neutralized all regional and niche references across entire codebase.

## [2.1.0] - 2026-10-17

### Added
- **Dynamic Language Auto-Discovery**: Checker dynamically detects and loads language packs (`banned-phrases-<lang>.txt`) from the references directory.
- **Unicode-Aware Tokenization**: Full regex support for accented characters, umlauts, cedillas, Devanagari, and non-Latin scripts.
- **Universal Developer & Tech Examples**: Authentic, realistic software engineering guides (Docker build optimization, credential management).

### Improved
- Checker: Multilingual opinion & experience detection patterns for major world languages.
- Checker: Multilingual conclusion heading and transition phrase checks.
- References: Cleaned up niche references in `honesty-and-claims.md` and `seo-extras.md`.

### Fixed
- Fixed bug where `check_opinion_variety` was hardcoded to English opinions even when `--lang` was set to another language.
- Fixed `choices=["en", "hi"]` restriction in `check_article.py` to allow dynamic language codes.
- Fixed unused `import math` and moved `from collections import Counter` to module level.

## [2.0.0] - 2026-10-17

### Added
- **Multi-language support**: Multilingual banned phrases and checker support
- **Example articles**: Complete examples (with notes, without notes, multilingual)
- **Enhanced checker**: Section length variance, heading quality, passive voice, opinion variety, transition phrases
- **JSON output**: `--json` flag for programmatic integration
- **Blank site profile template**: `assets/site-profile-template.md` for any niche
- **Contributing guide**: `CONTRIBUTING.md`
- **MIT License**
- **Professional README** with installation, usage, and SEO keywords

## [1.0.0] - 2026-10-17

### Initial Release
- Core SKILL.md with 6-step workflow
- Voice guide with anti-AI-detection patterns
- Banned phrases list (hard + soft)
- Honesty and claims framework
- Article types reference (5 types)
- SEO extras reference
- Site profile with article queue
- Notes template
- Python checker script
