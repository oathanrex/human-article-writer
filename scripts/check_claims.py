#!/usr/bin/env python3
"""check_claims.py - prove where every number in a draft came from.

check_article.py decides whether a draft *reads* like a human wrote it.
This decides whether a human *could have written it* - that is, whether every number
in the article points at a source of the right kind.

    python3 scripts/check_claims.py --article draft.md --claims draft.claims.md
    python3 scripts/check_claims.py --article draft.md --claims draft.claims.md --json

Exit codes:
    0  no FAIL rows (WARN rows allowed)
    1  at least one FAIL row
    2  bad usage, missing file, or a claims file that cannot be parsed

The claims file is a markdown table. One row per number or factual claim:

    | id | claim | value | source | type | verified |
    |----|-------|-------|--------|------|----------|
    | C1 | Editors raised writing scores | 0.6 SD | doi:10.1016/j.jebo.2023.11.011 | primary | 2026-11-26 |

`type` is the whole point:
    own           you measured it; `source` is a path in this repo that must exist
    primary       you read the paper/report yourself; `source` must be a DOI or URL
    secondary     someone summarised it for you (a blog, a newsletter, a book about a paper)
    book-summary  an AI summary of a copyrighted book, or a study guide about one
    none          no source. always a FAIL.

A number may only come from `own` or `primary`. That single rule is what stops a draft
built from a summary of a book from shipping as if the writer had read the research.
"""
import argparse
import json
import os
import re
import sys
from datetime import date

TYPES = ("own", "primary", "secondary", "book-summary")
FAIL, WARN, INFO = "FAIL", "WARN", "INFO"

# numbers we care about: measured things, not years, list indices or headings
NUM_PATTERNS = [
    (re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?"), "money"),
    (re.compile(r"\d+(?:\.\d+)?\s?%"), "percent"),
    (re.compile(r"\d+(?:\.\d+)?\s?(?:pp\b|percentage\s?points?)", re.I), "points"),
    (re.compile(r"\b\d{3,}(?:,\d{3})*\s+[A-Za-z][A-Za-z-]*"), "count"),
    (re.compile(r"\d+(?:\.\d+)?\s?-?\s?(?:SDs?|standard deviations?)\b", re.I), "sd"),
    (re.compile(r"\d+(?:\.\d+)?\s?(?:hours?|hrs?|minutes?|mins?|seconds?|secs?|ms|weeks?|days?)\b", re.I), "time"),
    (re.compile(r"\d[\d,]*\s?(?:words?|views?|clicks?|signups?|users?|people|lawyers|containers?|shots?)\b", re.I), "count"),
]
YEAR = re.compile(r"^(?:19|20)\d\d$")
DOI = re.compile(r"(?:doi:\s?|doi\.org/|https?://(?:dx\.)?doi\.org/)?10\.\d{4,9}/\S+", re.I)
URL = re.compile(r"https?://\S+", re.I)


def extract_numbers(text):
    """Return [(literal, kind, line_no)] for measured numbers outside code fences."""
    out, in_code = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.lstrip().startswith("#"):
            continue
        for pat, kind in NUM_PATTERNS:
            for m in pat.finditer(line):
                lit = m.group(0).strip()
                if YEAR.match(lit.replace("%", "").strip()):
                    continue
                out.append((lit, kind, i))
    return out


def norm_number(lit):
    """'37 %' / '37%' / '0.45 SDs' / '8.4 percentage points' -> comparable key."""
    s = lit.lower().replace(" ", "").rstrip(".")
    s = re.sub(r"percentagepoints?$", "pp", s)
    if re.search(r"sd", s):
        s = re.sub(r"(?:standarddeviations?|sds?|sd)$", "sd", s)
    return s



UNIT_KIND = [
    (re.compile(r"%"), "percent"),
    (re.compile(r"\bpp\b|percentage\s?points?", re.I), "points"),
    (re.compile(r"\bSDs?\b|standard\s?deviations?", re.I), "sd"),
    (re.compile(r"\b(?:hours?|hrs?|minutes?|mins?|seconds?|secs?|ms|weeks?|days?)\b", re.I), "time"),
    (re.compile(r"^\$"), "money"),
]


def value_key(value):
    """'8.4 pp' / '444 people' / '0.09 seconds' -> ('8.4', 'points'). None if no number."""
    m = re.search(r"\d[\d,]*(?:\.\d+)?", value)
    if not m:
        return None
    num = m.group(0).replace(",", "")
    if num.endswith(".0"):
        num = num[:-2]
    kind = "count"
    for pat, k in UNIT_KIND:
        if pat.search(value):
            kind = k
            break
    return (num, kind)


def parse_table(text):
    """Markdown table -> list of dicts. Tolerates extra pipes and empty cells."""
    rows, header = [], None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) != len(header):
            cells = (cells + [""] * len(header))[: len(header)]
        rows.append(dict(zip(header, cells)))
    return rows


def check(article_text, claims_text):
    findings = []

    def add(level, where, msg):
        findings.append({"level": level, "where": where, "message": msg})

    rows = parse_table(claims_text)
    if not rows:
        return None, [{"level": FAIL, "where": "claims", "message": "no claims table found"}]
    required = {"id", "claim", "value", "source", "type", "verified"}
    missing = required - set(rows[0].keys())
    if missing:
        return None, [{"level": FAIL, "where": "claims",
                       "message": "table is missing column(s): " + ", ".join(sorted(missing))}]

    seen_ids = {}
    article_nums = extract_numbers(article_text)
    claimed_values = {}

    for row in rows:
        rid = row.get("id", "") or "(no id)"
        ctype = (row.get("type") or "").strip().lower()
        value = (row.get("value") or "").strip()
        source = (row.get("source") or "").strip()
        verified = (row.get("verified") or "").strip()

        if not rid or rid == "(no id)":
            add(FAIL, "claims", "a row has no id")
        elif rid in seen_ids:
            add(FAIL, rid, "duplicate id")
        seen_ids[rid] = True

        if ctype not in TYPES and ctype != "none":
            add(FAIL, rid, "type %r is not one of: %s, none" % (ctype, ", ".join(TYPES)))
            continue

        if ctype == "none":
            add(FAIL, rid, "no source. A claim without a receipt does not ship")
            continue

        if ctype == "own":
            if not source:
                add(FAIL, rid, "type=own needs a path to the file that proves it")
            elif not os.path.exists(source.split()[0].strip("`'\"")):
                add(FAIL, rid, "type=own but the file does not exist: %s" % source)
        elif ctype == "primary":
            if not (DOI.search(source) or URL.search(source)):
                add(FAIL, rid, "type=primary needs a DOI or URL, got %r" % source)
        elif ctype in ("secondary", "book-summary"):
            if not source:
                add(FAIL, rid, "type=%s still needs where it came from" % ctype)
            if value and re.search(r"\d", value):
                add(FAIL, rid,
                    "%s number from a %s source. Read the primary, or delete the number"
                    % (value, ctype))
            else:
                add(WARN, rid, "secondary source - fine for framing, never for a number")

        if not verified:
            add(FAIL, rid, "verified is empty. Date the day you checked it (YYYY-MM-DD)")
        else:
            try:
                d = date.fromisoformat(verified)
                if d > date.today():
                    add(FAIL, rid, "verified date is in the future: %s" % verified)
            except ValueError:
                add(FAIL, rid, "verified must be YYYY-MM-DD, got %r" % verified)

        key = value_key(value)
        if key:
            claimed_values[key] = (rid, ctype)

    # every measured number in the draft must have a row
    covered, covered_strong = set(), set()
    for lit, kind, line in article_nums:
        key = value_key(lit)
        hit = claimed_values.get(key) if key else None
        if hit:
            rid, ctype = hit
            covered.add(rid)
            if ctype in ("own", "primary"):
                covered_strong.add(rid)
        else:
            add(FAIL, "line %d" % line,
                "number %r has no row in the claims file (%s)" % (lit, kind))

    # claims that exist but are never used by the draft are dead weight
    unused = [rid for rid, _ in claimed_values.values() if rid not in covered]
    if unused:
        add(INFO, "claims", "row(s) not used by this draft: " + ", ".join(sorted(set(unused))))

    return {"rows": len(rows), "numbers": len(article_nums),
            "covered": len(covered_strong)}, findings


def render(stats, findings, article, claims_file):
    order = {FAIL: 0, WARN: 1, INFO: 2}
    findings = sorted(findings, key=lambda f: order.get(f["level"], 3))
    print("=== Claims check: %s ===" % article)
    if stats:
        pct = (100.0 * stats["covered"] / stats["numbers"]) if stats["numbers"] else 100.0
        print("Claims: %d rows | numbers in draft: %d | with a primary/own source: %d (%.0f%%)"
              % (stats["rows"], stats["numbers"], stats["covered"], pct))
    print()
    for level in (FAIL, WARN, INFO):
        group = [f for f in findings if f["level"] == level]
        if not group:
            continue
        title = {"FAIL": "FAIL (must fix)",
                 "WARN": "WARN (look and decide)",
                 "INFO": "INFO"}[level]
        print("%s (%d)" % (title, len(group)))
        for f in group:
            print("  - %s: %s" % (f["where"], f["message"]))
        print()
    fails = sum(1 for f in findings if f["level"] == FAIL)
    if fails:
        print("%d claim(s) fail. The draft cannot ship: a reader who asks \"where did this number "
              "come from\" has no answer." % fails)
    else:
        print("every number in the draft has a receipt.")
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description="Prove where every number in a draft came from.")
    ap.add_argument("--article", required=True, help="draft markdown to check")
    ap.add_argument("--claims", required=True, help="claims table (markdown) for this draft")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--list-numbers", action="store_true", help="print the numbers found, then exit")
    args = ap.parse_args(argv)

    for path in (args.article, args.claims):
        if not os.path.exists(path):
            print("no such file: %s" % path, file=sys.stderr)
            return 2

    with open(args.article, encoding="utf-8") as f:
        article = f.read()
    with open(args.claims, encoding="utf-8") as f:
        claims = f.read()

    if args.list_numbers:
        for lit, kind, line in extract_numbers(article):
            print("line %-4d %-8s %s" % (line, kind, lit))
        return 0

    stats, findings = check(article, claims)
    if stats is None:
        for f in findings:
            print("%s: %s" % (f["where"], f["message"]), file=sys.stderr)
        return 2

    fails = render(stats, findings, args.article, args.claims)
    if args.json:
        print(json.dumps({"stats": stats, "findings": findings, "fails": fails}, indent=2))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
