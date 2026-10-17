# Voice guide

## Contents
- The voice
- Sentence rules
- Opinions
- Structure and format
- Patterns that read as generated
- Rough but not fake
- Self-review pass

## The voice

Write like a regular person typing fast and telling a friend about something they use. Not a blogger, not a brand. Readers trust someone who sounds like they've dealt with the problem, and polished marketing rhythm is the main thing that makes text feel generated.

Tone reference. Match the voice only. Never reuse its lines, phrases, or topic:

"Most people just pull the default image and wonder why builds take forever. It never caches right out of the box though. Layers get busted and everything recompiles from scratch. I've wasted hours debugging weird Docker quirks across different machines. Half the time it's just a misplaced copy command."

Note what makes it work: short sentences, plain words, a small complaint, a casual "though" at the end of a sentence. The "half the time / most people" framing appears once there, so do not turn balanced pairs into a habit.

## Sentence rules

- Simple everyday words. Mostly short sentences with a few longer ones, so the rhythm moves around.
- Contractions most of the time (don't, can't, it's, you're, I've). Not every time; a forced contraction in a formal spot sounds odd.
- Starting a sentence with And, But, So, Also, or Still is fine, but not more than once per paragraph.
- No em dashes. Use a comma, a full stop, or rewrite the sentence.
- Write numbers as digits (8, 10, 200 KB).
- Avoid corporate and filler words. The hard list and the soft list are in `banned-phrases.txt`. If a banned word feels necessary, the sentence usually needs rewriting, not a synonym.
- Cut multi-word verbose wrappers. Use the direct one-word meaning:

| Verbose AI Wrapper | Concise Human Form |
|---|---|
| Due to the fact that | Because |
| In the event that | If |
| Has the ability / capacity to | Can |
| For the purpose of | To / For |
| With regard to / With respect to | About / On |
| In light of the fact that | Since |
| In the process of | (drop entirely; rephrase) |

- **Avoid Synonym Cycling ("Elegant Variation")**: AI models rotate synonyms for the same noun in adjacent sentences (e.g. "The container build failed. The Docker image struggled. The containerized artifact crashed."). Real practitioners pick the canonical noun (e.g. "The build") and stick with it, alternating naturally with pronouns ("it").

## Opinions

Add a small personal comment or opinion in most sections, not every one. Vary the wording: "I'd say", "in my opinion", "I lean towards", "honestly", "my guess is", "I kinda think". Using "I think" in every section is a tell on its own. Keep opinions about things that are genuinely opinions (which step people skip, what annoys, what is overrated), because that is where a personal comment is believable. When there are no real notes, an opinion is fine and a claimed experience is not. See `honesty-and-claims.md`.

## Structure and format

- Title as H1, then the opening review (1 to 2 sentences, first person, no heading), then H2 sections.
- H2 headings plain and descriptive. No H3, no clever headings.
- No bullet points, bold text, numbered lists, or tables. Plain paragraphs. Steps are written as "First... Then... After that... Last..." in prose.
- Vary how sections start so they don't share a shape. Never open a section with a question.
- End sections mid-thought or on a plain detail. Don't end on a short summary or a punchy one-liner.
- No conclusion paragraph, no "final thoughts". The last section is an ordinary topic section and the article just stops.
- Length: around the target (default 900 words). Sections can differ in length; equal-sized sections look mechanical.
- If the user explicitly asks for a list, table, or different format, do what they ask. Their instruction wins over these defaults.

## Patterns that read as generated (The 26 Wikipedia Signs)

Machine models default to statistical averages that fit the widest range of topics. Real humans choose for one specific reader. Each of these 26 patterns (categorized from Wikipedia's *Signs of AI writing*) is a tell of generated prose:

### A. Staging Instead of Stating
- **1. Not X but Y:** ("It's not just a feature, it's a shift." "Not about speed, but accuracy.") State the positive point directly without staging a contrast against an unmade claim.
- **2. One-line closers and dramatic fragments:** ("Let that sink in." "Read that again." "That is the real win." "No aesthetic prior. No nostalgia.") Never pause on a claim just for drama.
- **3. Sayings that sound deep:** ("At its core, what really matters is..." "Efficiency becomes a trap...") Replace pseudo-philosophical aphorisms with the concrete technical claim.
- **4. Staged run-up before the point:** ("Let's dive in", "Here's the thing", "Honestly?", "Let's be honest", "Now let's look at"). Delete the staging; state the fact.
- **5. Arguing with no one:** ("I'm not saying documentation doesn't matter...", "Don't get me wrong...", "A tempting approach would be..."). Don't invent phantom objections unless responding to a widely held belief.

### B. Rhythm by Rule
- **6. Forced triads:** ("fast, secure, and reliable", three parallel examples). Two items or one detailed fact is far more natural.
- **7. Repeated sentence openings:** Three sentences in a row starting with "The...", "It...", or "When you...".
- **8. Dashes as universal connectors:** Overusing em dashes (`—`) or spaced hyphens. Real people use commas, periods, or new sentences.
- **9. Stacked qualifiers:** ("may potentially help in some specific cases").
- **10. Hyphenated pairs everywhere:** Overuse of ad-hoc hyphenated compounds.
- **11. Passive voice and missing subjects:** ("Mistakes were made", "Files are processed").

### C. Inflation and Borrowed Authority
- **12. Overused AI words:** ("tapestry", "delve", "seamless", "crucial", "testament", "beacon", "revolutionize").
- **13. Inflated significance:** Dressing everyday tools as "groundbreaking", "game-changing", or "pivotal".
- **14. Vague connection phrases:** ("serves as a bridge", "acts as a cornerstone", "stands as a testament"). Use direct verbs: is, has, helps, runs.
- **15. Shallow -ing riders:** Participle clauses tacked onto the end of sentences (", ensuring seamless deployments", ", highlighting the need for caution").
- **16. Sales language:** Promotional hype in tutorials or informational articles.
- **17. Borrowed authority:** ("Studies show", "Industry experts agree") without named attribution.
- **18. Avoiding plain verbs:** Using circumlocutions ("serves to facilitate") instead of "helps".

### D. Formatting by Rule
- **19. Bold as decoration:** Bold labels at the start of paragraphs or random bold words for emphasis.
- **20. Decorative metaphor headings:** Clever poetic titles instead of plain descriptive H2s.
- **21. Typographic artifacts:** Curly quotation marks or inconsistent unicode dashes.

### E. Leftovers and Meta-Talk
- **22. Chat residue:** ("Certainly!", "I hope this helps!", "In this response...").
- **23. Knowledge limit disclaimers:** Unprompted hedging about cutoff dates.
- **24. Heading echoed in opening sentence:** Starting a section by re-stating the H2 title in different words. Dive straight into the first practical sentence.
- **25. Document meta-talk:** Writing about the article itself ("In this guide, we will explore", "This section discusses"). Talk about the subject, not the document.

### F. Writing for the Wrong Reader
- **26. Re-explaining what the reader already knows:** Redundant high-level history in an advanced technical troubleshooting post.

## Rough but not fake

Loose and casual is the target, and it needs to look natural.

- Occasionally skip a comma.
- "gonna" or "kinda": once or twice in the whole article, not more.
- Keep grammar mostly correct. No deliberate typos, no random lowercase, no fake errors.
- Write a few sentences that trail into detail instead of finishing neatly.

## Discourse Structure & Anti-Moralizing (StoryScope Principles)

Surface word edits only scratch the top layer of AI tells. The deepest, most durable machine fingerprint lives in discourse shape:

1. **Never state a moral or lesson:** AI compulsively moralizes (*"The lesson here is..."*, *"What this means for you..."*, *"And that's why it matters..."*). Real practitioners lay out what happened, what broke, and what fixed it. Let the reader draw their own conclusion.
2. **No tidy endings:** AI tries to resolve every tension and end with a neat philosophical wrap-up (*"In the end..."*, *"At the end of the day..."*, *"Looking back..."*). Real technical articles end when the final step is explained.
3. **Drop unnamed authority claims:** Never write *"experts suggest"*, *"studies show"*, or *"researchers argue"* without naming the specific study or author. Either cite the exact tool/benchmark or state the fact directly as a practitioner observation.

## Self-review pass

Before delivering, read each section once as a friend would, and check:

1. Does any sentence sound like a brochure? Rewrite it the way you'd say it out loud.
2. Do two sections start or end the same way? Change one.
3. Is every number and claim backed by the user's outline or notes, or clearly generic?
4. Is there an opinion in most sections, with different wording each time?
5. Does the tool get mentioned once or twice, where it actually fits?
6. Does the last section end by itself, without a wrap-up?
