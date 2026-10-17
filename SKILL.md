---
name: human-article-writer
description: Write, rewrite, expand, outline, or humanize blog articles, SEO articles, how-to guides, and technical prose in an authentic conversational voice that eliminates AI tells and never invents fake experience. Answers to /human-article-writer or /humanizer. Incorporates Wikipedia's 26 Signs of AI Writing with tiered multi-language support (34 curated native language packs + universal extensible architecture for 100+ additional languages).
---

# Human Article Writer

This skill serves two complementary workflows:
1. **Full Article Generation**: Turns a topic, an outline, and optional user test notes into an authentic, human-sounding article that passes mechanical style checks, stays honest about real experience, and includes complete SEO framing.
2. **Text & File Humanizer (`/humanizer`)**: Rewrites existing AI-sounding drafts or files to remove the 26 signs of AI writing while preserving exact facts, quotes, code blocks, and information.

## Talking with the user

Reply in the language the user writes in. If the user writes in Spanish, answer in Spanish. If English, answer in English. If French, German, Japanese, or any other language, match their language. Keep chat replies concise. Ask at most one question at a time, and never block on a missing input when a sensible default exists.

## Tiered Multi-Language Support

The skill is built on a two-tier localization architecture:

- **Tier 1 (34 Curated Native Language Packs)**: Out-of-the-box native cliché lists, opinion markers, and experience detectors for `ar`, `bn`, `cs`, `da`, `de`, `el`, `en`, `es`, `fa`, `fi`, `fr`, `he`, `hi`, `hu`, `id`, `it`, `ja`, `ko`, `ms`, `nl`, `no`, `pl`, `pt`, `ro`, `ru`, `sv`, `sw`, `th`, `tl`, `tr`, `uk`, `ur`, `vi`, `zh` in `references/banned-phrases-<lang>.txt`.
- **Tier 2 (Universal Extensible Architecture for 100+ Additional Languages)**: Run `python scripts/check_article.py draft.md --lang <any_iso_code>`. Structural checks (word counts, sentence cadence, section length symmetry variance, code-fence isolation, burstiness spread, honesty checks) apply universally without false positives. Custom banned phrase files dropped in `references/banned-phrases-<lang>.txt` are auto-discovered dynamically.
- **Multilingual Writing Guide**: Read `references/multilingual-guide.md` for cross-language human writing principles, cultural adaptations, and a representative showcase across selected language families and scripts.
- **Core Voice Guide**: `references/voice-guide.md` details sentence rhythm, tone, and the **26 Signs of AI Writing**.

## Workflow

### 1. Collect the inputs

Look for these in the message, in `assets/site-profile.md`, and in earlier turns:

- **Topic or title**
- **Outline** (if missing, draft 5 to 7 plain sections using `references/article-types.md`, state the assumption in one line, and proceed)
- **Real notes**: tools used, results, numbers, likes, dislikes, mistakes. Use `assets/notes-template.md` if the user wants a form to fill in.
- **Tool facts**: what the user's own tool really does (formats, limits, whether processing happens in the browser or locally, price, watermark). Only verified facts get written as facts.
- **Primary keyword** (one per article), **length** (content-driven adaptive length matching the natural depth of the topic, or specific target if requested by user), **language** (default English or user's target language)

If the notes are empty, switch to honest-general mode: read `references/honesty-and-claims.md` and follow it. Do not ask the user to fill in notes before writing; write the honest version and remind them afterwards that real details are what make it stand out.

**Edge cases:**
- **Long articles (1500+ words):** Use 7 to 9 H2 sections. Keep sections varied in length. More words come from deeper practical detail, not filler.
- **Multiple tools:** If the user mentions multiple tools, handle each tool the same way as the primary tool: only verified facts, no invented comparisons.
- **Sensitive topics (medical, legal, financial):** Follow `references/honesty-and-claims.md` strictly. Keep advice general, suggest official sources, and never promise outcomes.

### 2. Shape the outline

Convert outline items to plain H2 headings. Drop conclusion, summary, "final recommendation", FAQ, and comparison-table items from the article body. A wrap-up paragraph is one of the strongest signals of generated text, and tables and Q&A blocks fight the plain-paragraph format. Make the last section an ordinary topic section so the article ends naturally. If the user wants an FAQ or a table, produce it separately (see `references/seo-extras.md`).

### 3. Write the draft

Read the voice guide for the target language first:
- English: `references/voice-guide.md`
- Any other language: `references/multilingual-guide.md` and the relevant `references/banned-phrases-<lang>.txt`

Core format, unless the user overrides it:

- Open with a 1 to 2 sentence first-person review before the first H2, no heading on it. With real notes it can mention a specific thing the user liked or disliked. Without notes it must be a general opinion, never a claimed experience.
- H2 headings for the outline sections, kept plain. Plain paragraphs only: no bullets, bold, numbered lists, or tables. Steps go in prose ("First... Then... After that...").
- A small personal comment or opinion in most sections, not all of them.
- Mention the user's tool once or twice where it fits, not in every section.

### 4. Run the checker

Save the draft as markdown and run:

```bash
# English article
python scripts/check_article.py draft.md --target 900 --tool "ToolName"

# Multi-language articles (es, fr, de, pt, it, etc.)
python scripts/check_article.py draft.md --target 900 --tool "ToolName" --lang es
python scripts/check_article.py draft.md --target 900 --tool "ToolName" --lang fr
python scripts/check_article.py draft.md --target 900 --tool "ToolName" --lang de

# Without real notes (strict mode)
python scripts/check_article.py draft.md --target 900 --tool "ToolName" --no-notes

# JSON output for integrations
python scripts/check_article.py draft.md --target 900 --json
```

Add `--no-notes` when the user gave no real notes; it turns invented-experience phrases into hard failures. The script prints FIX items (must change) and CHECK items (look and decide). Fix every FIX item, judge each CHECK item, and re-run, up to 3 rounds.

The checker catches: banned phrases, em dashes, list formatting, question openers, short punchy section endings, "not X but Y" patterns, uncontracted phrases, repeated sentence openers, length, risky absolute claims, section length variance, heading quality, passive voice ratio, opinion variety, and transition/announcing phrases.

It cannot judge whether the text is good, so finish with the self-review pass at the end of the voice guide.

### 5. Deliver

Show the article in chat by default so the user can read it straight away. If the user asks for a file, or asks for several articles, save each as a `.md` file and share it.

After the article, add a short "before you publish" note, 4 lines at most, separated from the article by a rule. Cover only what applies: which real details the user should add in their own words, which claims need verifying, where their own screenshots or before/after images go, and which internal links to add. Do not repeat the style rules back to the user.

### 6. Follow-ups

- **"Make it rougher / still sounds like AI"**: rewrite the full article. Cut anything polished or repeated, avoid balanced sentence pairs, keep the same facts, keep headings exactly as they are, add no new claims or numbers. Give the full article only.
- **"Too short"**: expand to the target length in the same tone, same headings, no new claims or numbers. Add length through practical detail and plain explanation, not filler.
- **Rewrite of the user's own draft**: keep their facts and personal details untouched, and change rhythm and wording only.

Run the checker again after any rewrite.

## Batches and site-level work

When asked for several articles, write them one at a time and vary section shapes, openings, and opinion phrasing between them so the site does not look templated. Before starting, compare each article's primary keyword against the other articles in `assets/site-profile.md`. If two would compete for the same search intent, say so and suggest a different angle or merging them. Word count alone does not fix thin content; original screenshots, real numbers, and specific observations do, so say that plainly when it matters.

## Optional extras on request

FAQ block, meta title and description, slug, image alt text, internal-link suggestions, comparison table (as separate HTML or markdown), social snippet. All are in `references/seo-extras.md`.

## Reference files

- `references/voice-guide.md`: Core voice, style rules, generated-text patterns, self-review pass
- `references/multilingual-guide.md`: Two-tier multilingual architecture guide and representative showcase across selected language families
- `references/banned-phrases.txt`: English hard-banned and soft-avoid word lists (read by the checker)
- `references/banned-phrases-es.txt`: Spanish hard-banned and soft-avoid word lists
- `references/banned-phrases-fr.txt`: French hard-banned and soft-avoid word lists
- `references/banned-phrases-de.txt`: German hard-banned and soft-avoid word lists
- `references/banned-phrases-pt.txt`: Portuguese hard-banned and soft-avoid word lists
- `references/banned-phrases-it.txt`: Italian hard-banned and soft-avoid word lists
- `references/honesty-and-claims.md`: no-invented-experience rules, tool and competitor claims, sensitive topics
- `references/article-types.md`: outline patterns for how-to, problem explainer, privacy, roundup, and utility articles
- `references/seo-extras.md`: FAQ, meta tags, internal links, alt text, keyword overlap
- `assets/site-profile.md`: the user's site, tools, audience, and article queue (edit once, reused every time)
- `assets/site-profile-template.md`: blank template for new users (copy to site-profile.md and fill in)
- `assets/notes-template.md`: fill-in form for real notes
- `scripts/check_article.py`: the style and claims checker (run with `--help` for all options)

The Spanish and Hindi articles in `examples/` are representative localization samples across different scripts. They illustrate the shared workflow and do not limit or prioritize language support; consult the language-pack list above for supported languages.

## Example articles

- `examples/with-notes-how-to.md`: technical tutorial written with real user notes (Mode 1: with-notes)
- `examples/without-notes-general.md`: article in honest-general mode, opinions only, zero fake claims (Mode 2: without-notes)
