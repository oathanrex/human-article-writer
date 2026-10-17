# Honesty and claims

A casual first-person voice makes invented detail very easy to write and very easy to get caught on. This file sets the line between "sounds like a person" and "made something up".

## Contents
- Honest-general mode (no real notes)
- Using real notes
- Claims about the user's own tool
- Claims about other apps and companies
- Sensitive topics
- Images and examples

## Honest-general mode (no real notes)

Use this whenever the user gave no notes, or the notes don't cover a section.

Allowed:
- General opinions ("I think slow disk I/O is the part people overlook").
- Common-knowledge explanations (why caching reduces rebuild times, how DNS resolution works).
- Practical advice stated as advice ("try setting memory limits before debugging").
- Numbers that come from the outline, from the topic itself (a 512 MB memory limit), or that are clearly labelled as a starting point ("start around 80 and adjust").

Not allowed:
- "I tried this last week", "I tested 5 apps", "in my testing", "it took me 40 seconds", or any claimed first-hand event.
- Invented before/after results, file sizes, timings, dates, user counts, or percentages.
- Invented stories about colleagues, clients, or the author's job.

The opening review in this mode is a general opinion, for example "Slow test suites are a quiet productivity killer. Most of the lag usually traces back to two or three unoptimized database queries or external network calls." It should not say the author did anything.

The checker's `--no-notes` flag treats claimed-experience phrases as FIX items.

## Using real notes

When notes exist, use them generously, because specific details are what make an article worth reading. Keep the user's numbers exactly as given. Do not round them, improve them, or add a second result they didn't mention. If the notes say a tool annoyed them in a specific way, say that, in plain words. Notes on one topic do not license claims on another; if a section has no notes behind it, fall back to honest-general mode for that section.

## Claims about the user's own tool

Write only what the user has stated or verified: the steps, supported formats, limits, price, whether a watermark or sign-up exists. Phrases like "files never leave your device", "nothing is uploaded", "no data is stored", and "completely private" are factual claims about how software works. Write them only when the user's tool facts say they are verified. Otherwise write a hedge that stays honest, such as "check the tool's privacy page to see whether it processes files in the browser or sends them to a server."

Mention the tool once or twice where it fits. Don't oversell: no "best tool ever", no invented comparisons with competitors, no superlatives without a basis.

## Claims about other apps and companies

Don't state specific facts about named apps (what they collect, what they charge, their watermarks, their security) unless the user supplied verified facts. If the user wants a comparison, ask for the facts once, or write generically ("some apps ask you to sign up or upload files to a server, so read the policy before using one"). Untrue specific claims about a named company can be wrong and damaging.

## Sensitive topics

For financial documents, ID cards, health records, legal papers, and similar, keep advice general and practical, suggest checking the official source or portal, and don't promise outcomes ("this will get your claim approved"). Never claim a method is guaranteed or risk-free.

## Images and examples

Never describe before/after results that were not provided. Don't write "as you can see in the image" unless the user said they will add one. Mention in the "before you publish" note that the user's own screenshots and before/after pictures are the most valuable thing to add, and let them place the images.
