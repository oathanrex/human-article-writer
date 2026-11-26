# Claims — where every number in an article came from

`check_article.py` asks whether a draft **reads** like a human wrote it.
`check_claims.py` asks the harder question: could a human have **written** it at all?

A style linter cannot tell the difference between a writer who read the paper and a writer who
read an AI notebook summary of a book about the paper. Both produce clean sentences. Only one of
them can answer a reader who asks "where does 8.4 percentage points come from?"

```bash
python3 scripts/check_claims.py --article draft.md --claims draft.claims.md
python3 scripts/check_claims.py --article draft.md --claims draft.claims.md --list-numbers
python3 scripts/check_claims.py --article draft.md --claims draft.claims.md --json
```

Exit codes: `0` no FAIL rows · `1` at least one FAIL · `2` bad usage or an unparseable claims file.

## The claims file

One markdown table beside the draft, one row per number or factual claim.

| id | claim | value | source | type | verified |
|----|-------|-------|--------|------|----------|
| C1 | Writing experts scored edited papers higher | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | 2026-11-26 |
| C2 | Economists were more likely to accept an edited paper | 8.4 pp | doi:10.1016/j.jebo.2023.11.011 | primary | 2026-11-26 |
| C3 | The checker runs in 0.09s on the bundled example | 0.09 seconds | examples/evidence/check-run.txt | own | 2026-11-26 |

| column | meaning |
|---|---|
| `id` | unique. Used in the output, so make it recognisable |
| `claim` | the sentence in your own words, not the source's |
| `value` | the number as it appears in the draft (`8.4 pp`, `37%`, `0.09 seconds`). Empty for a claim with no number |
| `source` | DOI, URL, or a repo path. Depends on `type` |
| `type` | `own` · `primary` · `secondary` · `book-summary` · `none` |
| `verified` | the date **you** checked it, `YYYY-MM-DD`. Not the publication date |

## The five types, and what each one may support

| type | what it means | may support a number | what `source` must be |
|---|---|---|---|
| `own` | you measured it: a run, a screenshot, a spreadsheet, a log | **yes** | a path inside this repo that must exist |
| `primary` | you read the paper, standard or dataset yourself | **yes** | a DOI or URL |
| `secondary` | someone else read it for you: a blog, a newsletter, a colleague | **no** | where it came from |
| `book-summary` | AI notes on a book, a study guide, a course summary | **no** | where it came from |
| `none` | no source | **no** | — always a FAIL |

That one column is the product. Everything else is bookkeeping.

## Why secondary sources are banned for numbers

A summary of a summary loses exactly what a number needs: the sample, the condition, the
standard deviation, the version of the paper. It also loses the errors. In the wild you will find
a summary that attributes a paper to the wrong first author, describes a single journal issue as
"journals", or quotes a working paper as peer-reviewed. If the number came through that pipe, you
cannot defend it and neither can your reader.

Framing is different. "Experts underestimate how much readers need context" is a claim about the
world that a good book can support. Cite it as `secondary` and the checker only warns. The moment
the same row carries `0.6 SD`, it is a FAIL.

## The four rules, in order of how often they catch something

1. **A number may only come from `own` or `primary`.** Anything else is a FAIL, no exceptions,
   no "but it is a reputable summary".
2. **Every number in the draft needs a row.** The checker extracts numbers from the draft and
   fails the ones it cannot find in the table. Numbers inside code fences and headings are ignored.
3. **`own` needs a file that exists.** A path that does not resolve is a FAIL, because it is
   usually a memory rather than a measurement.
4. **`verified` is a date you can defend.** Empty, unparseable or in the future is a FAIL.

## What it deliberately does not do

- **It does not open the DOI for you.** It checks that the source is the *right kind* and that the
  number is carried by a source you claim to have read. Verifying the number against the paper is
  your job, and it stays your job.
- **It cannot see plagiarism.** A verbatim paragraph from a book passes. Use your own sentences;
  the linter does not police copyright and this tool does not pretend to.
- **It does not know your niche.** A number that is real can still be irrelevant, stale or
  misapplied. That is judgement, and judgement does not live in a regex.

## The two bundled examples

```bash
# passes: every number points at a DOI or at a file in this repo
python3 scripts/check_claims.py --article examples/claims-demo.md \
                                --claims examples/claims-demo.claims.md

# fails: the same numbers, sourced from AI notes about a book
python3 scripts/check_claims.py --article examples/failing-secondary-source.md \
                                --claims examples/failing-secondary-source.claims.md
```

The failure example is the one worth reading. It is what a draft looks like when it came out of a
notebook of book notes: confident, clean, well-organised, and impossible to defend.

## Wiring it into the skill

In `SKILL.md` the rule is one line: **before a draft is returned, the claims table must exist and
`check_claims.py` must exit 0.** A draft without a claims table is not a draft, it is a guess with
paragraph breaks.
