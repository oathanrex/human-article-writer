# human-article-writer

An AI writing skill and CLI linter that produces blog posts and technical guides in an authentic, conversational voice. It eliminates robotic AI phrasing, enforces sentence rhythm, and blocks fabricated experience claims across 34 built-in languages and any Google Translate language code.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Why this exists

Most AI-generated articles sound identical. They open with throat-clearing clichés (*"In today's fast-paced world"*), overuse em dashes, balance every point into neat lists of three, and wrap up with a redundant "Conclusion" section. Worse, when asked to write reviews or tutorials, language models routinely invent fake benchmarks, phantom test runs, and unverifiable privacy claims.

Readers spot the formula immediately. Search engines discount repetitive, unoriginal text.

This repository gives AI coding assistants (Antigravity, Claude, ChatGPT, Cursor) a rigorous framework to write like an experienced practitioner sharing practical notes with a peer. It pairs style rules with an automated Python linter that catches AI patterns before anything gets published.

---

## What makes it different

1. **Honesty-first architecture**: When you provide real testing notes, the skill integrates your exact numbers and observations. When you do not provide notes, it shifts into honest-general mode and forbids claiming first-hand experience.
2. **Mechanical verification**: A zero-dependency Python script (`check_article.py`) verifies drafts against 30+ linguistic markers, sentence length variance, and structural constraints.
3. **Universal multilingual engine**: Includes native banned-phrase lists and opinion patterns for 34 global languages, plus language-agnostic structural linting for all 133+ Google Translate languages.
4. **No promotional fluff**: Prohibits em dashes, boldface emphasis spam, intrusive comparison tables in article bodies, and artificial summary sections.

---

## Quick example

### Standard AI output (typical prompt)
> *"In today's fast-paced DevOps environment, container build performance is crucial for seamless developer velocity. In this section, let us explore Docker layer caching. Furthermore, it is important to remember that BuildKit revolutionizes workflow efficiency. In conclusion..."*

### Output with human-article-writer
> *"Waiting six minutes for a one-line code change to build inside a container gets old fast. Most of that time usually goes to cache misses on dependencies that did not even change. Once you reorder the Dockerfile instructions to keep package installs above source files, build times drop under thirty seconds on local machines."*

---

## Project structure

```
human-article-writer/
├── SKILL.md                          # Core agent skill instructions and workflow
├── README.md                         # Project documentation
├── LICENSE                           # MIT License
├── CONTRIBUTING.md                   # Contribution guide
├── CHANGELOG.md                      # Release notes
│
├── references/                       # Style standards and linguistic datasets
│   ├── voice-guide.md                # Sentence cadence, rhythm, and tone
│   ├── multilingual-guide.md         # Cross-language human writing guide
│   ├── honesty-and-claims.md         # First-hand experience verification rules
│   ├── article-types.md              # Structural outlines for 5 common article types
│   ├── seo-extras.md                 # FAQs, meta tags, and internal link specs
│   └── banned-phrases*.txt           # Banned phrase packs for 34 languages
│
├── assets/                           # Project templates
│   ├── site-profile.md               # Example profile for technical developer tools
│   ├── site-profile-template.md      # Blank profile template for any niche
│   └── notes-template.md             # Scratchpad for real testing data
│
├── scripts/                          # Automated linting tools
│   └── check_article.py              # Zero-dependency markdown linter
│
└── examples/                         # Verified reference articles
    ├── with-notes-how-to.md          # Mode 1: Technical tutorial with real test data
    └── without-notes-general.md      # Mode 2: General overview with zero fake claims
```

---

## Getting started

### 1. Install the skill
Copy the `human-article-writer/` folder into your agent skills directory (for example, `.gemini/antigravity-ide/builtin/skills/` or your project `.agents/skills/`).

### 2. Configure your site profile (optional)
Fill in `assets/site-profile.md` with your site name, domain, and tool specifics. When defined, the skill automatically aligns with your technical domain.

### 3. Generate an article
Give your agent a topic and optional test notes:

```markdown
TOPIC: Speeding up local Docker builds
OUTLINE:
- Why builds slow down
- Cache invalidation gotchas
- Practical Dockerfile fixes
NOTES:
- Tested with BuildKit on Ubuntu 24.04
- Reordering COPY commands cut build time from 2m 40s to 18s
```

The agent writes the draft, executes `scripts/check_article.py`, resolves flagged patterns, and presents the clean article.

---

## Running the linter manually

The verification script requires Python 3.7+ and has zero third-party dependencies:

```bash
# Standard check with a 900-word target and tool mention cap
python scripts/check_article.py draft.md --target 900 --tool "MyTool"

# Strict mode: fails if any first-hand experience claims lack real notes
python scripts/check_article.py draft.md --no-notes --strict

# Check non-English articles (built-in support for 34 languages)
python scripts/check_article.py draft.md --lang es
python scripts/check_article.py draft.md --lang de
python scripts/check_article.py draft.md --lang ja

# Machine-readable output for CI/CD pipelines
python scripts/check_article.py draft.md --json
```

### CLI options

| Flag | Default | Description |
|---|---|---|
| `--target INT` | `900` | Target word count |
| `--tolerance FLOAT` | `0.15` | Acceptable word count variance (±15%) |
| `--tool STR` | `None` | Product name to check against self-promotion frequency |
| `--max-tool INT` | `3` | Maximum allowed tool mentions across the article |
| `--no-notes` | `False` | Converts claimed experience phrases from informational checks to hard failures |
| `--lang CODE` | `en` | ISO 639-1 language code (e.g. `es`, `fr`, `de`, `hi`, `id`, `ja`) |
| `--strict` | `False` | Returns exit code 1 on soft warnings as well as hard errors |
| `--json` | `False` | Outputs results as structured JSON |

---

## Linter checks

The checker classifies findings into three tiers:

- **FIX (Hard Failures)**:
  - Banned AI vocabulary and throat-clearing intros
  - Em dashes (`—`) and spaced hyphens (` -- `)
  - Bulleted or numbered lists inside article prose
  - Unnecessary boldface emphasis
  - Markdown tables inside the body text
  - Question-based opening sentences (*"Have you ever wondered...?"*)
  - Redundant conclusion sections (*"In summary"*, *"Final thoughts"*, *"Fazit"*, *"Kesimpulan"*)
  - One-line dramatic closers (*"Let that sink in"*, *"Read that again"*, *"That is the real win"*)
  - Experience claims made without input notes (in `--no-notes` mode)

- **CHECK (Quality Warnings)**:
  - Corporate filler words (*"leverage"*, *"utilize"*, *"comprehensive"*)
  - Absolute privacy or security guarantees (*"100% safe"*, *"zero risk"*)
  - Sentence length monotony (average sentence length > 17 words or < 25% short sentences)
  - Shallow -ing participle riders (*", ensuring seamless workflows"*, *", highlighting the importance"*)
  - Vague connection copulas (*"serves as a"*, *"acts as a"*, *"stands as a testament"*)
  - Arguing with phantom objections (*"I'm not saying"*, *"Don't get me wrong"*, *"A tempting approach would be"*)
  - Document meta-talk (*"In this article we explore"*, *"This section discusses"*)
  - Section heading echoed in opening sentence
  - Robotic transition announcements (*"Let us now discuss"*, *"Moving on to"*)
  - Clickbait heading phrasing
  - Symmetrical section word counts (uniform length across sections)
  - Unvarying opinion markers (repeating the same opinion prefix repeatedly)

- **INFO (Context Verifications)**:
  - Inventory of specific numbers and metrics for author verification against original testing logs

---

## Supported languages

The engine includes out-of-the-box banned phrase lists, opinion dictionaries, and experience claim detectors for **34 languages**:

`ar`, `bn`, `cs`, `da`, `de`, `el`, `en`, `es`, `fa`, `fi`, `fr`, `he`, `hi`, `hu`, `id`, `it`, `ja`, `ko`, `ms`, `nl`, `no`, `pl`, `pt`, `ro`, `ru`, `sv`, `sw`, `th`, `tl`, `tr`, `uk`, `ur`, `vi`, `zh`.

### Other Google Translate languages (133+)
To use any other language code, pass `--lang <code>`. Universal checks (cadence, structural balance, code fence safety, heading rules, and honesty bounds) apply automatically. You can add localized banned phrases by dropping a file named `references/banned-phrases-<code\>.txt`.

---

## Two operating modes

The repository includes tested reference articles demonstrating both operating modes:

- [examples/with-notes-how-to.md](examples/with-notes-how-to.md): Mode 1 (Real Notes). Shows how authentic benchmark numbers, setup quirks, and concrete trade-offs are presented without corporate marketing language.
- [examples/without-notes-general.md](examples/without-notes-general.md): Mode 2 (Honest General). Demonstrates how to explain concepts and architectural patterns thoroughly when the author has not conducted personal hands-on tests, avoiding fabricated personal anecdotes.

---

## Contributing

Contributions of new language phrase packs, regex refinements, and additional edge-case tests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting pull requests.

## License

Released under the [MIT License](LICENSE).
