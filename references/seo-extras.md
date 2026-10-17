# SEO extras

Everything here is optional and produced only when asked, or offered in one line after an article. Each item is separate from the article body so the article keeps its plain-paragraph format.

## Contents
- What actually fixes thin content
- Keyword and overlap check
- FAQ block
- Meta title, description, slug
- Internal links
- Image alt text
- Comparison table
- Tool mention and CTA

## What actually fixes thin content

Word count is not the fix. Thin content is content with nothing original in it. What helps: the user's own screenshots, real before/after results, real numbers, specific mistakes they made, a clear angle that differs from the other pages on the site. When an article has no notes behind it, say so in the "before you publish" note and suggest 2 or 3 real observations to add by hand.

## Keyword and overlap check

One primary keyword per article, one angle. Compare against the article list in `assets/site-profile.md`. If two articles target the same intent (for example "debug docker memory", "docker out of memory", "reduce container ram"), flag it and suggest either a sharper angle for each or merging them. Use the keyword naturally in the title, the opening, and one or two headings. Don't repeat it for its own sake.

## FAQ block

Write separately, after the article. 3 to 5 questions that real people type. Answers are 2 to 3 plain sentences each, based only on facts in the article or the user's tool facts. Questions don't have to follow the "no question openers" rule, since the FAQ is not an article section. Offer markdown by default and FAQ schema JSON-LD if the user asks.

## Meta title, description, slug

- Title: up to about 60 characters, primary keyword near the front, no clickbait.
- Description: up to about 155 characters, says what the reader will be able to do, no invented claims.
- Slug: short, lowercase, hyphens, keyword only.

Offer 2 options for the title and 1 for the rest.

## Internal links

Suggest 2 to 4 per article, based on the article list in the site profile: other articles on related problems, and the tool page. Use descriptive anchor text ("how to configure docker resource limits"), not "click here". Give the exact sentence where each link would fit, so the user can paste it.

## Image alt text

Describe what the image shows in one plain sentence, with the keyword only when it truly fits. Write alt text only for images the user has described or provided.

## Comparison table

Produce as a separate markdown or HTML table, using only facts the user supplied. Mark unverified cells "check" rather than guessing. Don't put the table inside the article.

## Tool mention and CTA

Mention the tool once or twice, where it solves the exact problem being described. Because the article has no wrap-up paragraph, a call to action works best as a plain detail inside the last topic section ("I usually run the profiler directly from the CLI to catch the leak"), not as a closing pitch.
